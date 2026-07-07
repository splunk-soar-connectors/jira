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

Jira authenticates with HTTP Basic Auth: the username (Jira Cloud email or
on-prem username) plus the password (Jira Cloud API token or on-prem password).
Auth resolution lives here rather than being scattered across actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from soar_sdk.auth.httpx_auth import BasicAuth
from soar_sdk.exceptions import ActionFailure

from .consts import JIRA_CONFIG_PARAMS_REQUIRED

if TYPE_CHECKING:
    from ._asset import Asset


def resolve_jira_auth(asset: Asset) -> httpx.Auth:
    """Return the httpx auth for Jira, or raise if credentials are missing.

    Emits ``Authorization: Basic <base64(username:password)>`` via the SDK's
    ``BasicAuth``. Raises ``ActionFailure`` (not a bare exception) when either
    credential is absent, so SOAR shows a clean error instead of a traceback.
    """
    if asset.username and asset.password:
        return BasicAuth(asset.username, asset.password)
    raise ActionFailure(JIRA_CONFIG_PARAMS_REQUIRED)
