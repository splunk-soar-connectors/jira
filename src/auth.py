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


"""SDK-native auth resolution for the Jira app.

Jira normally authenticates with HTTP Basic Auth: the username (Jira Cloud
email or on-prem username) plus the password (Jira Cloud API token or
on-prem password). Atlassian service accounts (username ending in
``@serviceaccount.atlassian.com``) issue scoped tokens that reject Basic Auth
entirely — per Atlassian's docs, these authenticate as a Bearer token against
the ``api.atlassian.com`` gateway (``/ex/jira/{cloud_id}/...``) instead of the
site's own domain.

Atlassian service accounts can alternatively authenticate via OAuth 2.0
client credentials (``client_id``/``client_secret``), which is the preferred
flow when configured — see
https://support.atlassian.com/user-management/docs/create-oauth-2-0-credential-for-service-accounts/.
When ``client_id``/``client_secret`` are set, OAuth takes priority over
``username``/``password`` and neither is required.

Auth resolution lives here rather than being scattered across actions; base
URL resolution (plain site vs. gateway) lives alongside it since the two are
coupled for service accounts and OAuth.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from soar_sdk.auth import ClientCredentialsFlow, OAuthClientError
from soar_sdk.auth.httpx_auth import BasicAuth, StaticTokenAuth
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger

from .consts import (
    JIRA_CLOUD_GATEWAY_URL_TEMPLATE,
    JIRA_CONFIG_PARAMS_REQUIRED,
    JIRA_ERROR_CLOUD_ID_LOOKUP_FAILED,
    JIRA_ERROR_OAUTH_TOKEN_FETCH_FAILED,
    JIRA_OAUTH_TOKEN_ENDPOINT,
    JIRA_SERVICE_ACCOUNT_USERNAME_SUFFIX,
    JIRA_TENANT_INFO_ENDPOINT,
)


if TYPE_CHECKING:
    from ._asset import Asset

logger = getLogger()

_CLOUD_ID_STATE_KEY = "jira_cloud_id"


def is_oauth_configured(asset: Asset) -> bool:
    """Whether OAuth 2.0 client credentials are configured for this asset."""
    return bool(asset.client_id and asset.client_secret)


def is_service_account(asset: Asset) -> bool:
    """Whether the configured username is an Atlassian service account."""
    username = asset.username or ""
    result = username.lower().endswith(JIRA_SERVICE_ACCOUNT_USERNAME_SUFFIX)
    logger.info(
        f"[auth] is_service_account check: username={username!r} suffix="
        f"{JIRA_SERVICE_ACCOUNT_USERNAME_SUFFIX!r} -> {result}"
    )
    return result


def requires_cloud_gateway(asset: Asset) -> bool:
    """Whether Jira REST calls must go through the api.atlassian.com gateway."""
    return is_oauth_configured(asset) or is_service_account(asset)


def _resolve_oauth_auth(asset: Asset) -> httpx.Auth:
    """Fetch (or reuse a cached) OAuth access token via the client credentials grant."""
    assert asset.client_id and asset.client_secret  # noqa: S101 — caller checks is_oauth_configured
    flow = ClientCredentialsFlow(
        asset.auth_state,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        token_endpoint=JIRA_OAUTH_TOKEN_ENDPOINT,
    )
    try:
        token = flow.get_token()
    except OAuthClientError as exc:
        logger.info(f"[auth] resolve_jira_auth: OAuth token fetch failed: {exc}")
        raise ActionFailure(
            JIRA_ERROR_OAUTH_TOKEN_FETCH_FAILED.format(error=str(exc))
        ) from exc
    logger.info("[auth] resolve_jira_auth: using OAuth client credentials (Bearer)")
    return StaticTokenAuth(token)


def resolve_jira_auth(asset: Asset) -> httpx.Auth:
    """Return the httpx auth for Jira, or raise if credentials are missing.

    OAuth client credentials (``client_id``/``client_secret``) take priority
    when configured. Otherwise, service accounts (see
    :func:`is_service_account`) authenticate with ``password`` sent as a
    Bearer token, since Atlassian's scoped service-account tokens reject
    Basic Auth. Everyone else uses standard Basic Auth (``Authorization:
    Basic <base64(username:password)>``). Raises ``ActionFailure`` (not a
    bare exception) when no credentials are configured, so SOAR shows a
    clean error instead of a traceback.
    """
    if is_oauth_configured(asset):
        return _resolve_oauth_auth(asset)
    if not (asset.username and asset.password):
        logger.info("[auth] resolve_jira_auth: no credentials configured")
        raise ActionFailure(JIRA_CONFIG_PARAMS_REQUIRED)
    if is_service_account(asset):
        logger.info("[auth] resolve_jira_auth: using StaticTokenAuth (Bearer)")
        return StaticTokenAuth(asset.password)
    logger.info("[auth] resolve_jira_auth: using BasicAuth")
    return BasicAuth(asset.username, asset.password)


def resolve_jira_base_url(asset: Asset) -> str:
    """Return the base URL to send Jira REST requests to.

    Service accounts and OAuth clients can't call the site's own domain
    directly — their tokens are only valid against the ``api.atlassian.com``
    cloud gateway, which is addressed by cloud ID rather than site domain.
    The cloud ID is resolved once (via the unauthenticated
    ``_edge/tenant_info`` endpoint on the site domain) and cached in
    ``asset.auth_state`` to avoid an extra request on every action call.
    Everyone else uses ``device_url`` unchanged.
    """
    site_url = asset.device_url.rstrip("/")
    if not requires_cloud_gateway(asset):
        logger.info(
            f"[auth] resolve_jira_base_url: not a service account or OAuth client, using {site_url}"
        )
        return site_url

    cached = asset.auth_state.get(_CLOUD_ID_STATE_KEY)
    if cached:
        gateway_url = JIRA_CLOUD_GATEWAY_URL_TEMPLATE.format(cloud_id=cached)
        logger.info(
            f"[auth] resolve_jira_base_url: cached cloud_id={cached!r}, using {gateway_url}"
        )
        return gateway_url

    tenant_info_url = f"{site_url}/{JIRA_TENANT_INFO_ENDPOINT}"
    logger.info(
        f"[auth] resolve_jira_base_url: resolving cloud_id via {tenant_info_url}"
    )
    try:
        response = httpx.get(
            tenant_info_url,
            verify=bool(asset.verify_server_cert),
            timeout=30.0,
        )
        response.raise_for_status()
        cloud_id = response.json()["cloudId"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.info(f"[auth] resolve_jira_base_url: cloud_id lookup failed: {exc}")
        raise ActionFailure(
            JIRA_ERROR_CLOUD_ID_LOOKUP_FAILED.format(error=str(exc))
        ) from exc

    asset.auth_state[_CLOUD_ID_STATE_KEY] = cloud_id
    gateway_url = JIRA_CLOUD_GATEWAY_URL_TEMPLATE.format(cloud_id=cloud_id)
    logger.info(
        f"[auth] resolve_jira_base_url: resolved cloud_id={cloud_id!r}, using {gateway_url}"
    )
    return gateway_url
