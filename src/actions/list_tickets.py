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
from soar_sdk.action_results import (
    ActionOutput,
    OutputField,
)
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Param, Params

from .._asset import Asset
from ..client import JiraClient
from ..consts import (
    DEFAULT_MAX_VALUE,
    JIRA_ERROR_LIST_TICKETS_FAILED,
    JIRA_ERROR_NEGATIVE_INPUT,
    JIRA_TOTAL_ISSUES,
)
from ..helpers import (
    description_to_str,
    get_custom_field_map,
    sanitize_fields_dict,
)
from ._outputs import (
    JiraPermissiveOutput,
    LegacyIssueFieldsOutput,
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
class _AttachmentAuthorOutput(JiraPermissiveOutput):
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=["557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce"],
    )
    accountType: str = OutputField(example_values=["atlassian"])


class _AttachmentOutput(JiraPermissiveOutput):
    author: _AttachmentAuthorOutput | None


# list_tickets: CommentsOutput only has visibility
class _VisibilityOutput(JiraPermissiveOutput):
    type: str = OutputField(example_values=["group", "role"])
    value: str = OutputField(example_values=["jira-software-users"])


class _CommentsOutput(JiraPermissiveOutput):
    visibility: _VisibilityOutput | None


class _CommentOutput(JiraPermissiveOutput):
    comments: list[_CommentsOutput]
    maxResults: float
    startAt: float
    total: float


class TypeOutput(JiraPermissiveOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"],
    )


class OutwardissueOutput(JiraPermissiveOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11849"])
    key: str = OutputField(cef_types=["jira ticket key"], example_values=["ZEP-14"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11849"],
    )


class IssuelinksOutput(JiraPermissiveOutput):
    id: str = OutputField(example_values=["10615"])
    outwardIssue: OutwardissueOutput | None
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLink/10615"],
    )
    type: TypeOutput


class ParentOutput(JiraPermissiveOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11811"])
    key: str = OutputField(example_values=["PHANINCIDE-315"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11811"],
    )


class SubtasksOutput(JiraPermissiveOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11839"])
    key: str = OutputField(example_values=["PHANINCIDE-316"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11839"],
    )


class _WorklogOutput(JiraPermissiveOutput):
    maxResults: float
    startAt: float
    total: float


class FieldsOutput(LegacyIssueFieldsOutput):
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
        example_values=["This is a sample testing description"]
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
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["PRJ"], column_name="Project ID"
    )
    id: str = OutputField(example_values=["11840"], column_name="Ticket ID")
    issue_type: str = OutputField(
        cef_types=["jira issue type"], example_values=["Sub-Task"], column_name="Type"
    )
    name: str = OutputField(
        cef_types=["jira ticket key"],
        example_values=["PHANINCIDE-317"],
        column_name="Key",
    )
    status: str = OutputField(example_values=["To Do"], column_name="Status")
    priority: str = OutputField(
        cef_types=["jira ticket priority"],
        example_values=["Medium"],
        column_name="Priority",
    )
    resolution: str = OutputField(
        cef_types=["jira ticket resolution"],
        example_values=["Unresolved"],
        column_name="Resolution",
    )
    reporter: str = OutputField(
        cef_types=["jira user display name"],
        example_values=["Test Admin"],
        column_name="Reporter",
    )
    summary: str = OutputField(
        example_values=["Sub-taskofBigTask"], column_name="Summary"
    )
    description: str | None = OutputField(
        example_values=["This is a sample testing description"],
        column_name="Description",
    )
    fields: FieldsOutput


def list_tickets(
    params: ListTicketsParams, soar: SOARClient, asset: Asset
) -> list[ListTicketsOutput]:
    logger = getLogger()

    project_key = params.project_key

    start_index = int(params.start_index) if params.start_index is not None else 0
    max_results = (
        int(params.max_results) if params.max_results is not None else DEFAULT_MAX_VALUE
    )
    if max_results <= 0:
        raise ActionFailure("Please provide a positive value for max_results")
    jql_query = params.query

    if start_index < 0:
        raise ActionFailure(JIRA_ERROR_NEGATIVE_INPUT)

    if not project_key and not jql_query:
        raise ActionFailure(
            JIRA_ERROR_LIST_TICKETS_FAILED
            + "Please provide either project_key or JQL Query.Both Fields can not be empty"
        )

    if jql_query and project_key:
        jql = f"project={project_key} and {jql_query}"
    elif project_key:
        jql = f"project={project_key}"
    else:
        jql = jql_query

    issues: list[dict] = []
    page_size = 100
    client = JiraClient(asset)

    # Jira Cloud's enhanced search endpoint uses an opaque cursor rather than
    # ``startAt``. To preserve the action's existing ``start_index`` contract,
    # consume and skip complete pages until that offset is reached, then
    # collect at most ``max_results`` issues.
    next_page_token: str | None = None
    traversed = 0

    while len(issues) < max_results:
        response = client.search_issues(
            jql,
            max_results=page_size,
            fields="*all",
            next_page_token=next_page_token,
        )
        page_issues = response.get("issues", [])
        if not page_issues:
            break

        page_offset = max(0, start_index - traversed)
        if page_offset < len(page_issues):
            remaining = max_results - len(issues)
            issues.extend(page_issues[page_offset : page_offset + remaining])
        traversed += len(page_issues)

        if len(issues) >= max_results or response.get("isLast", False):
            break

        new_token = response.get("nextPageToken")
        if not new_token or new_token == next_page_token:
            break
        next_page_token = new_token

    logger.info(f"{JIRA_TOTAL_ISSUES} : {len(issues)}")

    results: list[ListTicketsOutput] = []
    for issue in issues:
        custom_field_map = get_custom_field_map(asset, issue.get("key") or issue["id"])
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
                fields=sanitize_fields_dict(fields, custom_field_map),
            )
        )
    soar.set_summary(ListTicketsSummaryOutput(total_issues=len(results)))
    return results
