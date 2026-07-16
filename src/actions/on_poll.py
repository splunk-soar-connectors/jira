# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json as _json
from collections.abc import Iterator
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import httpx as _httpx

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.models.artifact import Artifact
from soar_sdk.models.container import Container
from soar_sdk.params import OnPollParams
from soar_sdk.logging import getLogger

from .._asset import Asset
from ..consts import (
    DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT,
    JIRA_ERROR_FAILED,
    JIRA_LIMIT_VALIDATION_MESSAGE,
    JIRA_TIME_FORMAT,
)
from ..helpers import get_auth
from .on_poll_helpers import (
    _build_attachment_artifact,
    _build_comment_artifact,
    _build_fields_artifact,
    _build_jql,
    _fetch_all_comments,
    _get_existing_artifact,
    _get_global_custom_field_map,
    _migrate_legacy_ingest_state,
    _paginate_issues,
    _resolve_timezone,
)

logger = getLogger()


def _parse_dt(value: str) -> datetime:
    """Parse a Jira ISO-8601 timestamp (e.g. ``2023-01-15T10:30:45.123+0000``).

    Jira emits offsets without a colon (``+0000``); Python 3.11+
    ``datetime.fromisoformat`` handles that plus fractional seconds, so no
    third-party dependency is required.
    """
    return datetime.fromisoformat(value)


def on_poll(
    params: OnPollParams, soar: SOARClient, asset: Asset
) -> Iterator[Container | Artifact]:
    """Ingest Jira tickets as SOAR containers with field, comment, and attachment artifacts.

    State is stored in `asset.ingest_state` (SDK-managed, encrypted at rest):
      - `first_run` (bool): True until the first scheduled poll completes.
      - `last_time` (int): UTC epoch seconds of the `updated` field of the last ingested issue.

    Three execution modes (mirrors legacy connector):
      - Poll Now  (params.is_manual_poll()): uses params.container_count as limit; never writes state.
      - First Run (state["first_run"] == True): uses asset.first_run_max_tickets; no time filter.
      - Scheduled (ongoing): uses asset.max_tickets; adds `updated>="..."` JQL filter.
    """
    state = asset.ingest_state
    _migrate_legacy_ingest_state(asset)

    # `first_run` defaults True so a missing key = treat as first run.
    # `last_time` is UTC epoch int; 0 means "no previous run".
    first_run: bool = state.get("first_run", True)
    last_time: int = int(state.get("last_time") or 0)

    if last_time < 0:
        last_time = 0

    is_manual = params.is_manual_poll()

    if is_manual:
        # Poll Now: SOAR passes the user-supplied count; fall back to 100
        limit = int(
            params.container_count or DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT
        )
        limit_param_name = "container_count"
    elif first_run:
        limit = int(asset.first_run_max_tickets or 1000)
        limit_param_name = "first_run_max_tickets"
    else:
        limit = int(asset.max_tickets or DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT)
        limit_param_name = "max_tickets"

    if limit <= 0:
        raise ActionFailure(
            JIRA_LIMIT_VALIDATION_MESSAGE.format(parameter=limit_param_name)
        )

    # Only needed to convert the UTC cursor epoch → Jira-local string for the
    # JQL filter; skipped entirely on first run / Poll Now (no time filter).
    jira_tz: ZoneInfo | None = None
    if not is_manual and not first_run and last_time > 0:
        jira_tz = _resolve_timezone(asset)

    # -60s overlap: Jira's `updated` filter has minute-level granularity, so
    # without this, tickets updated in the same minute as the cursor are skipped.
    last_time_str: str | None = None
    if jira_tz is not None and last_time > 0:
        adjusted = max(0, last_time - 60)
        dt_utc = datetime.fromtimestamp(adjusted, tz=UTC)
        dt_jira = dt_utc.astimezone(jira_tz)
        last_time_str = dt_jira.strftime(JIRA_TIME_FORMAT)
        logger.info(
            f"Querying Jira for issues updated >= {last_time_str} ({jira_tz.key})"
        )

    jql = _build_jql(
        asset, last_time_str, is_first_run=first_run, is_manual_poll=is_manual
    )
    logger.info(f"JQL: {jql}")

    # asset.custom_fields is a JSON-formatted list: '["Sprint", "Epic Link"]'
    custom_fields_list: list[str] = []
    if asset.custom_fields:
        try:
            parsed = _json.loads(asset.custom_fields)
            if isinstance(parsed, list) and parsed:
                custom_fields_list = [str(f) for f in parsed]
        except Exception as exc:
            logger.warning(f"Could not parse custom_fields config: {exc}")

    cf_map = _get_global_custom_field_map(asset) if custom_fields_list else {}

    try:
        issues = _paginate_issues(asset, jql, limit)
    except ActionFailure as exc:
        raise ActionFailure(f"Failed to fetch issues from Jira: {exc}") from exc

    logger.info(f"Total issues fetched: {len(issues)}")

    if not issues:
        if not is_manual:
            state["first_run"] = False
        return

    last_updated_utc: int = last_time

    failed = 0

    for issue in issues:
        issue_key: str = issue.get("key") or issue.get("id", "")
        if not issue_key:
            continue

        fields = issue.get("fields") or {}
        issue_updated_str: str = fields.get("updated", "")

        try:
            issue_updated_utc = int(_parse_dt(issue_updated_str).timestamp())
        except Exception:
            issue_updated_utc = last_updated_utc

        asset_id = soar.get_asset_id()
        existing_response = soar.get(
            "rest/container",
            params={
                "_filter_source_data_identifier": f'"{issue_key}"',
                "_filter_asset": asset_id,
            },
        )
        existing_containers = []
        if existing_response.is_success:
            existing_containers = existing_response.json().get("data", [])

        container_id: int | None = (
            existing_containers[0]["id"] if existing_containers else None
        )

        if container_id is None:
            # Keep a handle to the yielded Container: the decorator calls
            # save_container() and backfills `.container_id` on this same object
            # once the generator is resumed, so we can read the real ID back below.
            new_container = Container(
                name=issue_key,
                description=fields.get("summary") or "",
                source_data_identifier=issue_key,
                data=issue,
            )
            yield new_container
            container_id = (
                int(new_container.container_id)
                if new_container.container_id is not None
                else None
            )

            if container_id is None:
                logger.warning(
                    f"Failed to create container for {issue_key}; skipping its artifacts"
                )
                if issue_updated_utc > last_updated_utc:
                    last_updated_utc = issue_updated_utc
                continue

            for attachment in fields.get("attachment") or []:
                try:
                    art = _build_attachment_artifact(attachment)
                    art.container_id = container_id
                    content_url = attachment.get("content", "")
                    if content_url:
                        with _httpx.Client(
                            verify=bool(asset.verify_server_cert), follow_redirects=True
                        ) as hclient:
                            dl = hclient.get(
                                content_url, auth=get_auth(asset), timeout=120.0
                            )
                        if dl.is_success:
                            vault_id = soar.vault.create_attachment(
                                container_id=container_id,
                                file_content=dl.content,
                                file_name=attachment.get("filename", "attachment"),
                            )
                            art.cef = {**(art.cef or {}), "vault_id": vault_id}
                    yield art
                except Exception as exc:
                    logger.warning(
                        f"Failed to ingest attachment for {issue_key}: {exc}"
                    )

            # _fetch_all_comments handles the case where search/jql truncated the list
            for comment in _fetch_all_comments(
                asset, issue_key, fields.get("comment") or {}
            ):
                try:
                    art = _build_comment_artifact(comment)
                    art.container_id = container_id
                    yield art
                except Exception as exc:
                    logger.warning(
                        f"Failed to build comment artifact for {issue_key}: {exc}"
                    )

            try:
                fields_art = _build_fields_artifact(issue, cf_map, custom_fields_list)
                fields_art.container_id = container_id
                yield fields_art
            except Exception as exc:
                logger.warning(
                    f"Failed to build fields artifact for {issue_key}: {exc}"
                )
                failed += 1

        else:
            soar.post(
                f"rest/container/{container_id}",
                json={"data": issue, "description": fields.get("summary") or ""},
            )

            artifact_batch: list[Artifact] = []

            # Attachments — skip if already ingested (Jira attachment IDs are stable)
            for attachment in fields.get("attachment") or []:
                attachment_sdi = str(attachment.get("id", ""))
                if _get_existing_artifact(soar, container_id, attachment_sdi):
                    continue
                try:
                    art = _build_attachment_artifact(attachment)
                    art.container_id = container_id
                    content_url = attachment.get("content", "")
                    if content_url:
                        with _httpx.Client(
                            verify=bool(asset.verify_server_cert), follow_redirects=True
                        ) as hclient:
                            dl = hclient.get(
                                content_url, auth=get_auth(asset), timeout=120.0
                            )
                        if dl.is_success:
                            vault_id = soar.vault.create_attachment(
                                container_id=container_id,
                                file_content=dl.content,
                                file_name=attachment.get("filename", "attachment"),
                            )
                            art.cef = {**(art.cef or {}), "vault_id": vault_id}
                    artifact_batch.append(art)
                except Exception as exc:
                    logger.warning(
                        f"Failed to ingest attachment for {issue_key}: {exc}"
                    )

            # _fetch_all_comments handles truncation from search/jql *all response
            for comment in _fetch_all_comments(
                asset, issue_key, fields.get("comment") or {}
            ):
                comment_sdi = str(comment.get("id", ""))
                existing_artifact = _get_existing_artifact(
                    soar, container_id, comment_sdi
                )
                existing_cef = (existing_artifact or {}).get("cef") or {}

                if existing_artifact is not None:
                    if is_manual:
                        # Poll Now always re-creates to show current state (legacy behaviour)
                        pass
                    else:
                        # Compare UTC timestamps to avoid timezone representation drift
                        try:
                            current_utc = int(
                                _parse_dt(comment.get("updated", "")).timestamp()
                            )
                            stored_utc = int(
                                _parse_dt(existing_cef.get("updated", "")).timestamp()
                            )
                            if current_utc == stored_utc:
                                continue  # unchanged — skip
                        except Exception as _cmp_exc:
                            logger.debug(
                                f"Comment timestamp comparison failed, will re-create artifact: {_cmp_exc}"
                            )

                try:
                    art = _build_comment_artifact(comment)
                    art.container_id = container_id
                    artifact_batch.append(art)
                except Exception as exc:
                    logger.warning(
                        f"Failed to build comment artifact for {issue_key}: {exc}"
                    )

            # Same SDI (issue key) overwrites the previous fields artifact
            try:
                fields_art = _build_fields_artifact(issue, cf_map, custom_fields_list)
                fields_art.container_id = container_id
                artifact_batch.append(fields_art)
            except Exception as exc:
                logger.warning(
                    f"Failed to build fields artifact for {issue_key}: {exc}"
                )
                failed += 1

            for art in artifact_batch:
                yield art

        if issue_updated_utc > last_updated_utc:
            last_updated_utc = issue_updated_utc

    if not is_manual:
        if issues and last_updated_utc > 0:
            # Store as UTC epoch int — unambiguous, no time.mktime(local timetuple) drift
            state["last_time"] = last_updated_utc
        state["first_run"] = False

    if failed:
        raise ActionFailure(JIRA_ERROR_FAILED)
