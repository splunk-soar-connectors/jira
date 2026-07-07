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
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dateutil.parser import parse as _parse_dt
import httpx as _httpx

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.models.artifact import Artifact
from soar_sdk.models.container import Container
from soar_sdk.params import OnPollParams

from soar_sdk.logging import getLogger

from ._app_ref import app
from ._asset import Asset
from .consts import (
    DEFAULT_MAX_RESULTS_PER_PAGE,
    DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT,
    JIRA_ERROR_FAILED,
    JIRA_TIME_FORMAT,
)
from .helpers import get_auth, jira_request

logger = getLogger()


from . import actions as _actions  # noqa: F401

__all__ = ["Asset", "app"]


# ---------------------------------------------------------------------------
# on_poll helpers
# ---------------------------------------------------------------------------


def _resolve_timezone(asset: Asset) -> ZoneInfo:
    """Return the Jira server timezone.

    If asset.timezone is explicitly set by the operator, use it.
    Otherwise call GET rest/api/2/serverInfo to auto-detect `serverTimeZone`.
    Falls back to UTC if the API call fails or returns an unknown zone name.
    """
    if asset.timezone is not None:
        # Operator override — trust it and skip the API call entirely.
        logger.info(f"Using configured timezone: {asset.timezone.key}")
        return asset.timezone

    # Auto-detect from Jira server
    try:
        info = jira_request(asset, "GET", "rest/api/2/serverInfo")
        tz_name: str = info.get("serverTimeZone") or "UTC"
        tz = ZoneInfo(tz_name)
        logger.info(f"Auto-detected Jira server timezone: {tz_name}")
        return tz
    except (ActionFailure, ZoneInfoNotFoundError, KeyError) as exc:
        logger.warning(f"Could not detect server timezone ({exc}), falling back to UTC")
        return ZoneInfo("UTC")


def _build_jql(
    asset: Asset, last_time_str: str | None, is_first_run: bool, is_manual_poll: bool
) -> str:
    """Construct the JQL query string.

    - `project=KEY` if project_key is set on the asset
    - `and {query}` if a custom JQL snippet is set
    - `and updated>="YYYY/MM/DD HH:MM"` on ongoing scheduled polls only
    - Always ends with `order by updated asc` for deterministic cursor behaviour
    """
    parts: list[str] = []

    if asset.project_key:
        parts.append(f"project={asset.project_key}")

    if asset.query:
        parts.append(asset.query)

    # Jira Cloud rejects bare `order by updated asc` with no filter.
    # Inject a no-op filter when no project/query/time filter is present.
    if not is_manual_poll and not is_first_run and last_time_str:
        parts.append(f'updated>="{last_time_str}"')
    elif not parts:
        parts.append("issueKey IS NOT EMPTY")

    base = " and ".join(parts)
    return f"{base} order by updated asc"


def _paginate_issues(asset: Asset, jql: str, limit: int) -> list[dict]:
    """Fetch full issues via cursor-based pagination against `search/jql`.

    Requests all fields (`*all`) so each page already contains the complete issue
    data — no per-issue re-fetch is required after this call.
    Uses nextPageToken / isLast pagination (Jira Cloud current API).
    """
    issues: list[dict] = []
    next_page_token: str | None = None

    while True:
        params: dict = {
            "jql": jql,
            "maxResults": DEFAULT_MAX_RESULTS_PER_PAGE,
            "fields": ["*all"],
        }
        if next_page_token:
            params["nextPageToken"] = next_page_token

        result = jira_request(asset, "GET", "rest/api/2/search/jql", params=params)

        page = result.get("issues", [])
        if not page:
            break

        remaining = limit - len(issues)
        issues.extend(page[:remaining])

        if len(issues) >= limit:
            break
        if result.get("isLast", False):
            break

        next_page_token = result.get("nextPageToken")
        if not next_page_token:
            break

    return issues


def _get_global_custom_field_map(asset: Asset) -> dict[str, str]:
    """Return {customfield_XXXXX: "Human Name"} for all custom fields in the Jira instance.

    Calls `GET rest/api/2/field` once per poll run regardless of how many issues
    or projects are being ingested. Falls back to an empty dict on failure so
    custom field resolution is silently skipped rather than aborting the poll.
    """
    try:
        all_fields = jira_request(asset, "GET", "rest/api/2/field")
        return {
            f["id"]: f["name"]
            for f in all_fields
            if str(f.get("id", "")).startswith("customfield") and f.get("name")
        }
    except ActionFailure as exc:
        logger.warning(f"Could not fetch global custom field definitions: {exc}")
        return {}


def _fetch_all_comments(asset: Asset, issue_key: str, comment_data: dict) -> list[dict]:
    """Return the complete comment list for an issue.

    `search/jql` with `*all` returns only the first page of comments
    (typically 10). When `comment.total > len(comment.comments)` we fetch
    the remaining pages from `GET rest/api/2/issue/{key}/comment` so behaviour
    matches the legacy connector's per-issue fetch which always returned all comments.
    """
    comments = list(comment_data.get("comments") or [])
    total = comment_data.get("total", len(comments))

    if total <= len(comments):
        return comments

    # Need more — paginate the comment endpoint
    start_at = len(comments)
    while start_at < total:
        try:
            page = jira_request(
                asset,
                "GET",
                f"rest/api/2/issue/{issue_key}/comment",
                params={
                    "startAt": start_at,
                    "maxResults": DEFAULT_MAX_RESULTS_PER_PAGE,
                },
            )
        except ActionFailure as exc:
            logger.warning(
                f"Failed to fetch remaining comments for {issue_key} at startAt={start_at}: {exc}"
            )
            break
        batch = page.get("comments") or []
        if not batch:
            break
        comments.extend(batch)
        start_at += len(batch)

    return comments


def _get_existing_artifact_sdis(soar: SOARClient, container_id: int) -> set[str]:
    """Return the set of source_data_identifiers for all artifacts in a container.

    Used for deduplication: one SOAR REST call per container instead of one per artifact.
    """
    response = soar.get(
        "rest/artifact",
        params={
            "_filter_container_id": container_id,
            "page_size": 0,  # 0 = return all
            "fields": "source_data_identifier,cef",
        },
    )
    if not response.is_success:
        return set()
    data = response.json()
    return {
        str(a.get("source_data_identifier", ""))
        for a in data.get("data", [])
        if a.get("source_data_identifier")
    }


def _get_artifact_cef_map(soar: SOARClient, container_id: int) -> dict[str, dict]:
    """Return {source_data_identifier: cef_dict} for all artifacts in a container.

    Used to check comment edit timestamps without N individual REST calls.
    """
    response = soar.get(
        "rest/artifact",
        params={
            "_filter_container_id": container_id,
            "page_size": 0,
            "sort": "id",
            "order": "desc",  # most recent first so first match wins on duplicate SDIs
            "fields": "source_data_identifier,cef",
        },
    )
    if not response.is_success:
        return {}
    cef_map: dict[str, dict] = {}
    for a in response.json().get("data", []):
        sdi = str(a.get("source_data_identifier", ""))
        if sdi and sdi not in cef_map:  # keep the most recently created version
            cef_map[sdi] = a.get("cef") or {}
    return cef_map


def _build_attachment_artifact(attachment: dict) -> Artifact:
    """Build an Artifact from a raw Jira attachment dict (from issue.fields.attachment)."""
    author_info = attachment.get("author") or {}
    author_account_id = author_info.get("accountId")
    # Jira Cloud authors carry an accountId (and use displayName); Jira on-prem
    # authors carry `name` and never an accountId. This mirrors the legacy
    # connector's try/except branch that set is_on_prem based on author.name.
    is_on_prem = not author_account_id
    author = (
        author_info.get("name") if is_on_prem else author_info.get("displayName")
    ) or ""

    return Artifact(
        name=f"attachment - {attachment.get('filename', '')}",
        label="attachment",
        source_data_identifier=str(attachment.get("id", "")),
        cef={
            "size": attachment.get("size"),
            "created": attachment.get("created"),
            "filename": attachment.get("filename"),
            "mimeType": attachment.get("mimeType"),
            "author": author,
            "author_account_id": author_account_id,
            "is_on_prem": is_on_prem,
            "vault_id": None,  # populated below when vault upload succeeds
        },
    )


def _build_comment_artifact(comment: dict) -> Artifact:
    """Build an Artifact from a raw Jira comment dict."""
    author_info = comment.get("author") or {}
    update_author_info = comment.get("updateAuthor") or {}

    author_account_id = author_info.get("accountId")
    update_author_account_id = update_author_info.get("accountId")
    # Jira Cloud authors carry an accountId (and use displayName); Jira on-prem
    # authors carry `name` and never an accountId. Legacy keyed is_on_prem off
    # author.name, so absence of accountId is the equivalent signal.
    is_on_prem = not author_account_id
    author = (
        author_info.get("name") if is_on_prem else author_info.get("displayName")
    ) or ""
    update_author = (
        update_author_info.get("name")
        if is_on_prem
        else update_author_info.get("displayName")
    ) or ""

    updated = comment.get("updated", "")

    return Artifact(
        name=f"comment_{updated} by {author}",
        label="comment",
        source_data_identifier=str(comment.get("id", "")),
        cef={
            "body": comment.get("body"),
            "created": comment.get("created"),
            "updated": updated,
            "is_on_prem": is_on_prem,
            "author": author,
            "author_account_id": author_account_id,
            "updateAuthor": update_author,
            "updateAuthor_account_id": update_author_account_id,
        },
    )


def _build_fields_artifact(
    issue: dict, custom_field_map: dict[str, str], custom_fields_list: list[str]
) -> Artifact:
    """Build the primary ticket-fields Artifact for a Jira issue.

    `custom_field_map` is {customfield_XXXXX: "Human Name"} — built once per project per poll run.
    `custom_fields_list` is the operator-configured list of human names to include in CEF.
    """
    fields = issue.get("fields") or {}
    issue_key = issue.get("key", "")

    def _name(obj: dict | None) -> str | None:
        if not isinstance(obj, dict):
            return None
        return obj.get("name") or obj.get("displayName")

    label = _name(fields.get("issuetype")) or "issue"
    updated = fields.get("updated", "")

    cef: dict = {}
    cef["updated_at"] = updated
    cef["priority"] = _name(fields.get("priority"))
    cef["resolution"] = _name(fields.get("resolution")) or "Unresolved"
    cef["status"] = _name(fields.get("status"))
    cef["reporter"] = _name(fields.get("reporter"))
    cef["project_key"] = (fields.get("project") or {}).get("key")
    cef["summary"] = fields.get("summary")
    cef["description"] = fields.get("description")
    cef["issue_type"] = _name(fields.get("issuetype"))

    # Custom fields: remap customfield_XXXXX → human name, then pick requested ones
    if custom_fields_list and custom_field_map:
        renamed: dict = {}
        for raw_key, value in fields.items():
            human_name = custom_field_map.get(raw_key, raw_key)
            renamed[human_name] = value
        for cf_name in custom_fields_list:
            if cf_name in renamed:
                cef[cf_name] = renamed[cf_name]

    # Strip None values — keeps artifacts clean
    cef = {k: v for k, v in cef.items() if v is not None}

    return Artifact(
        name=f"ticket fields_{updated}",
        label=label,
        source_data_identifier=issue_key,
        cef=cef,
    )


@app.on_poll()
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


if __name__ == "__main__":
    app.cli()
