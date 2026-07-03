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
    attachment: list[AttachmentOutput]
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
    assign_error: str
    attach_error: str
    description: str | None = OutputField(
        example_values=["Jira QA automation ticket description"]
    )
    fields: FieldsOutput
    id: str = OutputField(example_values=["11850"])
    issue_type: str = OutputField(
        cef_types=["jira issue type"], example_values=["Story", "Task"]
    )
    json_fields_error: str
    name: str = OutputField(cef_types=["jira ticket key"], example_values=["MAN-240"])
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
        cef_types=["jira ticket resolution"], example_values=["Unresolved"]
    )
    status: str = OutputField(example_values=["To Do"])
    summary: str = OutputField(example_values=["Jira QA ticket"])


@app.view_handler(template="jira_create_ticket.html")
def _create_ticket_view(
    context: ViewContext, results: list[CreateTicketOutput]
) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


@app.action(
    description="Create a ticket (issue)",
    action_type="generic",
    read_only=False,
    view_handler=_create_ticket_view,
    verbose='The <b>fields</b> parameter is provided for advanced use of the JIRA API. It is passed directly to the &quot;fields&quot; attribute in the JIRA API call. Values in the <b>fields</b> parameter will take precedence over the individual parameters such as <b>summary</b>, <b>description</b>, <b>project_key</b>, <b>issue_type</b>, etc.<br><br>When using the <b>fields</b> parameter, you are required to know how a particular field is inputted. To give a few examples (might differ in your JIRA environment):<ul><li>The <b>description</b> of a ticket can be added as the first level key with a value like { \\"description\\": \\"ticket description\\" }</li><li><b>issuetype</b> needs to be set as a dictionary like { \\"issuetype\\": { \\"name\\": \\"Task\\" } }</li><li><b>priority</b> is set as { \\"priority\\": { \\"name\\": \\"Medium\\" } }</li><li>The <b>project</b> key is set like { \\"project\\": { \\"key\\": \\"SPLUNK_APP\\" } }</li></ul><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><b>Assignee</b> and attachments by <b>vault_id</b> are addressed in a separate call to JIRA made after ticket creation.<br><br>The <b>project_key</b> parameter is case sensitive.<h3>Default Values</h3>Previous versions of the app set default values for <b>priority</b> and <b>issue_type</b>. This caused issues in situations where the default values used by the app were incompatible with the configured values. The app does not set default values anymore. If an optional field below is required by the JIRA environment and it is not provided, JIRA will give an error causing the action to fail.<br><br>This action will pass if a ticket is successfully created, even if it fails to assign the ticket, add an attachment to the ticket, or fill out the custom fields. These failures will be indicated in the result message.<h3>Creating a subtask</h3>The following <b>fields</b> parameter value can be used to create a sub-task, the key is to use the correct <b>issuetype</b>.<pre>{\\"fields\\":{\\"project\\":{\\"key\\":\\"AP\\"},\\"parent\\":{\\"key\\":\\"AP-231\\"},\\"summary\\":\\"Sub-taskofAP-231\\",\\"description\\":\\"Don\'tforgettodothistoo.\\",\\"issuetype\\":{\\"name\\":\\"Sub-Task\\"}}}</pre><h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add an assignee to the Jira ticket using a username for the Jira cloud, we will use the user\'s account_id to add the assignee. Use \'lookup users\' action to find out a user\'s account_id. You can use the [assignee_account_id] action parameter to add an assignee to the Jira ticket for the Jira cloud, and, [assignee] action parameter will be used to add an assignee to the Jira ticket for Jira on-prem.',
)
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
