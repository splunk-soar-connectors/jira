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
"""Single HTTP client function for the Jira app.

All actions route Jira REST calls through :func:`call_jira`. Never construct
``httpx.Client`` inside an action handler directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .auth import resolve_jira_auth, resolve_jira_base_url
from .consts import JIRA_DEFAULT_TIMEOUT, JIRA_USING_BASE_URL

if TYPE_CHECKING:
    from ._asset import Asset

logger = getLogger()


def call_jira(
    method: str,
    endpoint: str,
    asset: Asset,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    data: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = JIRA_DEFAULT_TIMEOUT,
) -> httpx.Response:
    """Make an authenticated HTTP request against the Jira REST API.

    Prepends ``asset.device_url`` to ``endpoint``, applies auth, and returns
    the raw ``httpx.Response`` — callers decide how to interpret the body.
    Raises ``ActionFailure`` if credentials are unconfigured or the network
    request itself fails; does not raise on non-2xx status codes.
    """
    base_url = resolve_jira_base_url(asset)
    url = f"{base_url}/{endpoint.lstrip('/')}"
    logger.info(JIRA_USING_BASE_URL.format(base_url=base_url))

    auth = resolve_jira_auth(asset)  # raises ActionFailure if unconfigured
    verify = bool(asset.verify_server_cert)

    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    # File uploads must not have Content-Type set (httpx sets multipart boundary automatically)
    if files:
        request_headers.pop("Content-Type", None)

    try:
        with httpx.Client(verify=verify, follow_redirects=True) as client:
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
