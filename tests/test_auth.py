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
import base64

import httpx

from src import auth
from src._asset import Asset


def _authorization_header(httpx_auth: httpx.Auth) -> str:
    request = httpx.Request("GET", "https://api.atlassian.com/ex/jira/cloud-id")
    authenticated_request = next(httpx_auth.auth_flow(request))
    return authenticated_request.headers["Authorization"]


def test_service_account_api_token_uses_basic_auth_and_cloud_gateway():
    asset = Asset(
        device_url="https://example.atlassian.net",
        username="automation@serviceaccount.atlassian.com",
        password="scoped-api-token",  # pragma: allowlist secret
    )

    expected_token = base64.b64encode(
        b"automation@serviceaccount.atlassian.com:scoped-api-token"
    ).decode()

    assert auth.requires_cloud_gateway(asset)
    assert (
        _authorization_header(auth.resolve_jira_auth(asset))
        == f"Basic {expected_token}"
    )


def test_oauth_client_credentials_take_priority_over_service_account_api_token(
    monkeypatch,
):
    asset = Asset(
        device_url="https://example.atlassian.net",
        username="automation@serviceaccount.atlassian.com",
        password="scoped-api-token",  # pragma: allowlist secret
        client_id="client-id",
        client_secret="client-secret",  # pragma: allowlist secret
    )
    oauth_auth = object()
    monkeypatch.setattr(auth, "_resolve_oauth_auth", lambda _: oauth_auth)

    assert auth.resolve_jira_auth(asset) is oauth_auth
