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
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .auth import resolve_jira_auth
from .client import call_jira
from .consts import (
    JIRA_DEFAULT_TIMEOUT,
    JIRA_RESPONSE_ERROR_MESSAGES_KEY,
    JIRA_RESPONSE_ERRORS_KEY,
)

if TYPE_CHECKING:
    from ._asset import Asset

logger = getLogger()


def get_auth(asset: Asset) -> httpx.Auth:
    """Return the Jira httpx auth. Delegates to :func:`resolve_jira_auth`.

    Kept as a thin alias so existing call sites keep working; new code should
    call ``resolve_jira_auth`` from ``src.auth`` directly.
    """
    return resolve_jira_auth(asset)


def _parse_jira_error(response: httpx.Response) -> str:
    """Extract a human-readable error string from a Jira error response body."""
    content_type = response.headers.get("content-type", "")

    if "json" in content_type:
        try:
            body = response.json()
            parts: list[str] = []
            error_messages: list[Any] = body.get(JIRA_RESPONSE_ERROR_MESSAGES_KEY) or []
            parts.extend(str(m) for m in error_messages if m)
            errors: dict[str, Any] = body.get(JIRA_RESPONSE_ERRORS_KEY) or {}
            parts.extend(f"{k}: {v}" for k, v in errors.items())
            if parts:
                return "; ".join(parts)
        except Exception:  # noqa: S110
            pass

    if "xml" in content_type or (response.text or "").lstrip().startswith("<"):
        # Strip XML tags to extract the readable message
        import re

        text = re.sub(r"<[^>]+>", " ", response.text or "").split()
        # Drop numeric status code tokens, rejoin
        readable = " ".join(t for t in text if not t.isdigit())
        if readable:
            return readable

    return response.text or f"HTTP {response.status_code}"


def description_to_str(value: Any) -> str | None:
    """Convert a Jira description field to a plain string.

    Jira Cloud returns ADF (Atlassian Document Format) dicts for description
    fields instead of plain strings. This extracts all text nodes from an ADF
    doc, or returns the value as-is if it's already a string (or None).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts: list[str] = []
        _collect_adf_text(value, parts)
        return " ".join(parts) if parts else None
    return str(value)


def get_custom_field_map(asset: Asset) -> dict[str, str]:
    """Return ``{customfield_XXXXX: "Human Name"}`` for every custom field in the instance.

    One ``GET rest/api/2/field`` call resolves the opaque ``customfield_*`` IDs
    to their display names. Falls back to an empty dict on failure so callers
    degrade gracefully (fields keep their raw IDs) rather than aborting.
    """
    try:
        all_fields = jira_request(asset, "GET", "rest/api/2/field")
        return {
            f["id"]: f["name"]
            for f in all_fields
            if str(f.get("id", "")).startswith("customfield") and f.get("name")
        }
    except ActionFailure as exc:
        logger.warning(f"Could not fetch custom field definitions: {exc}")
        return {}


def get_custom_field_name_to_id_map(asset: Asset) -> dict[str, str]:
    """Return ``{"Human Name": customfield_XXXXX}`` — the inverse of the read map.

    Used on the write path to let clients reference custom fields by display
    name (legacy parity — see ``_replace_custom_name_with_id``). Falls back to
    an empty dict on failure so name→id translation is skipped, not fatal.
    """
    return {name: field_id for field_id, name in get_custom_field_map(asset).items()}


def apply_custom_field_names_to_ids(
    payload: dict, name_to_id: dict[str, str] | None = None
) -> dict:
    """Rename custom-field display names to ``customfield_XXXXX`` ids in a write payload.

    Mirrors legacy ``_get_update_fields``: translates the keys inside the
    ``fields`` and ``update`` sub-dicts, plus any remaining top-level keys
    (which callers wrap into ``fields`` themselves). Returns ``payload``
    unchanged when there is nothing to translate.
    """
    n2i = name_to_id or {}
    if not n2i:
        return payload
    result: dict = {}
    for key, value in payload.items():
        if key in ("fields", "update") and isinstance(value, dict):
            result[key] = {n2i.get(k, k): v for k, v in value.items()}
        else:
            # A remaining top-level key may itself be a custom-field display name.
            result[n2i.get(key, key)] = value
    return result


def sanitize_fields_dict(
    fields: dict, custom_field_map: dict[str, str] | None = None
) -> dict:
    """Return a copy of a Jira ``fields`` dict, normalized for output.

    - Renames ``customfield_XXXXX`` keys to their human names using
      ``custom_field_map`` (legacy parity — see ``_replace_custom_id_with_name``).
    - Coerces the ADF ``description`` field to ``str | None``.
    """
    cfm = custom_field_map or {}
    result = {cfm.get(key, key): value for key, value in fields.items()}
    if "description" in result:
        result["description"] = description_to_str(result["description"])
    return result


def _collect_adf_text(node: dict, parts: list[str]) -> None:
    if node.get("type") == "text":
        text = node.get("text", "")
        if text:
            parts.append(text)
    for child in node.get("content") or []:
        _collect_adf_text(child, parts)


def jira_request(
    asset: Asset,
    method: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    data: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = JIRA_DEFAULT_TIMEOUT,
) -> Any:
    """Make an authenticated request to the Jira REST API.

    Delegates the actual transport to :func:`call_jira` and returns the
    parsed JSON body. Raises ActionFailure on HTTP errors or network failures.
    """
    response = call_jira(
        method,
        endpoint,
        asset,
        params=params,
        json=json,
        data=data,
        files=files,
        headers=headers,
        timeout=timeout,
    )

    if not response.is_success:
        error_msg = _parse_jira_error(response)
        raise ActionFailure(f"Jira API error {response.status_code}: {error_msg}")

    if not response.content:
        return {}

    try:
        return response.json()
    except Exception as exc:
        raise ActionFailure(f"Failed to parse Jira response as JSON: {exc}") from exc
