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


class LinkTicketsParams(Params):
    from_id: str = Param(
        description="First ticket (issue) key",
        primary=True,
        cef_types=["jira ticket key"],
    )
    to_id: str = Param(
        description="Second ticket (issue) key",
        primary=True,
        cef_types=["jira ticket key"],
    )
    link_type: str = Param(description="Type of link to create", default="Duplicate")
    comment: str | None = Param(description="Comment to add")
    comment_visibility_type: str | None = Param(
        description="How to limit the comment visibility", value_list=["group", "role"]
    )
    comment_visibility_name: str | None = Param(
        description="Name of group/role able to see the comment"
    )


class LinkTicketsOutput(ActionOutput):
    result: str = OutputField(example_values=["success", "failed"])


@app.view_handler(template="jira_link_tickets.html")
def _link_tickets_view(context: ViewContext, results: list[LinkTicketsOutput]) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


@app.action(
    description="Create a link between two separate tickets",
    action_type="generic",
    read_only=False,
    verbose="If the comment is not added, comment_visibility and comment_visibility_type values will not affect the action result.",
    view_handler=_link_tickets_view,
)
def link_tickets(
    params: LinkTicketsParams, soar: SOARClient, asset: Asset
) -> LinkTicketsOutput:
    from soar_sdk.exceptions import ActionFailure

    from ..helpers import jira_request

    # Resolve link type case-insensitively against the instance's available types
    link_types_resp = jira_request(asset, "GET", "rest/api/2/issueLinkType")
    available = link_types_resp.get("issueLinkTypes") or []
    canonical_name: str | None = None
    for lt in available:
        if lt.get("name", "").lower() == params.link_type.lower():
            canonical_name = lt["name"]
            break
    if canonical_name is None:
        raise ActionFailure(
            f"No issue link type with name '{params.link_type}' found. "
            f"Available: {', '.join(lt.get('name', '') for lt in available)}"
        )

    payload = {
        "type": {"name": canonical_name},
        "inwardIssue": {"key": params.from_id},
        "outwardIssue": {"key": params.to_id},
    }

    if params.comment is not None:
        payload["comment"] = {"body": params.comment}
        if params.comment_visibility_type and params.comment_visibility_name:
            payload["comment"]["visibility"] = {
                "type": params.comment_visibility_type,
                "value": params.comment_visibility_name,
            }

    jira_request(asset, "POST", "rest/api/2/issueLink", json=payload)

    soar.set_message("The ticket has been linked successfully")
    return LinkTicketsOutput(result="success")
