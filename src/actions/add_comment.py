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


class AddCommentParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])
    comment: str = Param(description="Comment to add")
    internal: bool | None = Param(
        description="Whether comment should be internal only or not in Jira Service Desk (if the value is not provided, it will internally be treated as 'false')",
        default=True,
    )


def add_comment(
    params: AddCommentParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..helpers import jira_request

    logger = getLogger()

    try:
        jira_request(
            asset=asset, method="GET", endpoint=f"rest/api/2/issue/{params.id}"
        )
    except ActionFailure as exc:
        raise ActionFailure(
            f"Unable to find ticket info.Please make sure that the issue exists: {exc}"
        ) from exc

    body: dict = {"body": params.comment}

    # Internal comments use the sd.public.comment property — same endpoint as regular comments
    if params.internal:
        body["properties"] = [{"key": "sd.public.comment", "value": {"internal": True}}]

    jira_request(asset, "POST", f"rest/api/2/issue/{params.id}/comment", json=body)
    logger.info("Successfully added the comment")
    soar.set_message("Successfully added the comment")
    return ActionOutput()
