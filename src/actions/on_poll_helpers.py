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
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from soar_sdk.abstract import SOARClient
from soar_sdk.exceptions import ActionFailure
from soar_sdk.models.artifact import Artifact
from soar_sdk.logging import getLogger

from .._asset import Asset
from ..consts import DEFAULT_MAX_RESULTS_PER_PAGE
from ..helpers import get_custom_field_map, jira_request

logger = getLogger()


def _migrate_legacy_ingest_state(asset: Asset) -> None:
    """Seed SDK ingest state from the pre-SDK connector's flat checkpoint keys.

    The legacy BaseConnector app stored `first_run` and `last_time` as top-level
    keys in the asset state file. The SDK keeps ingestion checkpoints in a
    separate encrypted partition of that same file, so upgrading in place would
    otherwise find that partition empty and re-ingest everything from scratch.
    `last_time` is a UTC epoch int on both sides (legacy's host-tz round-trip via
    time.mktime cancels itself out), so it's copied as-is with no conversion.
    Guarded by needs_* so this only ever fills a gap, never overwrites a
    checkpoint the SDK partition already has.
    """
    state = asset.ingest_state
    needs_first_run = "first_run" not in state
    needs_last_time = "last_time" not in state
    if not (needs_first_run or needs_last_time):
        return

    legacy_state = state.backend.load_state() or {}

    if needs_first_run and "first_run" in legacy_state:
        state["first_run"] = legacy_state["first_run"]

    if needs_last_time and (legacy_last_time := legacy_state.get("last_time")):
        state["last_time"] = legacy_last_time


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

    Thin alias over :func:`src.helpers.get_custom_field_map`; kept so the poll
    call site reads naturally. Resolves IDs once per poll run and falls back to
    an empty dict on failure (custom field resolution is skipped, not fatal).
    """
    return get_custom_field_map(asset)


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


def _get_existing_artifact(
    soar: SOARClient, container_id: int, sdi: str
) -> dict | None:
    """Return the most recent artifact matching this source_data_identifier, or None.

    Mirrors legacy's per-item ``_get_artifact_id`` lookup: one bounded, targeted
    REST call per artifact rather than one unbounded bulk fetch per container.
    Individually isolated (try/except) so a single slow/failed lookup only
    risks a duplicate artifact, not an aborted poll run.
    """
    try:
        response = soar.get(
            "rest/artifact",
            params={
                "_filter_source_data_identifier": f'"{sdi}"',
                "_filter_container_id": container_id,
                "sort": "id",
                "order": "desc",
                "page_size": 1,
                "fields": "source_data_identifier,cef",
            },
        )
    except Exception as exc:
        logger.warning(f"Artifact lookup failed for sdi={sdi!r}: {exc}")
        return None
    if not response.is_success:
        return None
    data = response.json().get("data", [])
    return data[0] if data else None


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
