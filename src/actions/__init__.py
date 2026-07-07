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
from soar_sdk.app import App

from .add_comment import add_comment
from .add_watcher import add_watcher
from .create_ticket import create_ticket
from .delete_ticket import delete_ticket
from .get_attachments import get_attachments
from .get_ticket import get_ticket
from .link_tickets import link_tickets
from .list_projects import ListProjectsSummaryOutput, list_projects
from .list_tickets import ListTicketsSummaryOutput, list_tickets
from .make_request import make_request
from .on_poll import on_poll
from .remove_watcher import remove_watcher
from .search_users import LookupUsersSummaryOutput, lookup_users
from .set_ticket_status import set_status
from .update_ticket import update_ticket

__all__ = ["register_actions"]


def register_actions(app: App) -> App:
    """Register every Jira action on the given App instance.

    Actions are declared as plain functions in their own modules; this is the
    single place they are wired onto the app. The special hooks (make_request,
    on_poll) use their dedicated decorators; everything else goes through
    app.register_action. test_connectivity is registered by the app factory.
    """
    # --- Special SDK hooks ---
    app.make_request()(make_request)
    app.on_poll()(on_poll)

    # --- add comment ---
    app.register_action(
        action=add_comment,
        description="Add a comment to the ticket (issue)",
        action_type="generic",
        read_only=False,
    )

    # --- add watcher ---
    app.register_action(
        action=add_watcher,
        description="Add a user to an issue's watchers list",
        action_type="generic",
        read_only=False,
        verbose="<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add a watcher using username for Jira cloud, we will use a user's account_id to add a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to add a watcher to the Jira ticket for Jira cloud, and, [username] action parameter will be used to add a watcher to the Jira ticket for Jira on-prem.",
    )

    # --- create ticket ---
    app.register_action(
        action=create_ticket,
        description="Create a ticket (issue)",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose='The <b>fields</b> parameter is provided for advanced use of the JIRA API. It is passed directly to the &quot;fields&quot; attribute in the JIRA API call. Values in the <b>fields</b> parameter will take precedence over the individual parameters such as <b>summary</b>, <b>description</b>, <b>project_key</b>, <b>issue_type</b>, etc.<br><br>When using the <b>fields</b> parameter, you are required to know how a particular field is inputted. To give a few examples (might differ in your JIRA environment):<ul><li>The <b>description</b> of a ticket can be added as the first level key with a value like { \\"description\\": \\"ticket description\\" }</li><li><b>issuetype</b> needs to be set as a dictionary like { \\"issuetype\\": { \\"name\\": \\"Task\\" } }</li><li><b>priority</b> is set as { \\"priority\\": { \\"name\\": \\"Medium\\" } }</li><li>The <b>project</b> key is set like { \\"project\\": { \\"key\\": \\"SPLUNK_APP\\" } }</li></ul><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><b>Assignee</b> and attachments by <b>vault_id</b> are addressed in a separate call to JIRA made after ticket creation.<br><br>The <b>project_key</b> parameter is case sensitive.<h3>Default Values</h3>Previous versions of the app set default values for <b>priority</b> and <b>issue_type</b>. This caused issues in situations where the default values used by the app were incompatible with the configured values. The app does not set default values anymore. If an optional field below is required by the JIRA environment and it is not provided, JIRA will give an error causing the action to fail.<br><br>This action will pass if a ticket is successfully created, even if it fails to assign the ticket, add an attachment to the ticket, or fill out the custom fields. These failures will be indicated in the result message.<h3>Creating a subtask</h3>The following <b>fields</b> parameter value can be used to create a sub-task, the key is to use the correct <b>issuetype</b>.<pre>{\\"fields\\":{\\"project\\":{\\"key\\":\\"AP\\"},\\"parent\\":{\\"key\\":\\"AP-231\\"},\\"summary\\":\\"Sub-taskofAP-231\\",\\"description\\":\\"Don\'tforgettodothistoo.\\",\\"issuetype\\":{\\"name\\":\\"Sub-Task\\"}}}</pre><h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add an assignee to the Jira ticket using a username for the Jira cloud, we will use the user\'s account_id to add the assignee. Use \'lookup users\' action to find out a user\'s account_id. You can use the [assignee_account_id] action parameter to add an assignee to the Jira ticket for the Jira cloud, and, [assignee] action parameter will be used to add an assignee to the Jira ticket for Jira on-prem.',
    )

    # --- delete ticket ---
    app.register_action(
        action=delete_ticket,
        description="Delete ticket (issue)",
        action_type="generic",
        read_only=False,
    )

    # --- get attachments ---
    app.register_action(
        action=get_attachments,
        description="Gets specific attachments from a Jira Ticket (issue)",
        action_type="investigate",
        render_as="table",
        verbose="The function will store specific attachments from a given Jira ticket inside the vault.",
    )

    # --- get ticket ---
    app.register_action(
        action=get_ticket,
        description="Get ticket (issue) information",
        action_type="investigate",
        render_as="table",
        verbose="The keys in the <b>action_result.data.*.fields</b> output section of the results can differ based on the JIRA server configuration.",
    )

    # --- link tickets ---
    app.register_action(
        action=link_tickets,
        description="Create a link between two separate tickets",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="If the comment is not added, comment_visibility and comment_visibility_type values will not affect the action result.",
    )

    # --- list projects ---
    app.register_action(
        action=list_projects,
        description="List all projects",
        action_type="investigate",
        render_as="table",
        summary_type=ListProjectsSummaryOutput,
    )

    # --- list tickets ---
    app.register_action(
        action=list_tickets,
        description="Get a list of tickets (issues) in a specified project",
        action_type="investigate",
        render_as="table",
        summary_type=ListTicketsSummaryOutput,
        verbose="The default value for the parameter <b>'start_index'</b> is <b>0</b> and for <b>'max_results'</b> is <b>1000</b>. The maximum number of tickets as specified by the parameter <b>'max_results'</b> will be fetched starting from the index specified by the parameter <b>'start_index'</b>.",
    )

    # --- lookup users ---
    app.register_action(
        action=lookup_users,
        description="Get a list of user resources that match the specified search string",
        action_type="investigate",
        render_as="table",
        summary_type=LookupUsersSummaryOutput,
        verbose="This action will be used to fetch the username of user resources for Jira on-prem and account_id of user resources for Jira cloud. The default value for [max_results] action parameter is <b>1000</b>. The maximum number of users as specified by the parameter [max_results] will be fetched starting from the first.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to search users using username for Jira cloud, we will use the user's display name to search users. You can use the [display_name] action parameter to search users for Jira cloud, and, [username] action parameter will be used to search users for Jira on-prem.",
    )

    # --- remove watcher ---
    app.register_action(
        action=remove_watcher,
        description="Remove a user from an issue's watchers list",
        action_type="generic",
        read_only=False,
        verbose="<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to remove a watcher using username for Jira cloud, we will use a user's account_id to remove a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to remove a watcher from the Jira ticket for Jira cloud, and, [username] action parameter will be used to remove a watcher from the Jira ticket for Jira on-prem.",
    )

    # --- set status ---
    app.register_action(
        action=set_status,
        description="Set ticket (issue) status",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose="In JIRA, the status transition of an issue is determined by the workflow defined for the project. The app will return an error if an un-allowed status transition is attempted. In such cases, the possible statuses are returned based on the issue's current status value.<br>The same is the case for invalid resolutions. Do note that some combinations of status and resolution values might be invalid, even if they are allowed individually.<br>To get valid values to use as input for the parameters:<ul><li>For valid <b>status</b> values:<ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/issue/<i>[jira_issue_key]</i>/transitions</li><li>The returned JSON should contain a list of transitions</li><li>The name field denotes the status that can be set using this action</li></ul></li><li>For valid <b>resolution</b> values: <ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/resolution</li><li>The returned JSON should contain a list of resolutions</li><li>The name field in each resolution denotes the value to be used</li></ul></li></ul>.",
    )

    # --- update ticket ---
    app.register_action(
        action=update_ticket,
        description="Update ticket (issue)",
        action_type="generic",
        read_only=False,
        render_as="table",
        verbose='Update an existing issue with the values specified in the <b>update_fields</b> parameter.<br>The results of the <b>get ticket</b> action may be used to obtain the <b>update_fields</b> parameters, including any custom fields present in the JIRA.</br>The JSON specified in the <b>update_fields</b> parameter requires the keys and the values specified in case-sensitive and double-quotes string format, except in the case of boolean values, which should be either <i>true</i> or <i>false</i> for example:</br>{\\"summary\\": \\"Zeus, multiple action need to be taken\\", \\"description\\": \\"A new summary was added\\"}</br></br>The App supports multiple methods for specifying the input dictionary. Please see <a href=\\"https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#editing-an-issue-examples\\" target=\'_blank\'><b>the Atlassian documentation for the JIRA REST <i>update issue</i> API</b></a> for more information.<br>The following formats can be passed as input: <ul><li>Simple format; Create a dictionary with all the fields that need to be set:<br>{\\"summary\\": \\"Zeus detected on endpoint\\", \\"description\\": \\"Investigate further\\"}</li><li>Using the <i>update</i> key; Some issue fields support operations like <i>remove</i> and <i>add</i>, these operations can be combined to update a ticket: <br>{\\"<b>update</b>\\": {\\"components\\" : [{\\"remove\\" : {\\"name\\" : \\"secondcomponent\\"}}, {\\"add\\" : {\\"name\\" : \\"firstcomponent\\"}}]}}<br>{\\"<b>update</b>\\": {\\"comment\\": [{\\"add\\": {\\"body\\": \\"test comment update\\"}}]}} </li><li>Using the <i>fields</i> key;</br>{\\"<b>fields</b>\\":{\\"labels\\" : [\\"FIRSTLABEL\\"]}}</li></ul></br>The app supports updating custom fields; depending on the custom field type, some operations might not be available. Review the <b>jira_app</b> playbook for examples.<br><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><br>This action requires that either the <b>update_fields</b> parameter or the <b>vault_id</b> parameter is filled out. The action will fail if it either unsuccessfully attempts to add the attachment to the ticket or update the fields on the ticket.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to update fields related to user resources in the Jira ticket using username for Jira cloud, we will use the user\'s account_id to update fields related to user resources. Use \'lookup users\' action to find out user\'s account_id. Use \'get ticket\' action results to obtain the [update_fields] parameters. Please find out below-mentioned examples for the [update_fields] parameter which is related to user resources.<ul><li>Add assignee to the Jira ticket for Jira on-prem:<br>{\\"fields\\":{\\"assignee\\" : {\\"name\\": \\"username\\"}}}</li><li>Add assignee to the Jira ticket for Jira cloud:<br>{\\"fields\\":{\\"assignee\\" : {\\"accountId\\": \\"6d1ef6xy52z7360c267f27bb\\"}}}</li></ul>.',
    )

    return app
