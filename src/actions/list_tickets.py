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
from ._outputs import (
    AggregateprogressOutput,
    AssigneeOutput,
    CreatorOutput,
    IssuetypeOutput,
    LinkedissuefieldsOutput,
    PriorityOutput,
    ProgressOutput,
    ProjectOutput,
    ReporterOutput,
    ResolutionOutput,
    StatusOutput,
    VotesOutput,
    WatchesOutput,
)


class ListTicketsSummaryOutput(ActionOutput):
    total_issues: int = OutputField(example_values=[10])


class ListTicketsParams(Params):
    project_key: str | None = Param(
        description="Project key to list the tickets (issues) of",
        primary=True,
        cef_types=["jira project key"],
    )
    query: str | None = Param(description="Additional parameters to query for in JQL")
    start_index: float | None = Param(description="Start index of the list", default=0)
    max_results: float | None = Param(
        description="Maximum number of issues to return", default=1000
    )


# list_tickets: lightweight AttachmentOutput (only accountId/accountType from app.py)
class _AttachmentAuthorOutput(ActionOutput):
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=["557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce"],
    )
    accountType: str = OutputField(example_values=["atlassian"])


class _AttachmentOutput(ActionOutput):
    author: _AttachmentAuthorOutput | None


# list_tickets: CommentsOutput only has visibility
class _VisibilityOutput(ActionOutput):
    type: str = OutputField(example_values=["group", "role"])
    value: str = OutputField(example_values=["jira-software-users"])


class _CommentsOutput(ActionOutput):
    visibility: _VisibilityOutput | None


class _CommentOutput(ActionOutput):
    comments: list[_CommentsOutput]
    maxResults: float
    startAt: float
    total: float


class TypeOutput(ActionOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"],
    )


class OutwardissueOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11849"])
    key: str = OutputField(cef_types=["jira ticket key"], example_values=["ZEP-14"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11849"],
    )


class IssuelinksOutput(ActionOutput):
    id: str = OutputField(example_values=["10615"])
    outwardIssue: OutwardissueOutput | None
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLink/10615"],
    )
    type: TypeOutput


class ParentOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11811"])
    key: str = OutputField(example_values=["PHANINCIDE-315"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11811"],
    )


class SubtasksOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11839"])
    key: str = OutputField(example_values=["PHANINCIDE-316"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11839"],
    )


class _WorklogOutput(ActionOutput):
    maxResults: float
    startAt: float
    total: float


class FieldsOutput(ActionOutput):
    aggregateprogress: AggregateprogressOutput | None
    aggregatetimeestimate: str | None
    aggregatetimeoriginalestimate: str | None
    aggregatetimespent: str | None
    assignee: AssigneeOutput | None
    attachment: list[_AttachmentOutput]
    comment: _CommentOutput | None
    created: str | None = OutputField(example_values=["2018-09-23T19:40:35.000-0700"])
    creator: CreatorOutput | None
    description: str | None = OutputField(
        cef_types=["url"], example_values=["This is a sample testing description"]
    )
    duedate: str | None
    environment: str | None
    issuelinks: list[IssuelinksOutput]
    issuetype: IssuetypeOutput | None
    lastViewed: str | None = OutputField(
        example_values=["2018-09-23T22:28:12.754-0700"]
    )
    parent: ParentOutput | None
    priority: PriorityOutput | None
    progress: ProgressOutput | None
    project: ProjectOutput | None
    reporter: ReporterOutput | None
    resolution: ResolutionOutput | None
    resolutiondate: str | None = OutputField(
        example_values=["2018-09-23T19:40:35.000-0700"]
    )
    security: str | None
    status: StatusOutput | None
    statuscategorychangedate: str | None = OutputField(
        example_values=["2019-07-22T22:43:07.771-0700"]
    )
    subtasks: list[SubtasksOutput]
    summary: str | None = OutputField(example_values=["Sub-taskofBigTask"])
    timeestimate: str | None
    timeoriginalestimate: str | None
    timespent: str | None
    updated: str | None = OutputField(example_values=["2018-09-23T22:28:12.000-0700"])
    votes: VotesOutput | None
    watches: WatchesOutput | None
    worklog: _WorklogOutput | None
    workratio: float | None = OutputField(example_values=[-1])


class ListTicketsOutput(ActionOutput):
    description: str | None = OutputField(
        cef_types=["url"], example_values=["This is a sample testing description"]
    )
    fields: FieldsOutput
    id: str = OutputField(example_values=["11840"])
    issue_type: str = OutputField(
        cef_types=["jira issue type"], example_values=["Sub-Task"]
    )
    name: str = OutputField(
        cef_types=["jira ticket key"], example_values=["PHANINCIDE-317"]
    )
    priority: str = OutputField(
        cef_types=["jira ticket priority"], example_values=["Medium"]
    )
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["PRJ"]
    )
    reporter: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    resolution: str = OutputField(
        cef_types=["jira ticket resolution"], example_values=["Unresolved"]
    )
    status: str = OutputField(example_values=["To Do"])
    summary: str = OutputField(example_values=["Sub-taskofBigTask"])


@app.view_handler(template="jira_list_tickets.html")
def _list_tickets_view(context: ViewContext, results: list[ListTicketsOutput]) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


@app.action(
    description="Get a list of tickets (issues) in a specified project",
    action_type="investigate",
    verbose="The default value for the parameter <b>'start_index'</b> is <b>0</b> and for <b>'max_results'</b> is <b>1000</b>. The maximum number of tickets as specified by the parameter <b>'max_results'</b> will be fetched starting from the index specified by the parameter <b>'start_index'</b>.",
    view_handler=_list_tickets_view,
    summary_type=ListTicketsSummaryOutput,
)
def list_tickets(
    params: ListTicketsParams, soar: SOARClient, asset: Asset
) -> list[ListTicketsOutput]:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger
    from ..helpers import description_to_str, jira_request, sanitize_fields_dict
    from ..consts import (
        JIRA_ERROR_LIST_TICKETS_FAILED,
        JIRA_ERROR_NEGATIVE_INPUT,
        JIRA_TOTAL_ISSUES,
    )

    logger = getLogger()

    project_key = params.project_key
    from ..consts import DEFAULT_MAX_VALUE

    start_index = int(params.start_index) if params.start_index is not None else 0
    max_results = (
        min(int(params.max_results), DEFAULT_MAX_VALUE)
        if params.max_results is not None
        else DEFAULT_MAX_VALUE
    )
    jql_query = params.query

    if start_index < 0:
        raise ActionFailure(JIRA_ERROR_NEGATIVE_INPUT)

    if not project_key and not jql_query:
        raise ActionFailure(
            JIRA_ERROR_LIST_TICKETS_FAILED
            + "Please provide either project_key or JQL Query.Both Fields can not be empty"
        )

    # When Both JQL and Project Key are present
    if jql_query and project_key:
        jql = f"project={project_key} and {jql_query}"
    elif project_key:
        jql = f"project={project_key}"
    else:
        jql = jql_query

    issues: list[dict] = []

    starts_at = start_index

    page_size = 100

    while True:
        fetch_limit = min(page_size, max_results - len(issues))
        response = jira_request(
            asset,
            "GET",
            "rest/api/3/search/jql",
            params={
                "jql": jql,
                "startAt": starts_at,
                "maxResults": fetch_limit,
                "fields": "*all",
            },
        )
        page_issues: list[dict] = response.get("issues", [])
        issues.extend(page_issues)

        logger.info(f"{JIRA_TOTAL_ISSUES} : {len(issues)}")

        if len(page_issues) < page_size or len(issues) >= max_results:
            break
        starts_at += len(page_issues)

    results: list[ListTicketsOutput] = []

    for issue in issues:
        fields = issue.get("fields") or {}
        results.append(
            ListTicketsOutput(
                id=issue["id"],
                name=issue["key"],
                summary=fields.get("summary", ""),
                description=description_to_str(fields.get("description")),
                project_key=(fields.get("project") or {}).get("key", ""),
                issue_type=(fields.get("issuetype") or {}).get("name", ""),
                priority=(fields.get("priority") or {}).get("name", ""),
                reporter=(fields.get("reporter") or {}).get("displayName", ""),
                status=(fields.get("status") or {}).get("name", ""),
                resolution=(fields.get("resolution") or {}).get("name") or "Unresolved",
                fields=sanitize_fields_dict(fields),
            )
        )
    soar.set_summary(ListTicketsSummaryOutput(total_issues=len(results)))
    return results
