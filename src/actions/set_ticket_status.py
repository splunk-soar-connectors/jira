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
from pydantic import Field

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Param, Params

from .._asset import Asset
from ._outputs import (
    AssigneeOutput,
    AttachmentOutput,
    AvatarurlsOutput,
    CommentOutput,
    ComponentsOutput,
    CreatorOutput,
    FixversionsOutput,
    IssuetypeOutput,
    LinkedissuefieldsOutput,
    PriorityOutput,
    ReporterOutput,
    ResolutionOutput,
    StatusOutput,
    TimetrackingOutput,
    VersionsOutput,
    VotesOutput,
    WatchesOutput,
    WorklogsOutput,
)


class SetStatusParams(Params):
    id: str = Param(
        description="Ticket (issue) key", primary=True, cef_types=["jira ticket key"]
    )
    status: str = Param(
        description="Status to set", primary=True, cef_types=["jira ticket status"]
    )
    resolution: str | None = Param(
        description="Resolution to set",
        primary=True,
        cef_types=["jira ticket resolution"],
    )
    comment: str | None = Param(description="Comment to set")
    update_fields: str | None = Param(description="JSON containing field values")
    time_spent: str | None = Param(description="Time Spent to Log")


# set_status has percent in both AggregateprogressOutput and ProgressOutput
class AggregateprogressOutput(ActionOutput):
    percent: float = OutputField(example_values=[100])
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class ProgressOutput(ActionOutput):
    percent: float = OutputField(example_values=[100])
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


# set_status ProjectOutput omits projectCategory and projectTypeKey/simplified
class ProjectOutput(ActionOutput):
    avatarUrls: AvatarurlsOutput | None
    id: str = OutputField(example_values=["10100"])
    key: str = OutputField(cef_types=["jira project key"], example_values=["MAN"])
    name: str = OutputField(example_values=["TestProject"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/project/10100"],
    )


class InwardissueOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["21576"])
    key: str = OutputField(example_values=["MAN-278"])
    self: str = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issue/21576"]
    )


class OutwardissueOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["21133"])
    key: str = OutputField(example_values=["SPOL-44"])
    self: str = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issue/21133"]
    )


class TypeOutput(ActionOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"]
    )


class IssuelinksOutput(ActionOutput):
    id: str = OutputField(example_values=["10727"])
    inwardIssue: InwardissueOutput | None
    outwardIssue: OutwardissueOutput | None
    self: str = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issueLink/10727"]
    )
    type: TypeOutput


class WorklogOutput(ActionOutput):
    maxResults: float = OutputField(example_values=[20])
    startAt: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])
    worklogs: list[WorklogsOutput]


class FieldsOutput(ActionOutput):
    Epic_Link: str | None = OutputField(alias="Epic Link")
    Severity: str | None
    Sprint: str | None = OutputField(
        example_values=[
            "com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1]"
        ]
    )
    aggregateprogress: AggregateprogressOutput | None
    aggregatetimeestimate: float | None
    aggregatetimeoriginalestimate: str | None
    aggregatetimespent: float | None
    assignee: AssigneeOutput | None
    attachment: list[AttachmentOutput] = Field(default_factory=list)
    comment: CommentOutput | None
    components: list[ComponentsOutput] = Field(default_factory=list)
    created: str | None = OutputField(example_values=["2016-03-13T13:22:08.254-0700"])
    creator: CreatorOutput | None
    description: str | None = OutputField(
        example_values=["This is a sample testing description of the ticket"]
    )
    duedate: str | None
    environment: str | None = OutputField(example_values=["above ground"])
    fixVersions: list[FixversionsOutput] = Field(default_factory=list)
    issuelinks: list[IssuelinksOutput] = Field(default_factory=list)
    issuetype: IssuetypeOutput | None
    labels: list[str] = Field(default_factory=list)
    lastViewed: str | None = OutputField(
        example_values=["2018-09-20T23:54:50.643-0700"]
    )
    priority: PriorityOutput | None
    progress: ProgressOutput | None
    project: ProjectOutput | None
    reporter: ReporterOutput | None
    resolution: ResolutionOutput | None
    resolutiondate: str | None = OutputField(
        example_values=["2018-09-20T19:02:38.646-0700"]
    )
    status: StatusOutput | None
    summary: str | None = OutputField(example_values=["Sample summary"])
    timeestimate: float | None
    timeoriginalestimate: str | None
    timespent: float | None
    timetracking: TimetrackingOutput | None
    updated: str | None = OutputField(example_values=["2018-09-25T06:21:27.802-0700"])
    versions: list[VersionsOutput] = Field(default_factory=list)
    votes: VotesOutput | None
    watches: WatchesOutput | None
    worklog: WorklogOutput | None
    workratio: float | None = OutputField(example_values=[-1])


class SetStatusOutput(ActionOutput):
    summary: str = OutputField(column_name="Summary", example_values=["Sample summary"])
    description: str | None = OutputField(
        column_name="Description",
        example_values=["This is a sample testing description of the ticket"],
    )
    id: str = OutputField(column_name="Id", example_values=["10246"])
    issue_type: str = OutputField(
        column_name="Type", cef_types=["jira issue type"], example_values=["Defect"]
    )
    name: str = OutputField(
        column_name="Key", cef_types=["jira ticket key"], example_values=["MAN-1"]
    )
    status: str = OutputField(column_name="Status", example_values=["Done"])
    priority: str = OutputField(
        column_name="Priority",
        cef_types=["jira ticket priority"],
        example_values=["Medium"],
    )
    resolution: str = OutputField(
        column_name="Resolution",
        cef_types=["jira ticket resolution"],
        example_values=["Done"],
    )
    reporter: str = OutputField(
        column_name="Reporter",
        cef_types=["jira user display name"],
        example_values=["Test Admin"],
    )
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["MAN"]
    )
    fields: FieldsOutput


def set_status(
    params: SetStatusParams, soar: SOARClient, asset: Asset
) -> SetStatusOutput:
    import json as json_mod

    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import JIRA_ERROR_FIELDS_JSON_PARSE
    from ..helpers import description_to_str, jira_request, sanitize_fields_dict

    logger = getLogger()

    def _name(obj):
        if isinstance(obj, dict):
            return obj.get("name") or obj.get("displayName")
        return None

    # Step 1: Verify ticket exists
    try:
        jira_request(asset, "GET", f"rest/api/2/issue/{params.id}")
    except ActionFailure as exc:
        raise ActionFailure(
            f"Unable to find ticket info. Please make sure the issue exists: {exc}"
        ) from exc

    # Step 2: Apply update_fields if provided
    if params.update_fields:
        try:
            fields = json_mod.loads(params.update_fields)
        except Exception as exc:
            raise ActionFailure(
                JIRA_ERROR_FIELDS_JSON_PARSE.format(field_name="update_fields")
                + f": {exc}"
            ) from exc

        if "fields" in fields or "update" in fields:
            body = fields
        else:
            body = {"fields": fields}

        jira_request(asset, "PUT", f"rest/api/2/issue/{params.id}", json=body)

    # Step 3: Get available transitions and find the matching one
    transitions_resp = jira_request(
        asset, "GET", f"rest/api/2/issue/{params.id}/transitions"
    )
    transitions = transitions_resp.get("transitions", [])
    transition_id = None
    for t in transitions:
        if t.get("name") == params.status:
            transition_id = t["id"]
            break

    if transition_id is None:
        raise ActionFailure(
            f"Invalid status '{params.status}'. Valid transitions: "
            + ", ".join(t["name"] for t in transitions)
        )

    # Step 4: Build transition body (with optional resolution)
    if params.resolution:
        resolutions_resp = jira_request(asset, "GET", "rest/api/2/resolution")
        resolutions = resolutions_resp if isinstance(resolutions_resp, list) else []
        resolution_id = None
        for r in resolutions:
            if r.get("name") == params.resolution:
                resolution_id = r["id"]
                break

        if resolution_id is None:
            raise ActionFailure(
                f"Invalid resolution '{params.resolution}'. Valid resolutions: "
                + ", ".join(r["name"] for r in resolutions)
            )

        transition_body = {
            "transition": {"id": transition_id},
            "fields": {"resolution": {"id": resolution_id}},
        }
    else:
        transition_body = {"transition": {"id": transition_id}}

    # Step 5: Log time spent if provided
    if params.time_spent:
        jira_request(
            asset,
            "POST",
            f"rest/api/2/issue/{params.id}/worklog",
            json={"timeSpent": params.time_spent},
        )

    # Step 6: Perform the transition
    jira_request(
        asset, "POST", f"rest/api/2/issue/{params.id}/transitions", json=transition_body
    )

    # Step 7: Add comment (soft failure — comment on a closed ticket may be rejected)
    if params.comment:
        try:
            jira_request(
                asset,
                "POST",
                f"rest/api/2/issue/{params.id}/comment",
                json={"body": params.comment},
            )
        except ActionFailure as exc:
            logger.warning(f"Failed to add comment after status transition: {exc}")

    # Step 8: Re-query ticket for final state
    issue = jira_request(asset, "GET", f"rest/api/2/issue/{params.id}")
    raw_fields = issue["fields"]

    # Step 9: Build and return output
    soar.set_message("The status is updated successfully")
    return SetStatusOutput(
        id=issue["id"],
        name=issue["key"],
        summary=raw_fields.get("summary", ""),
        description=description_to_str(raw_fields.get("description")),
        project_key=(raw_fields.get("project") or {}).get("key", ""),
        issue_type=_name(raw_fields.get("issuetype")) or "",
        priority=_name(raw_fields.get("priority")) or "",
        reporter=_name(raw_fields.get("reporter")) or "",
        status=_name(raw_fields.get("status")) or "",
        resolution=_name(raw_fields.get("resolution")) or "Unresolved",
        fields=sanitize_fields_dict(raw_fields),
    )
