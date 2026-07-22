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
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from .._asset import Asset
from ..consts import JIRA_WATCHERS_ERROR
from ..helpers import jira_request


class RemoveWatcherParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])
    username: str | None = Param(
        description="Username of the user to remove from watchers list (required for Jira on-prem)",
        primary=True,
        cef_types=["user name"],
    )
    user_account_id: str | None = Param(
        description="Account ID of the user to remove from the watchers list (required for Jira cloud)",
        primary=True,
        cef_types=["jira user account id"],
    )


def remove_watcher(
    params: RemoveWatcherParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    logger = getLogger()

    # Validate: exactly one of username or user_account_id must be set
    if bool(params.username) == bool(params.user_account_id):
        raise ActionFailure(JIRA_WATCHERS_ERROR)

    # username -> on-prem (matched by "name"); user_account_id -> cloud (matched by "accountId")
    user = params.username or params.user_account_id

    watchers_response = jira_request(
        asset, "GET", f"rest/api/2/issue/{params.id}/watchers"
    )
    existing_watchers = watchers_response.get("watchers", [])

    if not existing_watchers:
        raise ActionFailure(f"No watchers found in the issue ID: {params.id}")

    # Jira Cloud watcher entries have no "name" key, and pre-accountId on-prem
    # instances have no "accountId" key — a KeyError here means the caller
    # passed the wrong identifier type for this deployment (legacy behaviour).
    identifier_key = "name" if params.username else "accountId"
    try:
        existing_identifiers = {w[identifier_key] for w in existing_watchers}
    except KeyError as exc:
        raise ActionFailure(JIRA_WATCHERS_ERROR) from exc

    if user not in existing_identifiers:
        logger.info("user not in watchers list")
        soar.set_message(
            f"User is not in the watchers list of the issue ID: {params.id}"
        )
        return ActionOutput()

    jira_request(
        asset,
        "DELETE",
        f"rest/api/2/issue/{params.id}/watchers",
        params={"username": params.username}
        if params.username
        else {"accountId": params.user_account_id},
    )

    soar.set_message(
        f"Successfully removed the user from the watchers list of the issue ID: {params.id}"
    )
    return ActionOutput()
