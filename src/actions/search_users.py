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
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from .._asset import Asset
from ..client import JiraClient
from ..consts import (
    JIRA_SEARCH_USERS_ERROR,
    JIRA_LIMIT_VALIDATION_MESSAGE,
)
from ._outputs import AvatarurlsOutput, JiraPermissiveOutput


class LookupUsersParams(Params):
    username: str | None = Param(
        description="A string to match with usernames, name, or email against for JIRA on-prem (required for Jira on-prem)",
        primary=True,
        cef_types=["user name"],
    )
    display_name: str | None = Param(
        description="A string to match with display name for JIRA cloud (required for Jira cloud)",
        primary=True,
        cef_types=["jira user display name"],
    )
    max_results: float | None = Param(
        description="Maximum number of users to return", default=1000
    )


class LookupUsersSummaryOutput(ActionOutput):
    total_users: int = OutputField(example_values=[5])


class LookupUsersOutput(JiraPermissiveOutput):
    name: str = OutputField(
        cef_types=["user name"], example_values=["test"], column_name="Username"
    )
    displayName: str = OutputField(
        cef_types=["jira user display name"],
        example_values=["Test Name"],
        column_name="Display Name",
    )
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=[
            "5d2ef6aa6637260c19b78dfd"  # pragma: allowlist secret
        ],
        column_name="Account ID",
    )
    emailAddress: str = OutputField(
        cef_types=["email"],
        example_values=["test@domain.us"],
        column_name="Email Address",
    )
    accountType: str = OutputField(example_values=["atlassian"])
    active: bool
    avatarUrls: AvatarurlsOutput | None
    key: str = OutputField(example_values=["test"])
    locale: str = OutputField(example_values=["en_US"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=test"],
    )
    timeZone: str = OutputField(example_values=["America/Los_Angeles"])


def lookup_users(
    params: LookupUsersParams, soar: SOARClient, asset: Asset
) -> list[LookupUsersOutput]:
    logger = getLogger()

    has_username = bool(params.username)
    has_display_name = bool(params.display_name)

    if has_username == has_display_name:
        raise ActionFailure(JIRA_SEARCH_USERS_ERROR)

    max_results = int(params.max_results) if params.max_results is not None else 1000

    if max_results <= 0:
        raise ActionFailure(
            JIRA_LIMIT_VALIDATION_MESSAGE.format(parameter="max_results")
        )

    users: list[dict] = []
    start_at = 0
    page_size = 100
    client = JiraClient(asset)

    while len(users) < max_results:
        fetch_count = min(page_size, max_results - len(users))
        page = client.search_users(
            username=params.username,
            display_name=params.display_name,
            start_at=start_at,
            max_results=fetch_count,
        )

        if not page:
            break

        users.extend(page)
        start_at += len(page)

        if len(page) < fetch_count:
            break

    logger.info(f"Total users: {len(users)}")
    soar.set_message(f"Total users: {len(users)}")

    results = [LookupUsersOutput(**user) for user in users]

    soar.set_summary(LookupUsersSummaryOutput(total_users=len(results)))
    return results
