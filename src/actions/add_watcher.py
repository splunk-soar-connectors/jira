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
from soar_sdk.action_results import ActionOutput
from soar_sdk.params import Param, Params

from .._asset import Asset


class AddWatcherParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])
    username: str | None = Param(
        description="Username of the user to add to the watchers list (required for Jira on-prem)",
        primary=True,
        cef_types=["user name"],
    )
    user_account_id: str | None = Param(
        description="Account ID of the user to add to the watchers list (required for Jira cloud)",
        primary=True,
        cef_types=["jira user account id"],
    )


def add_watcher(
    params: AddWatcherParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import JIRA_WATCHERS_ERROR
    from ..helpers import jira_request

    logger = getLogger()

    # Validate: exactly one of username or user_account_id must be set
    if bool(params.username) == bool(params.user_account_id):
        raise ActionFailure(JIRA_WATCHERS_ERROR)

    # Cloud-only: user_account_id is required
    if params.username and not params.user_account_id:
        raise ActionFailure(
            "user_account_id is required for Jira Cloud. Use 'lookup users' to find the account ID."
        )

    # Fetch current watchers
    watchers_response = jira_request(
        asset, "GET", f"rest/api/2/issue/{params.id}/watchers"
    )
    existing_account_ids = {
        w.get("accountId") for w in watchers_response.get("watchers", [])
    }

    if params.user_account_id in existing_account_ids:
        logger.info("user already in watchers list")
        soar.set_message(
            f"User is already in the watchers list of the issue ID: {params.id}"
        )
        return ActionOutput()

    # POST the accountId as a JSON string body (what Jira Cloud expects)
    jira_request(
        asset,
        "POST",
        f"rest/api/2/issue/{params.id}/watchers",
        json=params.user_account_id,
    )

    soar.set_message(
        f"Successfully added user to the watchers list of the issue ID: {params.id}"
    )
    return ActionOutput()
