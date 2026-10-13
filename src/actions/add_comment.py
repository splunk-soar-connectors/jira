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
from ..client import JiraClient


class AddCommentParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])
    comment: str = Param(description="Comment to add")
    internal: bool | None = Param(
        description="Whether comment should be internal only in Jira Service Desk. Defaults to true when omitted.",
        default=True,
    )


def add_comment(
    params: AddCommentParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    logger = getLogger()

    client = JiraClient(asset)
    try:
        client.issue(params.id)
        internal = True if params.internal is None else params.internal
        client.add_comment(params.id, params.comment, internal=internal)
    except Exception as exc:
        raise ActionFailure(
            f"Unable to add comment. Please make sure that the issue exists: {exc}"
        ) from exc
    logger.info("Successfully added the comment")
    soar.set_message("Successfully added the comment")
    return ActionOutput()
