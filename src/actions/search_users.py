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
from soar_sdk.params import Param, Params

from soar_sdk.views.view_parser import ViewContext

from .._app_ref import app
from .._asset import Asset
from ._outputs import AvatarurlsOutput


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


class LookupUsersOutput(ActionOutput):
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=[
            "5d2ef6aa6637260c19b78dfd"  # pragma: allowlist secret
        ],
    )
    accountType: str = OutputField(example_values=["atlassian"])
    active: bool
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Name"]
    )
    emailAddress: str = OutputField(
        cef_types=["email"], example_values=["test@domain.us"]
    )
    key: str = OutputField(example_values=["test"])
    locale: str = OutputField(example_values=["en_US"])
    name: str = OutputField(cef_types=["user name"], example_values=["test"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=test"],
    )
    timeZone: str = OutputField(example_values=["America/Los_Angeles"])


@app.view_handler(template="jira_search_users.html")
def _lookup_users_view(context: ViewContext, results: list[LookupUsersOutput]) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


@app.action(
    description="Get a list of user resources that match the specified search string",
    action_type="investigate",
    view_handler=_lookup_users_view,
    summary_type=LookupUsersSummaryOutput,
    verbose="This action will be used to fetch the username of user resources for Jira on-prem and account_id of user resources for Jira cloud. The default value for [max_results] action parameter is <b>1000</b>. The maximum number of users as specified by the parameter [max_results] will be fetched starting from the first.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to search users using username for Jira cloud, we will use the user's display name to search users. You can use the [display_name] action parameter to search users for Jira cloud, and, [username] action parameter will be used to search users for Jira on-prem.",
)
def lookup_users(
    params: LookupUsersParams, soar: SOARClient, asset: Asset
) -> list[LookupUsersOutput]:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger
    from ..helpers import jira_request
    from ..consts import (
        JIRA_SEARCH_USERS_ERROR,
        JIRA_LIMIT_VALIDATION_MESSAGE,
    )

    logger = getLogger()

    # Validate: exactly one of username or display_name must be provided
    has_username = bool(params.username)
    has_display_name = bool(params.display_name)

    if has_username == has_display_name:
        # Both provided or neither provided
        raise ActionFailure(JIRA_SEARCH_USERS_ERROR)

    # Cloud only supports display_name; reject username-only on cloud
    is_cloud = "atlassian.net" in asset.device_url.lower()
    if is_cloud and has_username and not has_display_name:
        raise ActionFailure(JIRA_SEARCH_USERS_ERROR)

    # Cloud-only: use whichever non-None param is provided as the search query
    query = params.display_name if has_display_name else params.username

    max_results = int(params.max_results) if params.max_results is not None else 1000

    if max_results <= 0:
        raise ActionFailure(
            JIRA_LIMIT_VALIDATION_MESSAGE.format(parameter="max_results")
        )

    users: list[dict] = []
    start_at = 0
    page_size = 100

    while len(users) < max_results:
        fetch_count = min(page_size, max_results - len(users))
        page = jira_request(
            asset,
            "GET",
            "rest/api/2/user/search",
            params={
                "query": query,
                "includeActive": "true",
                "includeInactive": "false",
                "maxResults": fetch_count,
                "startAt": start_at,
            },
        )

        if not page:
            break

        users.extend(page)
        start_at += len(page)

        if len(page) < fetch_count:
            break

    logger.info(f"Total users: {len(users)}")
    soar.set_message(f"Total users: {len(users)}")

    results: list[LookupUsersOutput] = []
    for user in users:
        raw_avatar = user.get("avatarUrls")
        avatar = AvatarurlsOutput.model_validate(raw_avatar) if raw_avatar else None
        results.append(
            LookupUsersOutput(
                accountId=user.get("accountId", ""),
                accountType=user.get("accountType", ""),
                active=user.get("active", False),
                avatarUrls=avatar,
                displayName=user.get("displayName", ""),
                emailAddress=user.get("emailAddress", ""),
                key=user.get("key", ""),
                locale=user.get("locale", ""),
                name=user.get("name", ""),
                self=user.get("self", ""),
                timeZone=user.get("timeZone", ""),
            )
        )

    soar.set_summary(LookupUsersSummaryOutput(total_users=len(results)))
    return results
