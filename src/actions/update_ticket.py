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

from .._asset import Asset
from ._outputs import (
    AggregateprogressOutput,
    AssigneeOutput,
    AttachmentOutput,
    CommentOutput,
    ComponentsOutput,
    CreatorOutput,
    FixversionsOutput,
    IssuetypeOutput,
    LinkedissuefieldsOutput,
    PriorityOutput,
    ProgressOutput,
    ProjectOutput,
    ReporterOutput,
    ResolutionOutput,
    StatusOutput,
    VersionsOutput,
    VotesOutput,
    WatchesOutput,
    WorklogOutput,
)


class UpdateTicketParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])
    update_fields: str | None = Param(description="JSON containing field values")
    vault_id: str | None = Param(
        description="Vault ID of attachment", primary=True, cef_types=["vault id"]
    )


class InwardissueOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["21237"])
    key: str = OutputField(example_values=["SPOL-133"])
    self: str = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issue/21237"]
    )


class OutwardissueOutput(ActionOutput):
    fields: LinkedissuefieldsOutput | None
    id: str = OutputField(example_values=["11849"])
    key: str = OutputField(cef_types=["jira ticket key"], example_values=["ZEP-14"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/11849"],
    )


class TypeOutput(ActionOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"],
    )


class IssuelinksOutput(ActionOutput):
    id: str = OutputField(example_values=["10615"])
    inwardIssue: InwardissueOutput | None
    outwardIssue: OutwardissueOutput | None
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLink/10615"],
    )
    type: TypeOutput


class FieldsOutput(ActionOutput):
    Epic_Link: str | None = OutputField(alias="Epic Link")
    Sprint: str | None = OutputField(
        example_values=[
            "com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1]"
        ]
    )
    aggregateprogress: AggregateprogressOutput | None
    aggregatetimeestimate: int | None
    aggregatetimeoriginalestimate: int | None
    aggregatetimespent: int | None
    assignee: AssigneeOutput | None
    attachment: list[AttachmentOutput]
    comment: CommentOutput | None
    components: list[ComponentsOutput]
    created: str | None = OutputField(example_values=["2016-03-13T13:22:08.254-0700"])
    creator: CreatorOutput | None
    description: str | None = OutputField(
        example_values=["This is a sample testing description of the ticket"]
    )
    duedate: str | None
    environment: str | None = OutputField(example_values=["above ground"])
    fixVersions: list[FixversionsOutput]
    issuelinks: list[IssuelinksOutput]
    issuetype: IssuetypeOutput | None
    labels: list[str]
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
    security: str | None
    status: StatusOutput | None
    statuscategorychangedate: str | None = OutputField(
        example_values=["2019-07-22T22:43:07.771-0700"]
    )
    summary: str | None = OutputField(example_values=["Sample summary"])
    timeestimate: int | None
    timeoriginalestimate: int | None
    timespent: int | None
    updated: str | None = OutputField(example_values=["2018-09-25T06:49:43.523-0700"])
    versions: list[VersionsOutput]
    votes: VotesOutput | None
    watches: WatchesOutput | None
    worklog: WorklogOutput | None
    workratio: float | None = OutputField(example_values=[-1])


class UpdateTicketOutput(ActionOutput):
    description: str | None = OutputField(
        example_values=["This is a sample testing description of the ticket"]
    )
    fields: FieldsOutput
    id: str = OutputField(example_values=["10246"])
    issue_type: str = OutputField(
        cef_types=["jira issue type"], example_values=["Defect"]
    )
    name: str = OutputField(cef_types=["jira ticket key"], example_values=["MAN-1"])
    priority: str = OutputField(
        cef_types=["jira ticket priority"], example_values=["Medium"]
    )
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["MAN"]
    )
    reporter: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    resolution: str = OutputField(
        cef_types=["jira ticket resolution"], example_values=["Done"]
    )
    status: str = OutputField(example_values=["Done"])
    summary: str = OutputField(example_values=["Sample summary"])


def _update_ticket_view(
    context: ViewContext, results: list[UpdateTicketOutput]
) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


def update_ticket(
    params: UpdateTicketParams, soar: SOARClient, asset: Asset
) -> UpdateTicketOutput:
    import json as _json

    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import (
        JIRA_ERROR_ATTACH_FAILED,
        JIRA_ERROR_FIELDS_JSON_PARSE,
        JIRA_ERROR_FILE_NOT_IN_VAULT,
        JIRA_ERROR_GET_TICKET,
        JIRA_ERROR_UPDATE_NO_PARAM,
        JIRA_SUCCESS_TICKET_UPDATED,
    )
    from ..helpers import description_to_str, jira_request, sanitize_fields_dict

    logger = getLogger()

    # Step 1: Require at least one of update_fields or vault_id
    if not params.update_fields and not params.vault_id:
        raise ActionFailure(JIRA_ERROR_UPDATE_NO_PARAM)

    # Step 2: Verify ticket exists
    try:
        jira_request(asset, "GET", f"rest/api/2/issue/{params.id}")
    except ActionFailure as exc:
        raise ActionFailure(f"Unable to find ticket info: {exc}") from exc

    # Step 3: Update fields if provided
    if params.update_fields:
        try:
            fields = _json.loads(params.update_fields)
        except Exception as exc:
            raise ActionFailure(
                f"{JIRA_ERROR_FIELDS_JSON_PARSE.format(field_name='update_fields')}: {exc}"
            ) from exc

        has_fields_key = "fields" in fields
        has_update_key = "update" in fields
        body = fields if has_fields_key or has_update_key else {"fields": fields}

        jira_request(asset, "PUT", f"rest/api/2/issue/{params.id}", json=body)
        logger.info(JIRA_SUCCESS_TICKET_UPDATED)
        soar.set_message(JIRA_SUCCESS_TICKET_UPDATED)

    # Step 4: Attach vault file if provided
    if params.vault_id:
        attachments = soar.vault.get_attachment(vault_id=params.vault_id)
        if not attachments:
            raise ActionFailure(JIRA_ERROR_FILE_NOT_IN_VAULT)

        meta = attachments[0]
        filename = meta.name
        file_path = meta.path

        # Strip non-ASCII from filename if needed (avoids Jira 500 on unicode filenames)
        ascii_name = filename.encode("ascii", "ignore").decode("ascii")
        if len(ascii_name) < len(filename):
            filename = f"FILENAME_ASCII_{ascii_name}"

        try:
            with open(file_path, "rb") as f:
                jira_request(
                    asset,
                    "POST",
                    f"rest/api/2/issue/{params.id}/attachments",
                    files={"file": (filename, f, "application/octet-stream")},
                    headers={"X-Atlassian-Token": "no-check"},
                )
        except ActionFailure as exc:
            raise ActionFailure(JIRA_ERROR_ATTACH_FAILED.format(str(exc))) from exc
        except Exception as exc:
            raise ActionFailure(JIRA_ERROR_ATTACH_FAILED.format(str(exc))) from exc

    # Step 5: Re-query ticket to build full output
    try:
        issue = jira_request(asset, "GET", f"rest/api/2/issue/{params.id}")
    except ActionFailure as exc:
        raise ActionFailure(f"{JIRA_ERROR_GET_TICKET}: {exc}") from exc

    raw_fields = issue.get("fields", {})

    def _name(obj):
        if isinstance(obj, dict):
            return obj.get("name") or obj.get("displayName")
        return None

    # Step 6: Build and return output
    return UpdateTicketOutput(
        id=issue.get("id", ""),
        name=issue.get("key", ""),
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
