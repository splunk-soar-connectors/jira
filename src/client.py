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
"""Centralized Jira REST client."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .auth import resolve_jira_auth, resolve_jira_base_url
from .consts import (
    JIRA_DEFAULT_TIMEOUT,
    JIRA_RESPONSE_ERROR_MESSAGES_KEY,
    JIRA_RESPONSE_ERRORS_KEY,
    JIRA_USING_BASE_URL,
)

if TYPE_CHECKING:
    from ._asset import Asset

logger = getLogger()


def validate_issue_id(value: str) -> str:
    """Apply the issue-key/positive-ID policy used by the legacy connector."""
    if not re.fullmatch(
        r"(?:[A-Z][A-Z0-9_]*-[1-9][0-9]*|[1-9][0-9]*)",
        str(value),
        flags=re.ASCII | re.IGNORECASE,
    ):
        raise ActionFailure("Please provide a valid Jira issue key or numeric issue ID")
    return str(value)


def _same_origin(first_url: str, second_url: str) -> bool:
    """Return whether two absolute URLs have the same scheme, host, and port."""
    try:
        first = urlsplit(first_url)
        second = urlsplit(second_url)
        first_port = first.port or (443 if first.scheme.lower() == "https" else 80)
        second_port = second.port or (443 if second.scheme.lower() == "https" else 80)
    except ValueError:
        return False
    return (
        first.scheme.lower(),
        (first.hostname or "").lower(),
        first_port,
    ) == (
        second.scheme.lower(),
        (second.hostname or "").lower(),
        second_port,
    )


def _relative_endpoint(endpoint: str) -> str:
    """Reject absolute request destinations before Jira authentication is applied."""
    parsed = urlsplit(endpoint)
    if parsed.scheme or parsed.netloc:
        raise ActionFailure(
            "Invalid Jira endpoint. Provide only the path after the configured Jira URL."
        )
    return endpoint


def _parse_jira_error(response: httpx.Response) -> str:
    """Extract a human-readable error string from a Jira response."""
    content_type = response.headers.get("content-type", "")

    if "json" in content_type:
        try:
            body = response.json()
            parts: list[str] = []
            error_messages: list[Any] = body.get(JIRA_RESPONSE_ERROR_MESSAGES_KEY) or []
            parts.extend(str(message) for message in error_messages if message)
            errors: dict[str, Any] = body.get(JIRA_RESPONSE_ERRORS_KEY) or {}
            parts.extend(f"{key}: {value}" for key, value in errors.items())
            if parts:
                return "; ".join(parts)
        except Exception:  # noqa: S110
            pass

    if "xml" in content_type or (response.text or "").lstrip().startswith("<"):
        text = re.sub(r"<[^>]+>", " ", response.text or "").split()
        readable = " ".join(token for token in text if not token.isdigit())
        if readable:
            return readable

    return response.text or f"HTTP {response.status_code}"


class JiraClient:
    """Centralize Jira REST transport for all connector actions."""

    def __init__(self, asset: Asset):
        self.asset = asset

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = JIRA_DEFAULT_TIMEOUT,
        verify_ssl: bool | None = None,
        follow_redirects: bool = False,
    ) -> httpx.Response:
        return _call_jira(
            method,
            endpoint,
            self.asset,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
            timeout=timeout,
            verify_ssl=verify_ssl,
            follow_redirects=follow_redirects,
        )

    def request_json(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        response = self.request(method, endpoint, **kwargs)
        if not response.is_success:
            error_msg = _parse_jira_error(response)
            raise ActionFailure(f"Jira API error {response.status_code}: {error_msg}")

        if not response.content:
            return {}

        try:
            return response.json()
        except Exception as exc:
            raise ActionFailure(
                f"Failed to parse Jira response as JSON: {exc}"
            ) from exc

    def _attachment_endpoint(self, url: str, attachment_id: str | None) -> str:
        if attachment_id is not None:
            if not re.fullmatch(r"[1-9][0-9]*", str(attachment_id), flags=re.ASCII):
                raise ActionFailure("Invalid Jira attachment ID")
            return f"rest/api/2/attachment/content/{attachment_id}?redirect=false"
        base_url = resolve_jira_base_url(self.asset)
        parsed_url = urlsplit(url)
        if parsed_url.scheme or parsed_url.netloc:
            if not _same_origin(url, base_url):
                raise ActionFailure(
                    "Refusing to download an attachment from outside the configured Jira origin"
                )
            base_path = urlsplit(base_url).path.rstrip("/")
            path = parsed_url.path
            if base_path and path.startswith(base_path + "/"):
                path = path[len(base_path) :]
            return urlunsplit(("", "", path, parsed_url.query, ""))
        return _relative_endpoint(url)

    def download(
        self, url: str, *, attachment_id: str | None = None, timeout: float = 60.0
    ) -> bytes:
        """Download attachment content; polling uses download_to_file to bound memory."""
        buffer = BytesIO()
        self._download_into(url, buffer, attachment_id=attachment_id, timeout=timeout)
        return buffer.getvalue()

    def download_to_file(
        self,
        url: str,
        destination: str,
        *,
        attachment_id: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        """Stream attachment content to disk in 512 KiB chunks."""
        with Path(destination).open("wb") as handle:
            self._download_into(
                url, handle, attachment_id=attachment_id, timeout=timeout
            )

    def _download_into(
        self, url: str, handle: BinaryIO, *, attachment_id: str | None, timeout: float
    ) -> None:
        endpoint = self._attachment_endpoint(url, attachment_id)
        base_url = resolve_jira_base_url(self.asset)
        destination = f"{base_url}/{endpoint.lstrip('/')}"
        original = destination
        auth = resolve_jira_auth(self.asset)
        try:
            with httpx.Client(
                verify=bool(self.asset.verify_server_cert), follow_redirects=False
            ) as client:
                for _ in range(10):
                    with client.stream(
                        "GET",
                        destination,
                        auth=auth,
                        headers={"Accept": "*/*"},
                        timeout=timeout,
                    ) as response:
                        if response.is_redirect:
                            location = response.headers.get("location")
                            if not location:
                                raise ActionFailure(
                                    "Attachment redirect has no destination"
                                )
                            destination = urljoin(str(response.url), location)
                            parsed = urlsplit(destination)
                            if (
                                parsed.username
                                or parsed.password
                                or (
                                    parsed.scheme != "https"
                                    and not _same_origin(destination, original)
                                )
                            ):
                                raise ActionFailure(
                                    "Refusing an unsafe attachment redirect"
                                )
                            if not _same_origin(destination, original):
                                # Signed media URLs must never receive Jira credentials.
                                auth = None
                            continue
                        if not response.is_success:
                            raise ActionFailure(
                                f"Failed to download attachment: HTTP {response.status_code}"
                            )
                        for chunk in response.iter_bytes(chunk_size=512 * 1024):
                            handle.write(chunk)
                        return
                raise ActionFailure("Too many attachment redirects")
        except httpx.RequestError as exc:
            raise ActionFailure(f"Failed to download attachment: {exc}") from exc

    def issue(
        self,
        issue_id: str,
        *,
        fields: str | None = None,
        expand: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        if expand:
            params["expand"] = expand
        return self.request_json(
            "GET", f"rest/api/2/issue/{validate_issue_id(issue_id)}", params=params
        )

    def projects(self) -> list[dict[str, Any]]:
        return self.request_json("GET", "rest/api/2/project")

    def search_issues(
        self,
        jql: str,
        *,
        max_results: int = 100,
        fields: str = "*all",
        next_page_token: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
            "fields": fields,
        }
        if next_page_token:
            params["nextPageToken"] = next_page_token
        return self.request_json("GET", "rest/api/2/search/jql", params=params)

    def search_users(
        self,
        *,
        username: str | None = None,
        display_name: str | None = None,
        start_at: int = 0,
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        query = display_name or username or ""
        return self.request_json(
            "GET",
            "rest/api/2/user/search",
            params={
                "query": query,
                "includeActive": "true",
                "includeInactive": "false",
                "maxResults": max_results,
                "startAt": start_at,
            },
        )

    def watchers(self, issue_id: str) -> dict[str, Any]:
        return self.request_json(
            "GET", f"rest/api/2/issue/{validate_issue_id(issue_id)}/watchers"
        )

    def add_watcher(
        self, issue_id: str, identifier: str, *, account_id: bool = False
    ) -> None:
        self.request_json(
            "POST",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/watchers",
            json=identifier,
        )

    def remove_watcher(
        self, issue_id: str, identifier: str, *, account_id: bool = False
    ) -> None:
        params = {"accountId": identifier} if account_id else {"username": identifier}
        self.request_json(
            "DELETE",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/watchers",
            params=params,
        )

    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]:
        return self.request_json("POST", "rest/api/2/issue", json={"fields": fields})

    def update_issue(
        self,
        issue_id: str,
        *,
        fields: dict[str, Any] | None = None,
        update: dict[str, Any] | None = None,
    ) -> None:
        body: dict[str, Any] = {}
        if fields is not None:
            body["fields"] = fields
        if update is not None:
            body["update"] = update
        self.request_json(
            "PUT", f"rest/api/2/issue/{validate_issue_id(issue_id)}", json=body
        )

    def delete_issue(self, issue_id: str) -> None:
        self.request_json("DELETE", f"rest/api/2/issue/{validate_issue_id(issue_id)}")

    def add_comment(
        self, issue_id: str, comment: str, *, internal: bool = False
    ) -> None:
        body: dict[str, Any] = {"body": comment}
        if internal:
            body["properties"] = [
                {"key": "sd.public.comment", "value": {"internal": True}}
            ]
        self.request_json(
            "POST", f"rest/api/2/issue/{validate_issue_id(issue_id)}/comment", json=body
        )

    def add_attachment(
        self, issue_id: str, file_handle: BinaryIO, filename: str
    ) -> None:
        self.request_json(
            "POST",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/attachments",
            files={"file": (filename, file_handle, "application/octet-stream")},
            headers={"X-Atlassian-Token": "no-check"},
        )

    def issue_link_types(self) -> list[dict[str, Any]]:
        response = self.request_json("GET", "rest/api/2/issueLinkType")
        return response.get("issueLinkTypes", [])

    def create_issue_link(
        self,
        link_type: str,
        from_id: str,
        to_id: str,
        comment: dict[str, Any] | None = None,
    ) -> None:
        validate_issue_id(from_id)
        validate_issue_id(to_id)
        payload: dict[str, Any] = {
            "type": {"name": link_type},
            "inwardIssue": {"key": from_id},
            "outwardIssue": {"key": to_id},
        }
        if comment:
            payload["comment"] = comment
        self.request_json("POST", "rest/api/2/issueLink", json=payload)

    def assign_issue(
        self, issue_id: str, identifier: str, *, account_id: bool = False
    ) -> None:
        key = "accountId" if account_id else "name"
        self.request_json(
            "PUT",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/assignee",
            json={key: identifier},
        )

    def transitions(self, issue_id: str) -> list[dict[str, Any]]:
        return self.request_json(
            "GET", f"rest/api/2/issue/{validate_issue_id(issue_id)}/transitions"
        ).get("transitions", [])

    def resolutions(self) -> list[dict[str, Any]]:
        response = self.request_json("GET", "rest/api/2/resolution")
        return response if isinstance(response, list) else []

    def add_worklog(self, issue_id: str, time_spent: str) -> None:
        self.request_json(
            "POST",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/worklog",
            json={"timeSpent": time_spent},
        )

    def transition_issue(
        self, issue_id: str, transition_id: str, *, fields: dict[str, Any] | None = None
    ) -> None:
        body: dict[str, Any] = {"transition": {"id": transition_id}}
        if fields:
            body["fields"] = fields
        self.request_json(
            "POST",
            f"rest/api/2/issue/{validate_issue_id(issue_id)}/transitions",
            json=body,
        )


def _call_jira(
    method: str,
    endpoint: str,
    asset: Asset,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    data: Any | None = None,
    files: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = JIRA_DEFAULT_TIMEOUT,
    verify_ssl: bool | None = None,
    follow_redirects: bool = False,
) -> httpx.Response:
    """Make an authenticated HTTP request against the Jira REST API.

    Prepends ``asset.device_url`` to ``endpoint``, applies auth, and returns
    the raw ``httpx.Response`` — callers decide how to interpret the body.
    Raises ``ActionFailure`` if credentials are unconfigured or the network
    request itself fails; does not raise on non-2xx status codes.
    """
    endpoint = _relative_endpoint(endpoint)
    base_url = resolve_jira_base_url(asset)
    url = f"{base_url}/{endpoint.lstrip('/')}"
    logger.info(JIRA_USING_BASE_URL.format(base_url=base_url))

    auth = resolve_jira_auth(asset)  # raises ActionFailure if unconfigured
    verify = bool(asset.verify_server_cert) if verify_ssl is None else verify_ssl

    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    # File uploads must not have Content-Type set (httpx sets multipart boundary automatically)
    if files:
        request_headers.pop("Content-Type", None)

    try:
        with httpx.Client(verify=verify, follow_redirects=follow_redirects) as client:
            return client.request(
                method=method.upper(),
                url=url,
                auth=auth,
                headers=request_headers,
                params=params,
                json=json,
                data=data,
                files=files,
                timeout=timeout,
            )
    except httpx.RequestError as exc:
        raise ActionFailure(f"Request to Jira failed: {exc}") from exc


def call_jira(
    method: str,
    endpoint: str,
    asset: Asset,
    **kwargs: Any,
) -> httpx.Response:
    """Backward-compatible functional wrapper around :class:`JiraClient`."""
    return JiraClient(asset).request(method, endpoint, **kwargs)
