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
from soar_sdk.abstract import SOARClient

from .._asset import Asset


def run_test_connectivity(soar: SOARClient, asset: Asset) -> None:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..auth import resolve_jira_base_url
    from ..client import call_jira
    from ..consts import (
        JIRA_ERROR_CONNECTIVITY_TEST,
        JIRA_ERROR_SERVER_INFO,
        JIRA_SUCCESS_CONNECTIVITY_TEST,
        JIRA_USING_BASE_URL,
    )
    from ..helpers import get_auth

    logger = getLogger()

    # Raises AssetMisconfiguration early if credentials are not configured
    get_auth(asset)

    base_url = resolve_jira_base_url(asset)
    logger.info(JIRA_USING_BASE_URL.format(base_url=base_url))

    # Use call_jira directly (not jira_request) so we can inspect the raw response —
    # status, redirect chain and body — which is what diagnoses a 302 (SSO/login
    # interception) vs a real 401/403 auth failure.
    try:
        response = call_jira("GET", "rest/api/2/myself", asset)
    except ActionFailure as exc:
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: {JIRA_ERROR_SERVER_INFO}: {exc.message}",
        ) from exc

    body_snippet = (response.text or "")[:500]

    # --- Interpret ---
    if response.history:
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: request was redirected "
            f"({response.history[0].status_code}) to {response.url} — the Jira REST API "
            "is likely behind SSO/a reverse proxy that intercepts Basic-auth/API-token "
            "requests. Basic auth with an API token cannot pass an SSO login page.",
        )

    if not response.is_success:
        error_msg = (
            response.text[:300] if response.text else f"HTTP {response.status_code}"
        )
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: {JIRA_ERROR_SERVER_INFO}: "
            f"HTTP {response.status_code}: {error_msg}",
        )

    content_type = response.headers.get("content-type", "")
    if "json" not in content_type:
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: expected JSON but got {content_type!r} "
            f"(body starts: {body_snippet!r}) — the endpoint returned a non-API page, "
            "which usually means an SSO/login redirect or a wrong base URL.",
        )

    try:
        myself = response.json()
    except Exception as exc:
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: failed to parse response as JSON: {exc}; "
            f"body starts: {body_snippet!r}",
        ) from exc

    display_name = myself.get("displayName") or myself.get("name") or "unknown user"
    soar.set_message(
        f"{JIRA_SUCCESS_CONNECTIVITY_TEST} (authenticated as: {display_name})",
    )
