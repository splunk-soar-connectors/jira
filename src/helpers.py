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
from .client import JiraClient, validate_issue_id
from .consts import (
    JIRA_DEFAULT_TIMEOUT,
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


def get_custom_field_map(asset: Asset, issue_id: str | None = None) -> dict[str, str]:
    """Map custom IDs to names using issue edit metadata, or global fields for polling.

    Failure preserves raw IDs, matching the legacy fallback. Existing-issue
    actions must pass issue_id so global same-name fields cannot select a
    field from another issue context.
    """
    try:
        if issue_id is not None:
            metadata = jira_request(
                asset, "GET", f"rest/api/2/issue/{validate_issue_id(issue_id)}/editmeta"
            )
            fields = metadata.get("fields") or {}
            return {
                field_id: field["name"]
                for field_id, field in fields.items()
                if "customfield" in field_id and field.get("name")
            }
        all_fields = jira_request(asset, "GET", "rest/api/2/field")
        return {
            f["id"]: f["name"]
            for f in all_fields
            if str(f.get("id", "")).startswith("customfield") and f.get("name")
        }
    except ActionFailure as exc:
        logger.warning(f"Could not fetch custom field definitions: {exc}")
        return {}


def get_custom_field_name_to_id_map(asset: Asset, issue_id: str) -> dict[str, str]:
    """Return ``{"Human Name": customfield_XXXXX}`` — the inverse of the read map.

    Resolve only the fields editable on this issue. If metadata is unavailable,
    preserve explicit field IDs. Reject ambiguous names rather than selecting
    whichever field happened to occur last.
    """
    inverse: dict[str, str] = {}
    for field_id, name in get_custom_field_map(asset, issue_id).items():
        if name in inverse:
            raise ActionFailure(
                f"Multiple editable custom fields are named '{name}'; use customfield IDs instead"
            )
        inverse[name] = field_id
    return inverse


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

    Delegates the actual transport and response parsing to :class:`JiraClient` and returns the
    parsed JSON body. Raises ActionFailure on HTTP errors or network failures.
    """
    return JiraClient(asset).request_json(
        method,
        endpoint,
        params=params,
        json=json,
        data=data,
        files=files,
        headers=headers,
        timeout=timeout,
    )


def apply_issue_updates(client: JiraClient, issue_id: str, payload: dict) -> None:
    """Apply wrappers then simple fields, retaining the legacy request order."""
    for wrapper in ("fields", "update"):
        if wrapper in payload and not isinstance(payload[wrapper], dict):
            raise ActionFailure(f"'{wrapper}' must be a JSON formatted dictionary")
    if "fields" in payload:
        client.update_issue(issue_id, fields=payload["fields"])
    if "update" in payload:
        client.update_issue(issue_id, update=payload["update"])
    remaining = {
        key: value for key, value in payload.items() if key not in ("fields", "update")
    }
    if remaining:
        client.update_issue(issue_id, fields=remaining)


def upload_vault_attachment(
    client: JiraClient, issue_id: str, soar, vault_id: str
) -> None:
    """Select the current container association and retry Unicode names on failure."""
    attachments = soar.vault.get_attachment(vault_id=vault_id)
    if not attachments:
        raise ActionFailure("File not found in vault")
    container_id = soar.get_executing_container_id()
    meta = next(
        (item for item in attachments if item.container_id == container_id),
        attachments[0],
    )
    try:
        with open(meta.path, "rb") as handle:
            client.add_attachment(issue_id, handle, meta.name)
    except Exception:
        ascii_name = (
            meta.name.encode("ascii", "ignore")
            .decode("ascii")
            .replace("\r", " ")
            .replace("\n", " ")
        )
        if len(ascii_name) >= len(meta.name):
            raise
        with open(meta.path, "rb") as handle:
            client.add_attachment(issue_id, handle, f"FILENAME_ASCII_{ascii_name}")
