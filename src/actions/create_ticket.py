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
    AggregateprogressOutput,
    AssigneeOutput,
    AttachmentOutput,
    CommentOutput,
    CreatorOutput,
    IssuetypeOutput,
    PriorityOutput,
    ProgressOutput,
    ProjectOutput,
    ReporterOutput,
    StatusOutput,
    VotesOutput,
    WatchesOutput,
    WorklogOutput,
)


class CreateTicketParams(Params):
    project_key: str = Param(
        description="Project key to add the issue to (case-sensitive)",
        primary=True,
        cef_types=["jira project key"],
    )
    summary: str = Param(description="Summary of the issue")
    description: str | None = Param(description="Description of the issue")
    issue_type: str = Param(
        description="Type of the issue (case-sensitive)",
        primary=True,
        cef_types=["jira issue type"],
    )
    priority: str | None = Param(
        description="Priority of the issue",
        primary=True,
        cef_types=["jira ticket priority"],
    )
    assignee: str | None = Param(
        description="Assignee username (required for Jira on-prem, assign required permissions)",
        primary=True,
        cef_types=["user name"],
    )
    assignee_account_id: str | None = Param(
        description="Assignee user account ID (required for Jira cloud, assign required permissions)",
        primary=True,
        cef_types=["jira user account id"],
    )
    fields: str | None = Param(description="JSON containing field values")
    vault_id: str | None = Param(
        description="Vault ID of attachment", primary=True, cef_types=["vault id"]
    )


# create_ticket FieldsOutput — no components/fixVersions/issuelinks/labels/versions
class FieldsOutput(ActionOutput):
    Epic_Link: str | None = OutputField(alias="Epic Link")
    Epic_Name: str | None = OutputField(example_values=["Test epic"], alias="Epic Name")
    Severity: str | None
    Sprint: str | None
    aggregateprogress: AggregateprogressOutput | None
    aggregatetimeestimate: str | None
    aggregatetimeoriginalestimate: str | None
    aggregatetimespent: str | None
    assignee: AssigneeOutput | None
    attachment: list[AttachmentOutput] = Field(default_factory=list)
    comment: CommentOutput | None
    created: str | None = OutputField(example_values=["2018-09-25T06:31:58.854-0700"])
    creator: CreatorOutput | None
    description: str | None = OutputField(
        example_values=["Jira QA automation ticket description"]
    )
    duedate: str | None
    environment: str | None
    issuetype: IssuetypeOutput | None
    lastViewed: str | None
    priority: PriorityOutput | None
    progress: ProgressOutput | None
    project: ProjectOutput | None
    reporter: ReporterOutput | None
    resolution: str | None
    resolutiondate: str | None = OutputField(
        example_values=["2018-10-03T03:42:10.912-0700"]
    )
    security: str | None
    status: StatusOutput | None
    statuscategorychangedate: str | None = OutputField(
        example_values=["2019-07-22T22:43:07.771-0700"]
    )
    summary: str | None = OutputField(example_values=["Jira QA ticket"])
    timeestimate: str | None
    timeoriginalestimate: str | None
    timespent: str | None
    updated: str | None = OutputField(example_values=["2018-09-25T06:31:58.854-0700"])
    votes: VotesOutput | None
    watches: WatchesOutput | None
    worklog: WorklogOutput | None
    workratio: float | None = OutputField(example_values=[-1])


class CreateTicketOutput(ActionOutput):
    summary: str = OutputField(column_name="Summary", example_values=["Jira QA ticket"])
    description: str | None = OutputField(
        column_name="Description",
        example_values=["Jira QA automation ticket description"],
    )
    id: str = OutputField(column_name="Id", example_values=["11850"])
    issue_type: str = OutputField(
        column_name="Type",
        cef_types=["jira issue type"],
        example_values=["Story", "Task"],
    )
    name: str = OutputField(
        column_name="Key", cef_types=["jira ticket key"], example_values=["MAN-240"]
    )
    status: str = OutputField(column_name="Status", example_values=["To Do"])
    priority: str = OutputField(
        column_name="Priority",
        cef_types=["jira ticket priority"],
        example_values=["Medium"],
    )
    resolution: str = OutputField(
        column_name="Resolution",
        cef_types=["jira ticket resolution"],
        example_values=["Unresolved"],
    )
    reporter: str = OutputField(
        column_name="Reporter",
        cef_types=["jira user display name"],
        example_values=["Test Admin"],
    )
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["MAN"]
    )
    assign_error: str
    attach_error: str
    json_fields_error: str
    fields: FieldsOutput


def create_ticket(
    params: CreateTicketParams, soar: SOARClient, asset: Asset
) -> CreateTicketOutput:
    import json as _json

    from soar_sdk.exceptions import ActionFailure

    from ..consts import (
        JIRA_ASSIGNEE_ERROR,
        JIRA_ERROR_ATTACH_FAILED,
        JIRA_ERROR_FIELDS_JSON_PARSE,
        JIRA_ERROR_FILE_NOT_IN_VAULT,
        JIRA_ERROR_GET_TICKET,
        JIRA_ERROR_INPUT_FIELDS_NOT_THE_ONLY_ONE,
        JIRA_ERROR_TICKET_ASSIGNMENT_FAILED,
        JIRA_SUCCESS_TICKET_CREATED,
    )
    from soar_sdk.logging import getLogger

    from ..helpers import description_to_str, jira_request, sanitize_fields_dict

    logger = getLogger()

    # Validate: only one of assignee / assignee_account_id may be set
    if params.assignee and params.assignee_account_id:
        raise ActionFailure(JIRA_ASSIGNEE_ERROR)

    # --- Build fields dict ---
    fields: dict = {}
    json_fields_error = ""

    if params.fields:
        try:
            fields = _json.loads(params.fields)
        except Exception as exc:
            raise ActionFailure(
                f"{JIRA_ERROR_FIELDS_JSON_PARSE.format(field_name='fields')}: {exc}"
            ) from exc

        if "fields" in fields:
            if len(fields) > 1:
                raise ActionFailure(JIRA_ERROR_INPUT_FIELDS_NOT_THE_ONLY_ONE)
            fields = fields["fields"]

    # Individual params fill in only if not already in fields
    if params.project_key and "project" not in fields:
        fields["project"] = {"key": params.project_key}
    if params.summary and "summary" not in fields:
        fields["summary"] = params.summary
    if params.description and "description" not in fields:
        fields["description"] = params.description
    if params.issue_type and "issuetype" not in fields:
        fields["issuetype"] = {"name": params.issue_type}
    if params.priority and "priority" not in fields:
        fields["priority"] = {"name": params.priority}

    # --- Create the issue ---
    logger.info("Creating Jira ticket")
    new_issue = jira_request(asset, "POST", "rest/api/2/issue", json={"fields": fields})
    issue_key = new_issue.get("key")
    issue_id = new_issue.get("id")
    logger.info(f"Created ticket {issue_key}")

    assign_error = ""
    attach_error = ""

    # --- Assign (Jira Cloud only — accountId) ---
    if params.assignee_account_id:
        try:
            jira_request(
                asset,
                "PUT",
                f"rest/api/2/issue/{issue_key}/assignee",
                json={"accountId": params.assignee_account_id},
            )
        except ActionFailure as exc:
            assign_error = JIRA_ERROR_TICKET_ASSIGNMENT_FAILED.format(
                params.assignee_account_id, str(exc)
            )
            logger.warning(assign_error)

    # --- Attach vault file ---
    if params.vault_id:
        try:
            attachments = soar.vault.get_attachment(vault_id=params.vault_id)
            if not attachments:
                attach_error = JIRA_ERROR_FILE_NOT_IN_VAULT
            else:
                meta = attachments[0]
                filename = meta.name
                file_path = meta.path

                # Strip non-ASCII from filename if needed (avoids Jira 500 on unicode filenames)
                ascii_name = filename.encode("ascii", "ignore").decode("ascii")
                if len(ascii_name) < len(filename):
                    filename = f"FILENAME_ASCII_{ascii_name}"

                with open(file_path, "rb") as f:
                    jira_request(
                        asset,
                        "POST",
                        f"rest/api/2/issue/{issue_key}/attachments",
                        files={"file": (filename, f, "application/octet-stream")},
                        headers={"X-Atlassian-Token": "no-check"},
                    )
        except ActionFailure as exc:
            attach_error = JIRA_ERROR_ATTACH_FAILED.format(str(exc))
            logger.warning(attach_error)
        except Exception as exc:
            attach_error = JIRA_ERROR_ATTACH_FAILED.format(str(exc))
            logger.warning(attach_error)

    # --- Re-query ticket to build full output ---
    try:
        issue = jira_request(asset, "GET", f"rest/api/2/issue/{issue_key}")
    except ActionFailure as exc:
        raise ActionFailure(f"{JIRA_ERROR_GET_TICKET}: {exc}") from exc

    raw_fields = issue.get("fields", {})

    def _name(obj):
        if isinstance(obj, dict):
            return obj.get("name") or obj.get("displayName")
        return None

    resolution = _name(raw_fields.get("resolution")) or "Unresolved"

    status_message = JIRA_SUCCESS_TICKET_CREATED.format(id=issue_id, key=issue_key)
    if assign_error:
        status_message = f"{status_message} {assign_error}"
    if attach_error:
        status_message = f"{status_message} {attach_error}"

    logger.info(status_message)
    soar.set_message(status_message)

    return CreateTicketOutput(
        id=issue_id,
        name=issue_key,
        summary=raw_fields.get("summary", ""),
        description=description_to_str(raw_fields.get("description")),
        project_key=(raw_fields.get("project") or {}).get("key", ""),
        issue_type=_name(raw_fields.get("issuetype")) or "",
        priority=_name(raw_fields.get("priority")) or "",
        reporter=_name(raw_fields.get("reporter")) or "",
        status=_name(raw_fields.get("status")) or "",
        resolution=resolution,
        fields=sanitize_fields_dict(raw_fields),
        assign_error=assign_error,
        attach_error=attach_error,
        json_fields_error=json_fields_error,
    )
