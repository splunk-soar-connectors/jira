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

    from ..consts import (
        JIRA_ERROR_CONNECTIVITY_TEST,
        JIRA_ERROR_SERVER_INFO,
        JIRA_SUCCESS_CONNECTIVITY_TEST,
        JIRA_USING_BASE_URL,
    )
    from ..helpers import get_auth, jira_request

    logger = getLogger()

    logger.info(JIRA_USING_BASE_URL.format(base_url=asset.device_url.rstrip("/")))

    # Raises AssetMisconfiguration early if credentials are not configured
    get_auth(asset)

    logger.info("Connecting to Jira instance")

    # GET /rest/api/2/myself — lightest authenticated endpoint; confirms URL + token
    try:
        myself = jira_request(asset, "GET", "rest/api/2/myself")
    except ActionFailure as exc:
        raise ActionFailure(
            f"{JIRA_ERROR_CONNECTIVITY_TEST}: {JIRA_ERROR_SERVER_INFO}: {exc.message}"
        ) from exc

    display_name = myself.get("displayName") or myself.get("name") or "unknown user"
    soar.set_message(
        f"{JIRA_SUCCESS_CONNECTIVITY_TEST} (authenticated as: {display_name})"
    )
