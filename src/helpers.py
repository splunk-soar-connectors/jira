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

from soar_sdk.auth.httpx_auth import BasicAuth
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .consts import (
    JIRA_DEFAULT_TIMEOUT,
    JIRA_RESPONSE_ERROR_MESSAGES_KEY,
    JIRA_RESPONSE_ERRORS_KEY,
    JIRA_USING_BASE_URL,
)

if TYPE_CHECKING:
    from ._asset import Asset

logger = getLogger()


def get_auth(asset: Asset) -> httpx.Auth:
    """Return BasicAuth using the asset's username and password (API token)."""
    return BasicAuth(asset.username, asset.password)


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


def sanitize_fields_dict(fields: dict) -> dict:
    """Return a shallow copy of a Jira fields dict with description coerced to str | None."""
    if "description" not in fields:
        return fields
    result = dict(fields)
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

    Prepends asset.device_url to endpoint, applies auth, and returns the
    parsed JSON body. Raises ActionFailure on HTTP errors or network failures.
    """
    base_url = asset.device_url.rstrip("/")
    full_url = f"{base_url}/{endpoint.lstrip('/')}"
    logger.info(JIRA_USING_BASE_URL.format(base_url=base_url))

    auth = get_auth(asset)
    verify: bool = bool(asset.verify_server_cert)

    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    # File uploads must not have Content-Type set (httpx sets multipart boundary automatically)
    if files:
        request_headers.pop("Content-Type", None)

    with httpx.Client(verify=verify, follow_redirects=True) as client:
        try:
            response = client.request(
                method=method.upper(),
                url=full_url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=request_headers,
                auth=auth,
                timeout=timeout,
            )
        except httpx.RequestError as exc:
            raise ActionFailure(f"Request to Jira failed: {exc}") from exc

    if not response.is_success:
        error_msg = _parse_jira_error(response)
        raise ActionFailure(f"Jira API error {response.status_code}: {error_msg}")

    if not response.content:
        return {}

    try:
        return response.json()
    except Exception as exc:
        raise ActionFailure(f"Failed to parse Jira response as JSON: {exc}") from exc
