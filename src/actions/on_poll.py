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

from dateutil.parser import parse as _parse_dt
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
    JIRA_TIME_FORMAT,
)
from ..helpers import get_auth
from .on_poll_helpers import (
    _build_attachment_artifact,
    _build_comment_artifact,
    _build_fields_artifact,
    _build_jql,
    _fetch_all_comments,
    _get_artifact_cef_map,
    _get_existing_artifact_sdis,
    _get_global_custom_field_map,
    _paginate_issues,
    _resolve_timezone,
)

logger = getLogger()


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

    # --- Load cursor ---
    # `first_run` defaults True so a missing key = treat as first run.
    # `last_time` is UTC epoch int; 0 means "no previous run".
    first_run: bool = state.get("first_run", True)
    last_time: int = int(state.get("last_time") or 0)

    # Ensure non-negative (guard against corrupted state)
    if last_time < 0:
        last_time = 0

    is_manual = params.is_manual_poll()

    # --- Resolve ticket limit ---
    if is_manual:
        # Poll Now: SOAR passes the user-supplied count; fall back to 100
        limit = int(
            params.container_count or DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT
        )
    elif first_run:
        limit = int(asset.first_run_max_tickets or 1000)
    else:
        limit = int(asset.max_tickets or DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT)

    # --- Resolve Jira server timezone ---
    # Used only to convert the UTC cursor epoch → Jira-local string for the JQL filter.
    # On first run or Poll Now there is no time filter, so the API call is skipped.
    jira_tz: ZoneInfo | None = None
    if not is_manual and not first_run and last_time > 0:
        jira_tz = _resolve_timezone(asset)

    # --- Build JQL time filter string ---
    # Legacy connector subtracts 60 s from last_time to handle Jira's minute-level
    # granularity — without this, tickets updated in the same minute as the cursor
    # are silently skipped.
    last_time_str: str | None = None
    if jira_tz is not None and last_time > 0:
        adjusted = max(
            0, last_time - 60
        )  # -60 s overlap to avoid minute-boundary misses
        dt_utc = datetime.fromtimestamp(adjusted, tz=UTC)
        dt_jira = dt_utc.astimezone(jira_tz)
        last_time_str = dt_jira.strftime(JIRA_TIME_FORMAT)
        logger.info(
            f"Querying Jira for issues updated >= {last_time_str} ({jira_tz.key})"
        )

    # --- Build JQL ---
    jql = _build_jql(
        asset, last_time_str, is_first_run=first_run, is_manual_poll=is_manual
    )
    logger.info(f"JQL: {jql}")

    # --- Parse custom_fields config ---
    # asset.custom_fields is a JSON-formatted list: '["Sprint", "Epic Link"]'
    custom_fields_list: list[str] = []
    if asset.custom_fields:
        try:
            parsed = _json.loads(asset.custom_fields)
            if isinstance(parsed, list) and parsed:
                custom_fields_list = [str(f) for f in parsed]
        except Exception as exc:
            logger.warning(f"Could not parse custom_fields config: {exc}")

    # --- Fetch global custom field map (one call for the entire poll run) ---
    # `GET rest/api/2/field` returns all field definitions instance-wide.
    # This replaces the legacy per-issue editmeta call and our earlier per-project cache.
    cf_map = _get_global_custom_field_map(asset) if custom_fields_list else {}

    # --- Paginate: full issues returned directly, no per-issue re-fetch needed ---
    try:
        issues = _paginate_issues(asset, jql, limit)
    except ActionFailure as exc:
        raise ActionFailure(f"Failed to fetch issues from Jira: {exc}") from exc

    logger.info(f"Total issues fetched: {len(issues)}")

    if not issues:
        # Nothing to ingest — still flip first_run and write state on scheduled runs
        if not is_manual:
            state["first_run"] = False
        return

    last_updated_utc: int = last_time  # will be updated as we process issues

    failed = 0

    for issue in issues:
        issue_key: str = issue.get("key") or issue.get("id", "")
        if not issue_key:
            continue

        fields = issue.get("fields") or {}
        issue_updated_str: str = fields.get("updated", "")

        # Convert issue's `updated` to UTC epoch for cursor tracking
        try:
            issue_updated_utc = int(_parse_dt(issue_updated_str).timestamp())
        except Exception:
            issue_updated_utc = last_updated_utc

        # --- Check if container already exists in SOAR ---
        # SDK provides soar.get() for direct SOAR REST access.
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
            # ----------------------------------------------------------------
            # NEW container path
            # ----------------------------------------------------------------
            # Yield a Container — the SDK decorator calls save_container and
            # assigns container_id; all subsequent Artifacts (until the next
            # Container yield) are attached to it.

            # SDK sets the label from ingest config automatically when container_label is omitted.
            yield Container(
                name=issue_key,
                description=fields.get("summary") or "",
                source_data_identifier=issue_key,
                data=issue,  # full raw Jira JSON stored on the container
            )

            # Attachment artifacts (new container — no dedup needed)
            for attachment in fields.get("attachment") or []:
                try:
                    art = _build_attachment_artifact(attachment)
                    # Download into vault
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
                                container_id=0,  # SDK fills real ID after Container save
                                file_content=dl.content,
                                file_name=attachment.get("filename", "attachment"),
                            )
                            art.cef = {**(art.cef or {}), "vault_id": vault_id}
                    yield art
                except Exception as exc:
                    logger.warning(
                        f"Failed to ingest attachment for {issue_key}: {exc}"
                    )

            # Comment artifacts (new container — no dedup needed)
            # _fetch_all_comments handles the case where search/jql truncated the list
            for comment in _fetch_all_comments(
                asset, issue_key, fields.get("comment") or {}
            ):
                try:
                    yield _build_comment_artifact(comment)
                except Exception as exc:
                    logger.warning(
                        f"Failed to build comment artifact for {issue_key}: {exc}"
                    )

            # Primary ticket-fields artifact
            try:
                yield _build_fields_artifact(issue, cf_map, custom_fields_list)
            except Exception as exc:
                logger.warning(
                    f"Failed to build fields artifact for {issue_key}: {exc}"
                )
                failed += 1

        else:
            # ----------------------------------------------------------------
            # UPDATE path — container already exists
            # ----------------------------------------------------------------
            # Update the container's raw data and description via SOAR REST.
            soar.post(
                f"rest/container/{container_id}",
                json={"data": issue, "description": fields.get("summary") or ""},
            )

            # Batch-load existing artifact SDIs for this container (one REST call)
            existing_sdis = _get_existing_artifact_sdis(soar, container_id)
            existing_cef_map = _get_artifact_cef_map(soar, container_id)

            artifact_batch: list[Artifact] = []

            # Attachments — skip if already ingested (Jira attachment IDs are stable)
            for attachment in fields.get("attachment") or []:
                attachment_sdi = str(attachment.get("id", ""))
                if attachment_sdi in existing_sdis:
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

            # Comments — deduplicate; create new artifact only if new or edited
            # _fetch_all_comments handles truncation from search/jql *all response
            for comment in _fetch_all_comments(
                asset, issue_key, fields.get("comment") or {}
            ):
                comment_sdi = str(comment.get("id", ""))
                existing_cef = existing_cef_map.get(comment_sdi)

                if existing_cef is None:
                    # New comment — always create
                    pass
                else:
                    if is_manual:
                        # Poll Now always re-creates to show current state (legacy behaviour)
                        pass
                    else:
                        # Scheduled: only create if comment was edited since last ingest
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

            # Ticket-fields artifact (always update — same SDI = issue key overwrites previous)
            try:
                fields_art = _build_fields_artifact(issue, cf_map, custom_fields_list)
                fields_art.container_id = container_id
                artifact_batch.append(fields_art)
            except Exception as exc:
                logger.warning(
                    f"Failed to build fields artifact for {issue_key}: {exc}"
                )
                failed += 1

            # Yield accumulated artifacts for this container
            for art in artifact_batch:
                yield art

        # Track the most recent `updated` timestamp seen across all issues
        if issue_updated_utc > last_updated_utc:
            last_updated_utc = issue_updated_utc

    # --- Persist state (scheduled runs only) ---
    if not is_manual:
        if issues and last_updated_utc > 0:
            # Store as UTC epoch int — unambiguous, no time.mktime(local timetuple) drift
            state["last_time"] = last_updated_utc
        state["first_run"] = False

    if failed:
        raise ActionFailure(JIRA_ERROR_FAILED)
