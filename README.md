# Jira

Publisher: Splunk <br>
Connector Version: 4.1.0 <br>
Product Vendor: Atlassian <br>
Product Name: Jira <br>
Minimum Product Version: 7.0.0

This app integrates with JIRA to perform several ticket management actions

### Configuration variables

This table lists the configuration variables required to operate Jira. These variables are specified when configuring a Jira asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device_url** | required | string | Device URL including the port, e.g. https://myjira.enterprise.com:8080 |
**verify_server_cert** | optional | boolean | Verify server certificate |
**username** | required | string | Jira Cloud email address (or on-prem username) for Basic Auth |
**password** | required | password | Jira Cloud API token (or on-prem password) for Basic Auth |
**project_key** | optional | string | Project key to ingest tickets (issues) from |
**query** | optional | string | Additional parameters to query for during ingestion in JQL |
**first_run_max_tickets** | optional | numeric | Maximum tickets (issues) to poll first time |
**max_tickets** | optional | numeric | Maximum tickets (issues) for scheduled polling |
**custom_fields** | optional | string | JSON formatted list of names of custom fields (case-sensitive) to be ingested |
**timezone** | optional | timezone | Jira instance timezone used to format the JQL 'updated>=' filter during ingestion. Leave blank to auto-detect from the Jira server (recommended). Set only if the auto-detected value is wrong. Must be a valid IANA timezone string, e.g. 'America/New_York'. |

### Supported Actions

[add comment](#action-add-comment) - Add a comment to the ticket (issue) <br>
[add watcher](#action-add-watcher) - Add a user to an issue's watchers list <br>
[create ticket](#action-create-ticket) - Create a ticket (issue) <br>
[delete ticket](#action-delete-ticket) - Delete ticket (issue) <br>
[get attachments](#action-get-attachments) - Gets specific attachments from a Jira Ticket (issue) <br>
[get ticket](#action-get-ticket) - Get ticket (issue) information <br>
[link tickets](#action-link-tickets) - Create a link between two separate tickets <br>
[list projects](#action-list-projects) - List all projects <br>
[list tickets](#action-list-tickets) - Get a list of tickets (issues) in a specified project <br>
[make request](#action-make-request) - Make a custom REST API call to Jira.

Use this action to call any Jira REST API endpoint not covered by the other actions.
The endpoint parameter is the path after the base device URL,
e.g. rest/api/2/issue/PROJ-1 or rest/api/2/project.
The full response body is returned as a string in response_body. <br>
[remove watcher](#action-remove-watcher) - Remove a user from an issue's watchers list <br>
[lookup users](#action-lookup-users) - Get a list of user resources that match the specified search string <br>
[set status](#action-set-status) - Set ticket (issue) status <br>
[update ticket](#action-update-ticket) - Update ticket (issue) <br>
[on poll](#action-on-poll) - Ingest Jira tickets as SOAR containers with field, comment, and attachment artifacts.

State is stored in `asset.ingest_state` (SDK-managed, encrypted at rest):

- `first_run` (bool): True until the first scheduled poll completes.
- `last_time` (int): UTC epoch seconds of the `updated` field of the last ingested issue.

Three execution modes (mirrors legacy connector):

- Poll Now (params.is_manual_poll()): uses params.container_count as limit; never writes state.
- First Run (state["first_run"] == True): uses asset.first_run_max_tickets; no time filter.
- Scheduled (ongoing): uses asset.max_tickets; adds `updated>="..."` JQL filter. <br>
  [test connectivity](#action-test-connectivity) - test connectivity

## action: 'add comment'

Add a comment to the ticket (issue)

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Issue ID | string | `jira ticket key` |
**comment** | required | Comment to add | string | |
**internal** | optional | Whether comment should be internal only or not in Jira Service Desk (if the value is not provided, it will internally be treated as 'false') | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.comment | string | | |
action_result.parameter.internal | boolean | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'add watcher'

Add a user to an issue's watchers list

Type: **generic** <br>
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add a watcher using username for Jira cloud, we will use a user's account_id to add a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to add a watcher to the Jira ticket for Jira cloud, and, [username] action parameter will be used to add a watcher to the Jira ticket for Jira on-prem.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Issue ID | string | `jira ticket key` |
**username** | optional | Username of the user to add to the watchers list (required for Jira on-prem) | string | `user name` |
**user_account_id** | optional | Account ID of the user to add to the watchers list (required for Jira cloud) | string | `jira user account id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.username | string | `user name` | |
action_result.parameter.user_account_id | string | `jira user account id` | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'create ticket'

Create a ticket (issue)

Type: **generic** <br>
Read only: **False**

The <b>fields</b> parameter is provided for advanced use of the JIRA API. It is passed directly to the "fields" attribute in the JIRA API call. Values in the <b>fields</b> parameter will take precedence over the individual parameters such as <b>summary</b>, <b>description</b>, <b>project_key</b>, <b>issue_type</b>, etc.<br><br>When using the <b>fields</b> parameter, you are required to know how a particular field is inputted. To give a few examples (might differ in your JIRA environment):<ul><li>The <b>description</b> of a ticket can be added as the first level key with a value like { \\"description\\": \\"ticket description\\" }</li><li><b>issuetype</b> needs to be set as a dictionary like { \\"issuetype\\": { \\"name\\": \\"Task\\" } }</li><li><b>priority</b> is set as { \\"priority\\": { \\"name\\": \\"Medium\\" } }</li><li>The <b>project</b> key is set like { \\"project\\": { \\"key\\": \\"SPLUNK_APP\\" } }</li></ul><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><b>Assignee</b> and attachments by <b>vault_id</b> are addressed in a separate call to JIRA made after ticket creation.<br><br>The <b>project_key</b> parameter is case sensitive.<h3>Default Values</h3>Previous versions of the app set default values for <b>priority</b> and <b>issue_type</b>. This caused issues in situations where the default values used by the app were incompatible with the configured values. The app does not set default values anymore. If an optional field below is required by the JIRA environment and it is not provided, JIRA will give an error causing the action to fail.<br><br>This action will pass if a ticket is successfully created, even if it fails to assign the ticket, add an attachment to the ticket, or fill out the custom fields. These failures will be indicated in the result message.<h3>Creating a subtask</h3>The following <b>fields</b> parameter value can be used to create a sub-task, the key is to use the correct <b>issuetype</b>.<pre>{\\"fields\\":{\\"project\\":{\\"key\\":\\"AP\\"},\\"parent\\":{\\"key\\":\\"AP-231\\"},\\"summary\\":\\"Sub-taskofAP-231\\",\\"description\\":\\"Don'tforgettodothistoo.\\",\\"issuetype\\":{\\"name\\":\\"Sub-Task\\"}}}</pre><h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add an assignee to the Jira ticket using a username for the Jira cloud, we will use the user's account_id to add the assignee. Use 'lookup users' action to find out a user's account_id. You can use the [assignee_account_id] action parameter to add an assignee to the Jira ticket for the Jira cloud, and, [assignee] action parameter will be used to add an assignee to the Jira ticket for Jira on-prem.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project_key** | required | Project key to add the issue to (case-sensitive) | string | `jira project key` |
**summary** | required | Summary of the issue | string | |
**description** | optional | Description of the issue | string | |
**issue_type** | required | Type of the issue (case-sensitive) | string | `jira issue type` |
**priority** | optional | Priority of the issue | string | `jira ticket priority` |
**assignee** | optional | Assignee username (required for Jira on-prem, assign required permissions) | string | `user name` |
**assignee_account_id** | optional | Assignee user account ID (required for Jira cloud, assign required permissions) | string | `jira user account id` |
**fields** | optional | JSON containing field values | string | |
**vault_id** | optional | Vault ID of attachment | string | `vault id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.project_key | string | `jira project key` | |
action_result.parameter.summary | string | | |
action_result.parameter.description | string | | |
action_result.parameter.issue_type | string | `jira issue type` | |
action_result.parameter.priority | string | `jira ticket priority` | |
action_result.parameter.assignee | string | `user name` | |
action_result.parameter.assignee_account_id | string | `jira user account id` | |
action_result.parameter.fields | string | | |
action_result.parameter.vault_id | string | `vault id` | |
action_result.data.\*.assign_error | string | | |
action_result.data.\*.attach_error | string | | |
action_result.data.\*.description | string | | Jira QA automation ticket description |
action_result.data.\*.fields.Epic Link | string | | |
action_result.data.\*.fields.Epic Name | string | | Test epic |
action_result.data.\*.fields.Severity | string | | |
action_result.data.\*.fields.Sprint | string | | |
action_result.data.\*.fields.aggregateprogress.progress | numeric | | 0 |
action_result.data.\*.fields.aggregateprogress.total | numeric | | 0 |
action_result.data.\*.fields.aggregatetimeestimate | string | | |
action_result.data.\*.fields.aggregatetimeoriginalestimate | string | | |
action_result.data.\*.fields.aggregatetimespent | string | | |
action_result.data.\*.fields.assignee.accountId | string | `jira user account id` | 5d2ef6ab52a8370c567f27bb |
action_result.data.\*.fields.assignee.accountType | string | | atlassian |
action_result.data.\*.fields.assignee.active | boolean | | True False |
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.fields.assignee.emailAddress | string | `email` | abc@domain.com |
action_result.data.\*.fields.assignee.key | string | | test |
action_result.data.\*.fields.assignee.name | string | `user name` | test |
action_result.data.\*.fields.assignee.self | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.timeZone | string | | |
action_result.data.\*.fields.attachment.\*.author.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.attachment.\*.author.accountType | string | | atlassian |
action_result.data.\*.fields.attachment.\*.author.active | boolean | | True False |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.attachment.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.attachment.\*.author.key | string | | admin |
action_result.data.\*.fields.attachment.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.attachment.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.attachment.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.attachment.\*.content | string | `url` | http://jira.instance.ip/secure/attachment/10403/Add+Comment.png |
action_result.data.\*.fields.attachment.\*.created | string | | 2018-09-19T18:15:01.060-0700 |
action_result.data.\*.fields.attachment.\*.filename | string | | Add Comment.png |
action_result.data.\*.fields.attachment.\*.id | string | | 10403 |
action_result.data.\*.fields.attachment.\*.mimeType | string | | image/png |
action_result.data.\*.fields.attachment.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/attachment/10403 |
action_result.data.\*.fields.attachment.\*.size | numeric | | 97613 |
action_result.data.\*.fields.attachment.\*.thumbnail | string | `url` | http://jira.instance.ip/secure/thumbnail/10403/\_thumb_10403.png |
action_result.data.\*.fields.comment.comments.\*.author.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.author.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.body | string | | This is a sample testing body for the comment |
action_result.data.\*.fields.comment.comments.\*.created | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.id | string | | 10004 |
action_result.data.\*.fields.comment.comments.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.updated | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.visibility.type | string | | group role |
action_result.data.\*.fields.comment.comments.\*.visibility.value | string | | jira-software-users |
action_result.data.\*.fields.comment.maxResults | numeric | | 7 |
action_result.data.\*.fields.comment.startAt | numeric | | 0 |
action_result.data.\*.fields.comment.total | numeric | | 7 |
action_result.data.\*.fields.created | string | | 2018-09-25T06:31:58.854-0700 |
action_result.data.\*.fields.creator.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.creator.accountType | string | | atlassian |
action_result.data.\*.fields.creator.active | boolean | | True False |
action_result.data.\*.fields.creator.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.creator.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.creator.key | string | | admin |
action_result.data.\*.fields.creator.name | string | `user name` | admin |
action_result.data.\*.fields.creator.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.creator.timeZone | string | | UTC |
action_result.data.\*.fields.description | string | | Jira QA automation ticket description |
action_result.data.\*.fields.duedate | string | | |
action_result.data.\*.fields.environment | string | | |
action_result.data.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.lastViewed | string | | |
action_result.data.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.progress.progress | numeric | | 0 |
action_result.data.\*.fields.progress.total | numeric | | 0 |
action_result.data.\*.fields.project.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.id | string | | 10100 |
action_result.data.\*.fields.project.key | string | `jira project key` | MAN |
action_result.data.\*.fields.project.name | string | | TestProject |
action_result.data.\*.fields.project.projectCategory.description | string | | test |
action_result.data.\*.fields.project.projectCategory.id | string | | 10000 |
action_result.data.\*.fields.project.projectCategory.name | string | | QA-Team |
action_result.data.\*.fields.project.projectCategory.self | string | | https://testlab.atlassian.net/rest/api/2/projectCategory/10000 |
action_result.data.\*.fields.project.projectTypeKey | string | | software |
action_result.data.\*.fields.project.self | string | `url` | http://jira.instance.ip/rest/api/2/project/10100 |
action_result.data.\*.fields.project.simplified | boolean | | True False |
action_result.data.\*.fields.reporter.accountType | string | | atlassian |
action_result.data.\*.fields.reporter.active | boolean | | True False |
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.reporter.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.reporter.key | string | | admin |
action_result.data.\*.fields.reporter.name | string | `user name` | admin |
action_result.data.\*.fields.reporter.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.reporter.timeZone | string | | UTC |
action_result.data.\*.fields.resolution | string | | |
action_result.data.\*.fields.resolutiondate | string | | 2018-10-03T03:42:10.912-0700 |
action_result.data.\*.fields.security | string | | |
action_result.data.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.statuscategorychangedate | string | | 2019-07-22T22:43:07.771-0700 |
action_result.data.\*.fields.summary | string | | Jira QA ticket |
action_result.data.\*.fields.timeestimate | string | | |
action_result.data.\*.fields.timeoriginalestimate | string | | |
action_result.data.\*.fields.timespent | string | | |
action_result.data.\*.fields.updated | string | | 2018-09-25T06:31:58.854-0700 |
action_result.data.\*.fields.votes.hasVoted | boolean | | True False |
action_result.data.\*.fields.votes.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/votes |
action_result.data.\*.fields.votes.votes | numeric | | 0 |
action_result.data.\*.fields.watches.isWatching | boolean | | True False |
action_result.data.\*.fields.watches.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers |
action_result.data.\*.fields.watches.watchCount | numeric | | 1 |
action_result.data.\*.fields.worklog.maxResults | numeric | | 20 |
action_result.data.\*.fields.worklog.startAt | numeric | | 0 |
action_result.data.\*.fields.worklog.total | numeric | | 0 |
action_result.data.\*.fields.workratio | numeric | | -1 |
action_result.data.\*.id | string | | 11850 |
action_result.data.\*.issue_type | string | `jira issue type` | Story Task |
action_result.data.\*.json_fields_error | string | | |
action_result.data.\*.name | string | `jira ticket key` | MAN-240 |
action_result.data.\*.priority | string | `jira ticket priority` | Medium |
action_result.data.\*.project_key | string | `jira project key` | MAN |
action_result.data.\*.reporter | string | `jira user display name` | Test Admin |
action_result.data.\*.resolution | string | `jira ticket resolution` | Unresolved |
action_result.data.\*.status | string | | To Do |
action_result.data.\*.summary | string | | Jira QA ticket |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'delete ticket'

Delete ticket (issue)

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Issue ID | string | `jira ticket key` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get attachments'

Gets specific attachments from a Jira Ticket (issue)

Type: **investigate** <br>
Read only: **True**

The function will store specific attachments from a given Jira ticket inside the vault.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | The key of the Jira issue | string | `jira ticket key` |
**retrieve_all** | optional | If this is set to true all attachments will be retrieved from the issue (if the value is not provided, it will internally be treated as 'false') | boolean | |
**container_id** | required | The Container ID to associate the file with | string | |
**extension_filter** | optional | Comma-separated list of file extensions to be returned from the issue | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.retrieve_all | boolean | | |
action_result.parameter.container_id | string | | |
action_result.parameter.extension_filter | string | | |
action_result.data.\*.container | numeric | | 2446 |
action_result.data.\*.hash | string | `md5` | 9c03244555e41685dc5f03ec7d9de1c6db26c318 |
action_result.data.\*.id | numeric | | 501 |
action_result.data.\*.message | string | | success |
action_result.data.\*.size | numeric | | 231003 |
action_result.data.\*.succeeded | boolean | | True False |
action_result.data.\*.vault_id | string | `vault id` | 9c03244555e41685dc5f03ec7d9de1c6db26c318 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get ticket'

Get ticket (issue) information

Type: **investigate** <br>
Read only: **True**

The keys in the <b>action_result.data.\*.fields</b> output section of the results can differ based on the JIRA server configuration.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Ticket (issue) key | string | `jira ticket key` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.data.\*.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.Epic Link | string | | |
action_result.data.\*.fields.Sprint | string | | com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97\[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1\] |
action_result.data.\*.fields.aggregateprogress.progress | numeric | | 0 |
action_result.data.\*.fields.aggregateprogress.total | numeric | | 0 |
action_result.data.\*.fields.aggregatetimeestimate | numeric | | |
action_result.data.\*.fields.aggregatetimeoriginalestimate | numeric | | |
action_result.data.\*.fields.aggregatetimespent | numeric | | |
action_result.data.\*.fields.assignee.accountId | string | `jira user account id` | 5d2ef6ab52a8370c567f27bb |
action_result.data.\*.fields.assignee.accountType | string | | atlassian |
action_result.data.\*.fields.assignee.active | boolean | | True False |
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.fields.assignee.emailAddress | string | `email` | abc@domain.com |
action_result.data.\*.fields.assignee.key | string | | test |
action_result.data.\*.fields.assignee.name | string | `user name` | test |
action_result.data.\*.fields.assignee.self | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.timeZone | string | | |
action_result.data.\*.fields.attachment.\*.author.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.attachment.\*.author.accountType | string | | atlassian |
action_result.data.\*.fields.attachment.\*.author.active | boolean | | True False |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.attachment.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.attachment.\*.author.key | string | | admin |
action_result.data.\*.fields.attachment.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.attachment.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.attachment.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.attachment.\*.content | string | `url` | http://jira.instance.ip/secure/attachment/10403/Add+Comment.png |
action_result.data.\*.fields.attachment.\*.created | string | | 2018-09-19T18:15:01.060-0700 |
action_result.data.\*.fields.attachment.\*.filename | string | | Add Comment.png |
action_result.data.\*.fields.attachment.\*.id | string | | 10403 |
action_result.data.\*.fields.attachment.\*.mimeType | string | | image/png |
action_result.data.\*.fields.attachment.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/attachment/10403 |
action_result.data.\*.fields.attachment.\*.size | numeric | | 97613 |
action_result.data.\*.fields.attachment.\*.thumbnail | string | `url` | http://jira.instance.ip/secure/thumbnail/10403/\_thumb_10403.png |
action_result.data.\*.fields.comment.comments.\*.author.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.author.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.body | string | | This is a sample testing body for the comment |
action_result.data.\*.fields.comment.comments.\*.created | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.id | string | | 10004 |
action_result.data.\*.fields.comment.comments.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.updated | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.visibility.type | string | | group role |
action_result.data.\*.fields.comment.comments.\*.visibility.value | string | | jira-software-users |
action_result.data.\*.fields.comment.maxResults | numeric | | 7 |
action_result.data.\*.fields.comment.startAt | numeric | | 0 |
action_result.data.\*.fields.comment.total | numeric | | 7 |
action_result.data.\*.fields.components.\*.id | string | | 10104 |
action_result.data.\*.fields.components.\*.name | string | | comp_test1 |
action_result.data.\*.fields.components.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/component/10104 |
action_result.data.\*.fields.created | string | | 2016-03-13T13:22:08.254-0700 |
action_result.data.\*.fields.creator.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.creator.accountType | string | | atlassian |
action_result.data.\*.fields.creator.active | boolean | | True False |
action_result.data.\*.fields.creator.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.creator.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.creator.key | string | | admin |
action_result.data.\*.fields.creator.name | string | `user name` | admin |
action_result.data.\*.fields.creator.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.creator.timeZone | string | | UTC |
action_result.data.\*.fields.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.duedate | string | | |
action_result.data.\*.fields.environment | string | | above ground |
action_result.data.\*.fields.fixVersions.\*.archived | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.id | string | | 10000 |
action_result.data.\*.fields.fixVersions.\*.name | string | | 1.0 |
action_result.data.\*.fields.fixVersions.\*.released | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.issuelinks.\*.id | string | | 10615 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string | | 21237 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string | | SPOL-133 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string | | http://jira.instance.ip/rest/api/2/issue/21237 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string | | 11849 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string | `jira ticket key` | ZEP-14 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/11849 |
action_result.data.\*.fields.issuelinks.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLink/10615 |
action_result.data.\*.fields.issuelinks.\*.type.id | string | | 10000 |
action_result.data.\*.fields.issuelinks.\*.type.inward | string | | is blocked by |
action_result.data.\*.fields.issuelinks.\*.type.name | string | | Blocks |
action_result.data.\*.fields.issuelinks.\*.type.outward | string | | blocks |
action_result.data.\*.fields.issuelinks.\*.type.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLinkType/10000 |
action_result.data.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.labels.\* | string | | |
action_result.data.\*.fields.lastViewed | string | | 2018-09-20T23:54:50.643-0700 |
action_result.data.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.progress.progress | numeric | | 0 |
action_result.data.\*.fields.progress.total | numeric | | 0 |
action_result.data.\*.fields.project.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.id | string | | 10100 |
action_result.data.\*.fields.project.key | string | `jira project key` | MAN |
action_result.data.\*.fields.project.name | string | | TestProject |
action_result.data.\*.fields.project.projectCategory.description | string | | test |
action_result.data.\*.fields.project.projectCategory.id | string | | 10000 |
action_result.data.\*.fields.project.projectCategory.name | string | | QA-Team |
action_result.data.\*.fields.project.projectCategory.self | string | | https://testlab.atlassian.net/rest/api/2/projectCategory/10000 |
action_result.data.\*.fields.project.projectTypeKey | string | | software |
action_result.data.\*.fields.project.self | string | `url` | http://jira.instance.ip/rest/api/2/project/10100 |
action_result.data.\*.fields.project.simplified | boolean | | True False |
action_result.data.\*.fields.reporter.accountType | string | | atlassian |
action_result.data.\*.fields.reporter.active | boolean | | True False |
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.reporter.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.reporter.key | string | | admin |
action_result.data.\*.fields.reporter.name | string | `user name` | admin |
action_result.data.\*.fields.reporter.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.reporter.timeZone | string | | UTC |
action_result.data.\*.fields.resolution.description | string | | Work has been completed on this issue |
action_result.data.\*.fields.resolution.id | string | | 10000 |
action_result.data.\*.fields.resolution.name | string | `jira ticket resolution` | Done |
action_result.data.\*.fields.resolution.self | string | `url` | http://jira.instance.ip/rest/api/2/resolution/10000 |
action_result.data.\*.fields.resolutiondate | string | | 2018-09-20T19:02:38.646-0700 |
action_result.data.\*.fields.security | string | | |
action_result.data.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.statuscategorychangedate | string | | 2019-07-22T22:43:07.771-0700 |
action_result.data.\*.fields.summary | string | | Sample summary |
action_result.data.\*.fields.timeestimate | numeric | | |
action_result.data.\*.fields.timeoriginalestimate | numeric | | |
action_result.data.\*.fields.timespent | numeric | | |
action_result.data.\*.fields.updated | string | | 2018-09-25T06:21:27.802-0700 |
action_result.data.\*.fields.versions.\*.archived | boolean | | True False |
action_result.data.\*.fields.versions.\*.id | string | | 10000 |
action_result.data.\*.fields.versions.\*.name | string | | 1.0 |
action_result.data.\*.fields.versions.\*.released | boolean | | True False |
action_result.data.\*.fields.versions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.votes.hasVoted | boolean | | True False |
action_result.data.\*.fields.votes.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/votes |
action_result.data.\*.fields.votes.votes | numeric | | 0 |
action_result.data.\*.fields.watches.isWatching | boolean | | True False |
action_result.data.\*.fields.watches.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers |
action_result.data.\*.fields.watches.watchCount | numeric | | 1 |
action_result.data.\*.fields.worklog.maxResults | numeric | | 20 |
action_result.data.\*.fields.worklog.startAt | numeric | | 0 |
action_result.data.\*.fields.worklog.total | numeric | | 0 |
action_result.data.\*.fields.workratio | numeric | | -1 |
action_result.data.\*.id | string | | 10246 |
action_result.data.\*.issue_type | string | `jira issue type` | Defect |
action_result.data.\*.name | string | `jira ticket key` | MAN-1 |
action_result.data.\*.priority | string | `jira ticket priority` | Medium |
action_result.data.\*.project_key | string | `jira project key` | MAN |
action_result.data.\*.reporter | string | `jira user display name` | Test Admin |
action_result.data.\*.resolution | string | `jira ticket resolution` | Done |
action_result.data.\*.status | string | | Done |
action_result.data.\*.summary | string | | Sample summary |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'link tickets'

Create a link between two separate tickets

Type: **generic** <br>
Read only: **False**

If the comment is not added, comment_visibility and comment_visibility_type values will not affect the action result.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**from_id** | required | First ticket (issue) key | string | `jira ticket key` |
**to_id** | required | Second ticket (issue) key | string | `jira ticket key` |
**link_type** | required | Type of link to create | string | |
**comment** | optional | Comment to add | string | |
**comment_visibility_type** | optional | How to limit the comment visibility | string | |
**comment_visibility_name** | optional | Name of group/role able to see the comment | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.from_id | string | `jira ticket key` | |
action_result.parameter.to_id | string | `jira ticket key` | |
action_result.parameter.link_type | string | | |
action_result.parameter.comment | string | | |
action_result.parameter.comment_visibility_type | string | | |
action_result.parameter.comment_visibility_name | string | | |
action_result.data.\*.result | string | | success failed |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list projects'

List all projects

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.data.\*.id | string | | 10207 |
action_result.data.\*.name | string | | Access Uplift Alerts |
action_result.data.\*.project_key | string | `jira project key` | AUA |
action_result.summary.total_projects | numeric | | 5 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'list tickets'

Get a list of tickets (issues) in a specified project

Type: **investigate** <br>
Read only: **True**

The default value for the parameter <b>'start_index'</b> is <b>0</b> and for <b>'max_results'</b> is <b>1000</b>. The maximum number of tickets as specified by the parameter <b>'max_results'</b> will be fetched starting from the index specified by the parameter <b>'start_index'</b>.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project_key** | optional | Project key to list the tickets (issues) of | string | `jira project key` |
**query** | optional | Additional parameters to query for in JQL | string | |
**start_index** | optional | Start index of the list | numeric | |
**max_results** | optional | Maximum number of issues to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.project_key | string | `jira project key` | |
action_result.parameter.query | string | | |
action_result.parameter.start_index | numeric | | |
action_result.parameter.max_results | numeric | | |
action_result.data.\*.description | string | `url` | This is a sample testing description |
action_result.data.\*.fields.aggregateprogress.progress | numeric | | 0 |
action_result.data.\*.fields.aggregateprogress.total | numeric | | 0 |
action_result.data.\*.fields.aggregatetimeestimate | string | | |
action_result.data.\*.fields.aggregatetimeoriginalestimate | string | | |
action_result.data.\*.fields.aggregatetimespent | string | | |
action_result.data.\*.fields.assignee.accountId | string | `jira user account id` | 5d2ef6ab52a8370c567f27bb |
action_result.data.\*.fields.assignee.accountType | string | | atlassian |
action_result.data.\*.fields.assignee.active | boolean | | True False |
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.fields.assignee.emailAddress | string | `email` | abc@domain.com |
action_result.data.\*.fields.assignee.key | string | | test |
action_result.data.\*.fields.assignee.name | string | `user name` | test |
action_result.data.\*.fields.assignee.self | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.timeZone | string | | |
action_result.data.\*.fields.attachment.\*.author.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.attachment.\*.author.accountType | string | | atlassian |
action_result.data.\*.fields.comment.comments.\*.visibility.type | string | | group role |
action_result.data.\*.fields.comment.comments.\*.visibility.value | string | | jira-software-users |
action_result.data.\*.fields.comment.maxResults | numeric | | |
action_result.data.\*.fields.comment.startAt | numeric | | |
action_result.data.\*.fields.comment.total | numeric | | |
action_result.data.\*.fields.created | string | | 2018-09-23T19:40:35.000-0700 |
action_result.data.\*.fields.creator.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.creator.accountType | string | | atlassian |
action_result.data.\*.fields.creator.active | boolean | | True False |
action_result.data.\*.fields.creator.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.creator.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.creator.key | string | | admin |
action_result.data.\*.fields.creator.name | string | `user name` | admin |
action_result.data.\*.fields.creator.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.creator.timeZone | string | | UTC |
action_result.data.\*.fields.description | string | `url` | This is a sample testing description |
action_result.data.\*.fields.duedate | string | | |
action_result.data.\*.fields.environment | string | | |
action_result.data.\*.fields.issuelinks.\*.id | string | | 10615 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string | | 11849 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string | `jira ticket key` | ZEP-14 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/11849 |
action_result.data.\*.fields.issuelinks.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLink/10615 |
action_result.data.\*.fields.issuelinks.\*.type.id | string | | 10000 |
action_result.data.\*.fields.issuelinks.\*.type.inward | string | | is blocked by |
action_result.data.\*.fields.issuelinks.\*.type.name | string | | Blocks |
action_result.data.\*.fields.issuelinks.\*.type.outward | string | | blocks |
action_result.data.\*.fields.issuelinks.\*.type.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLinkType/10000 |
action_result.data.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.lastViewed | string | | 2018-09-23T22:28:12.754-0700 |
action_result.data.\*.fields.parent.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.parent.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.parent.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.parent.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.parent.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.parent.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.parent.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.parent.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.parent.fields.priority.id | string | | 3 |
action_result.data.\*.fields.parent.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.parent.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.parent.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.parent.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.parent.fields.status.id | string | | 10001 |
action_result.data.\*.fields.parent.fields.status.name | string | | Done |
action_result.data.\*.fields.parent.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.parent.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.parent.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.parent.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.parent.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.parent.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.parent.fields.summary | string | | Sample summary |
action_result.data.\*.fields.parent.id | string | | 11811 |
action_result.data.\*.fields.parent.key | string | | PHANINCIDE-315 |
action_result.data.\*.fields.parent.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/11811 |
action_result.data.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.progress.progress | numeric | | 0 |
action_result.data.\*.fields.progress.total | numeric | | 0 |
action_result.data.\*.fields.project.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.id | string | | 10100 |
action_result.data.\*.fields.project.key | string | `jira project key` | MAN |
action_result.data.\*.fields.project.name | string | | TestProject |
action_result.data.\*.fields.project.projectCategory.description | string | | test |
action_result.data.\*.fields.project.projectCategory.id | string | | 10000 |
action_result.data.\*.fields.project.projectCategory.name | string | | QA-Team |
action_result.data.\*.fields.project.projectCategory.self | string | | https://testlab.atlassian.net/rest/api/2/projectCategory/10000 |
action_result.data.\*.fields.project.projectTypeKey | string | | software |
action_result.data.\*.fields.project.self | string | `url` | http://jira.instance.ip/rest/api/2/project/10100 |
action_result.data.\*.fields.project.simplified | boolean | | True False |
action_result.data.\*.fields.reporter.accountType | string | | atlassian |
action_result.data.\*.fields.reporter.active | boolean | | True False |
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.reporter.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.reporter.key | string | | admin |
action_result.data.\*.fields.reporter.name | string | `user name` | admin |
action_result.data.\*.fields.reporter.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.reporter.timeZone | string | | UTC |
action_result.data.\*.fields.resolution.description | string | | Work has been completed on this issue |
action_result.data.\*.fields.resolution.id | string | | 10000 |
action_result.data.\*.fields.resolution.name | string | `jira ticket resolution` | Done |
action_result.data.\*.fields.resolution.self | string | `url` | http://jira.instance.ip/rest/api/2/resolution/10000 |
action_result.data.\*.fields.resolutiondate | string | | 2018-09-23T19:40:35.000-0700 |
action_result.data.\*.fields.security | string | | |
action_result.data.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.statuscategorychangedate | string | | 2019-07-22T22:43:07.771-0700 |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.subtasks.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.subtasks.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.subtasks.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.subtasks.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.subtasks.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.subtasks.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.subtasks.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.subtasks.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.subtasks.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.subtasks.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.subtasks.\*.fields.summary | string | | Sample summary |
action_result.data.\*.fields.subtasks.\*.id | string | | 11839 |
action_result.data.\*.fields.subtasks.\*.key | string | | PHANINCIDE-316 |
action_result.data.\*.fields.subtasks.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/11839 |
action_result.data.\*.fields.summary | string | | Sub-taskofBigTask |
action_result.data.\*.fields.timeestimate | string | | |
action_result.data.\*.fields.timeoriginalestimate | string | | |
action_result.data.\*.fields.timespent | string | | |
action_result.data.\*.fields.updated | string | | 2018-09-23T22:28:12.000-0700 |
action_result.data.\*.fields.votes.hasVoted | boolean | | True False |
action_result.data.\*.fields.votes.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/votes |
action_result.data.\*.fields.votes.votes | numeric | | 0 |
action_result.data.\*.fields.watches.isWatching | boolean | | True False |
action_result.data.\*.fields.watches.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers |
action_result.data.\*.fields.watches.watchCount | numeric | | 1 |
action_result.data.\*.fields.worklog.maxResults | numeric | | |
action_result.data.\*.fields.worklog.startAt | numeric | | |
action_result.data.\*.fields.worklog.total | numeric | | |
action_result.data.\*.fields.workratio | numeric | | -1 |
action_result.data.\*.id | string | | 11840 |
action_result.data.\*.issue_type | string | `jira issue type` | Sub-Task |
action_result.data.\*.name | string | `jira ticket key` | PHANINCIDE-317 |
action_result.data.\*.priority | string | `jira ticket priority` | Medium |
action_result.data.\*.project_key | string | `jira project key` | PRJ |
action_result.data.\*.reporter | string | `jira user display name` | Test Admin |
action_result.data.\*.resolution | string | `jira ticket resolution` | Unresolved |
action_result.data.\*.status | string | | To Do |
action_result.data.\*.summary | string | | Sub-taskofBigTask |
action_result.summary.total_issues | numeric | | 10 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'make request'

Make a custom REST API call to Jira.

Use this action to call any Jira REST API endpoint not covered by the other actions.
The endpoint parameter is the path after the base device URL,
e.g. rest/api/2/issue/PROJ-1 or rest/api/2/project.
The full response body is returned as a string in response_body.

Type: **generic** <br>
Read only: **False**

'make request' action for the app. Used to handle arbitrary HTTP requests with the app's asset

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**http_method** | required | The HTTP method to use for the request. | string | |
**endpoint** | required | The endpoint to send the request to. | string | |
**headers** | optional | The headers to send with the request (JSON object). An example is {'Content-Type': 'application/json'} | string | |
**query_parameters** | optional | Parameters to append to the URL (JSON object or query string). An example is ?key=value&key2=value2 | string | |
**body** | optional | The body to send with the request (JSON object). An example is {'key': 'value', 'key2': 'value2'} | string | |
**timeout** | optional | The timeout for the request in seconds. | numeric | |
**verify_ssl** | optional | Whether to verify the SSL certificate. Default is False. | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.http_method | string | | |
action_result.parameter.endpoint | string | | |
action_result.parameter.headers | string | | |
action_result.parameter.query_parameters | string | | |
action_result.parameter.body | string | | |
action_result.parameter.timeout | numeric | | |
action_result.parameter.verify_ssl | boolean | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"key": "value"} |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'remove watcher'

Remove a user from an issue's watchers list

Type: **generic** <br>
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to remove a watcher using username for Jira cloud, we will use a user's account_id to remove a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to remove a watcher from the Jira ticket for Jira cloud, and, [username] action parameter will be used to remove a watcher from the Jira ticket for Jira on-prem.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Issue ID | string | `jira ticket key` |
**username** | optional | Username of the user to remove from watchers list (required for Jira on-prem) | string | `user name` |
**user_account_id** | optional | Account ID of the user to remove from the watchers list (required for Jira cloud) | string | `jira user account id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.username | string | `user name` | |
action_result.parameter.user_account_id | string | `jira user account id` | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'lookup users'

Get a list of user resources that match the specified search string

Type: **investigate** <br>
Read only: **True**

This action will be used to fetch the username of user resources for Jira on-prem and account_id of user resources for Jira cloud. The default value for [max_results] action parameter is <b>1000</b>. The maximum number of users as specified by the parameter [max_results] will be fetched starting from the first.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to search users using username for Jira cloud, we will use the user's display name to search users. You can use the [display_name] action parameter to search users for Jira cloud, and, [username] action parameter will be used to search users for Jira on-prem.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**username** | optional | A string to match with usernames, name, or email against for JIRA on-prem (required for Jira on-prem) | string | `user name` |
**display_name** | optional | A string to match with display name for JIRA cloud (required for Jira cloud) | string | `jira user display name` |
**max_results** | optional | Maximum number of users to return | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.username | string | `user name` | |
action_result.parameter.display_name | string | `jira user display name` | |
action_result.parameter.max_results | numeric | | |
action_result.data.\*.accountId | string | `jira user account id` | 5d2ef6aa6637260c19b78dfd |
action_result.data.\*.accountType | string | | atlassian |
action_result.data.\*.active | boolean | | True False |
action_result.data.\*.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.emailAddress | string | `email` | test@domain.us |
action_result.data.\*.key | string | | test |
action_result.data.\*.locale | string | | en_US |
action_result.data.\*.name | string | `user name` | test |
action_result.data.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=test |
action_result.data.\*.timeZone | string | | America/Los_Angeles |
action_result.summary.total_users | numeric | | 5 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'set status'

Set ticket (issue) status

Type: **generic** <br>
Read only: **False**

In JIRA, the status transition of an issue is determined by the workflow defined for the project. The app will return an error if an un-allowed status transition is attempted. In such cases, the possible statuses are returned based on the issue's current status value.<br>The same is the case for invalid resolutions. Do note that some combinations of status and resolution values might be invalid, even if they are allowed individually.<br>To get valid values to use as input for the parameters:<ul><li>For valid <b>status</b> values:<ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/issue/<i>[jira_issue_key]</i>/transitions</li><li>The returned JSON should contain a list of transitions</li><li>The name field denotes the status that can be set using this action</li></ul></li><li>For valid <b>resolution</b> values: <ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/resolution</li><li>The returned JSON should contain a list of resolutions</li><li>The name field in each resolution denotes the value to be used</li></ul></li></ul>.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Ticket (issue) key | string | `jira ticket key` |
**status** | required | Status to set | string | `jira ticket status` |
**resolution** | optional | Resolution to set | string | `jira ticket resolution` |
**comment** | optional | Comment to set | string | |
**update_fields** | optional | JSON containing field values | string | |
**time_spent** | optional | Time Spent to Log | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.status | string | `jira ticket status` | |
action_result.parameter.resolution | string | `jira ticket resolution` | |
action_result.parameter.comment | string | | |
action_result.parameter.update_fields | string | | |
action_result.parameter.time_spent | string | | |
action_result.data.\*.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.Epic Link | string | | |
action_result.data.\*.fields.Severity | string | | |
action_result.data.\*.fields.Sprint | string | | com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97\[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1\] |
action_result.data.\*.fields.aggregateprogress.percent | numeric | | 100 |
action_result.data.\*.fields.aggregateprogress.progress | numeric | | 0 |
action_result.data.\*.fields.aggregateprogress.total | numeric | | 0 |
action_result.data.\*.fields.aggregatetimeestimate | numeric | | |
action_result.data.\*.fields.aggregatetimeoriginalestimate | string | | |
action_result.data.\*.fields.aggregatetimespent | numeric | | |
action_result.data.\*.fields.assignee.accountId | string | `jira user account id` | 5d2ef6ab52a8370c567f27bb |
action_result.data.\*.fields.assignee.accountType | string | | atlassian |
action_result.data.\*.fields.assignee.active | boolean | | True False |
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.fields.assignee.emailAddress | string | `email` | abc@domain.com |
action_result.data.\*.fields.assignee.key | string | | test |
action_result.data.\*.fields.assignee.name | string | `user name` | test |
action_result.data.\*.fields.assignee.self | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.timeZone | string | | |
action_result.data.\*.fields.attachment.\*.author.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.attachment.\*.author.accountType | string | | atlassian |
action_result.data.\*.fields.attachment.\*.author.active | boolean | | True False |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.attachment.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.attachment.\*.author.key | string | | admin |
action_result.data.\*.fields.attachment.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.attachment.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.attachment.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.attachment.\*.content | string | `url` | http://jira.instance.ip/secure/attachment/10403/Add+Comment.png |
action_result.data.\*.fields.attachment.\*.created | string | | 2018-09-19T18:15:01.060-0700 |
action_result.data.\*.fields.attachment.\*.filename | string | | Add Comment.png |
action_result.data.\*.fields.attachment.\*.id | string | | 10403 |
action_result.data.\*.fields.attachment.\*.mimeType | string | | image/png |
action_result.data.\*.fields.attachment.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/attachment/10403 |
action_result.data.\*.fields.attachment.\*.size | numeric | | 97613 |
action_result.data.\*.fields.attachment.\*.thumbnail | string | `url` | http://jira.instance.ip/secure/thumbnail/10403/\_thumb_10403.png |
action_result.data.\*.fields.comment.comments.\*.author.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.author.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.body | string | | This is a sample testing body for the comment |
action_result.data.\*.fields.comment.comments.\*.created | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.id | string | | 10004 |
action_result.data.\*.fields.comment.comments.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.updated | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.visibility.type | string | | group role |
action_result.data.\*.fields.comment.comments.\*.visibility.value | string | | jira-software-users |
action_result.data.\*.fields.comment.maxResults | numeric | | 7 |
action_result.data.\*.fields.comment.startAt | numeric | | 0 |
action_result.data.\*.fields.comment.total | numeric | | 7 |
action_result.data.\*.fields.components.\*.id | string | | 10104 |
action_result.data.\*.fields.components.\*.name | string | | comp_test1 |
action_result.data.\*.fields.components.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/component/10104 |
action_result.data.\*.fields.created | string | | 2016-03-13T13:22:08.254-0700 |
action_result.data.\*.fields.creator.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.creator.accountType | string | | atlassian |
action_result.data.\*.fields.creator.active | boolean | | True False |
action_result.data.\*.fields.creator.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.creator.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.creator.key | string | | admin |
action_result.data.\*.fields.creator.name | string | `user name` | admin |
action_result.data.\*.fields.creator.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.creator.timeZone | string | | UTC |
action_result.data.\*.fields.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.duedate | string | | |
action_result.data.\*.fields.environment | string | | above ground |
action_result.data.\*.fields.fixVersions.\*.archived | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.id | string | | 10000 |
action_result.data.\*.fields.fixVersions.\*.name | string | | 1.0 |
action_result.data.\*.fields.fixVersions.\*.released | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.issuelinks.\*.id | string | | 10727 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string | | 21576 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string | | MAN-278 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string | | http://jira.instance.ip/rest/api/2/issue/21576 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string | | 21133 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string | | SPOL-44 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string | | http://jira.instance.ip/rest/api/2/issue/21133 |
action_result.data.\*.fields.issuelinks.\*.self | string | | http://jira.instance.ip/rest/api/2/issueLink/10727 |
action_result.data.\*.fields.issuelinks.\*.type.id | string | | 10000 |
action_result.data.\*.fields.issuelinks.\*.type.inward | string | | is blocked by |
action_result.data.\*.fields.issuelinks.\*.type.name | string | | Blocks |
action_result.data.\*.fields.issuelinks.\*.type.outward | string | | blocks |
action_result.data.\*.fields.issuelinks.\*.type.self | string | | http://jira.instance.ip/rest/api/2/issueLinkType/10000 |
action_result.data.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.labels.\* | string | | |
action_result.data.\*.fields.lastViewed | string | | 2018-09-20T23:54:50.643-0700 |
action_result.data.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.progress.percent | numeric | | 100 |
action_result.data.\*.fields.progress.progress | numeric | | 0 |
action_result.data.\*.fields.progress.total | numeric | | 0 |
action_result.data.\*.fields.project.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.id | string | | 10100 |
action_result.data.\*.fields.project.key | string | `jira project key` | MAN |
action_result.data.\*.fields.project.name | string | | TestProject |
action_result.data.\*.fields.project.self | string | `url` | http://jira.instance.ip/rest/api/2/project/10100 |
action_result.data.\*.fields.reporter.accountType | string | | atlassian |
action_result.data.\*.fields.reporter.active | boolean | | True False |
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.reporter.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.reporter.key | string | | admin |
action_result.data.\*.fields.reporter.name | string | `user name` | admin |
action_result.data.\*.fields.reporter.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.reporter.timeZone | string | | UTC |
action_result.data.\*.fields.resolution.description | string | | Work has been completed on this issue |
action_result.data.\*.fields.resolution.id | string | | 10000 |
action_result.data.\*.fields.resolution.name | string | `jira ticket resolution` | Done |
action_result.data.\*.fields.resolution.self | string | `url` | http://jira.instance.ip/rest/api/2/resolution/10000 |
action_result.data.\*.fields.resolutiondate | string | | 2018-09-20T19:02:38.646-0700 |
action_result.data.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.summary | string | | Sample summary |
action_result.data.\*.fields.timeestimate | numeric | | |
action_result.data.\*.fields.timeoriginalestimate | string | | |
action_result.data.\*.fields.timespent | numeric | | |
action_result.data.\*.fields.timetracking.remainingEstimate | string | | 0m |
action_result.data.\*.fields.timetracking.remainingEstimateSeconds | numeric | | 0 |
action_result.data.\*.fields.timetracking.timeSpent | string | | 2d 4h |
action_result.data.\*.fields.timetracking.timeSpentSeconds | numeric | | 72000 |
action_result.data.\*.fields.updated | string | | 2018-09-25T06:21:27.802-0700 |
action_result.data.\*.fields.versions.\*.archived | boolean | | True False |
action_result.data.\*.fields.versions.\*.id | string | | 10000 |
action_result.data.\*.fields.versions.\*.name | string | | 1.0 |
action_result.data.\*.fields.versions.\*.released | boolean | | True False |
action_result.data.\*.fields.versions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.votes.hasVoted | boolean | | True False |
action_result.data.\*.fields.votes.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/votes |
action_result.data.\*.fields.votes.votes | numeric | | 0 |
action_result.data.\*.fields.watches.isWatching | boolean | | True False |
action_result.data.\*.fields.watches.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers |
action_result.data.\*.fields.watches.watchCount | numeric | | 1 |
action_result.data.\*.fields.worklog.maxResults | numeric | | 20 |
action_result.data.\*.fields.worklog.startAt | numeric | | 0 |
action_result.data.\*.fields.worklog.total | numeric | | 0 |
action_result.data.\*.fields.worklog.worklogs.\*.author.active | boolean | | True False |
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.worklog.worklogs.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.worklog.worklogs.\*.author.key | string | | admin |
action_result.data.\*.fields.worklog.worklogs.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.worklog.worklogs.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.worklog.worklogs.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.worklog.worklogs.\*.comment | string | | |
action_result.data.\*.fields.worklog.worklogs.\*.created | string | | 2021-12-06T06:35:45.703+0000 |
action_result.data.\*.fields.worklog.worklogs.\*.id | string | | 10200 |
action_result.data.\*.fields.worklog.worklogs.\*.issueId | string | | 27216 |
action_result.data.\*.fields.worklog.worklogs.\*.self | string | | http://jira.instance.ip/rest/api/2/issue/27216/worklog/10200 |
action_result.data.\*.fields.worklog.worklogs.\*.started | string | | 2021-12-06T06:35:00.000+0000 |
action_result.data.\*.fields.worklog.worklogs.\*.timeSpent | string | | 4h |
action_result.data.\*.fields.worklog.worklogs.\*.timeSpentSeconds | numeric | | 14400 |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.active | boolean | | True False |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.key | string | | admin |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.name | string | `user name` | admin |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.timeZone | string | | UTC |
action_result.data.\*.fields.worklog.worklogs.\*.updated | string | | 2021-12-06T06:35:45.703+0000 |
action_result.data.\*.fields.workratio | numeric | | -1 |
action_result.data.\*.id | string | | 10246 |
action_result.data.\*.issue_type | string | `jira issue type` | Defect |
action_result.data.\*.name | string | `jira ticket key` | MAN-1 |
action_result.data.\*.priority | string | `jira ticket priority` | Medium |
action_result.data.\*.project_key | string | `jira project key` | MAN |
action_result.data.\*.reporter | string | `jira user display name` | Test Admin |
action_result.data.\*.resolution | string | `jira ticket resolution` | Done |
action_result.data.\*.status | string | | Done |
action_result.data.\*.summary | string | | Sample summary |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'update ticket'

Update ticket (issue)

Type: **generic** <br>
Read only: **False**

Update an existing issue with the values specified in the <b>update_fields</b> parameter.<br>The results of the <b>get ticket</b> action may be used to obtain the <b>update_fields</b> parameters, including any custom fields present in the JIRA.</br>The JSON specified in the <b>update_fields</b> parameter requires the keys and the values specified in case-sensitive and double-quotes string format, except in the case of boolean values, which should be either <i>true</i> or <i>false</i> for example:</br>{\\"summary\\": \\"Zeus, multiple action need to be taken\\", \\"description\\": \\"A new summary was added\\"}</br></br>The App supports multiple methods for specifying the input dictionary. Please see \<a href=\\"https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#editing-an-issue-examples\\" target='\_blank'><b>the Atlassian documentation for the JIRA REST <i>update issue</i> API</b></a> for more information.<br>The following formats can be passed as input: <ul><li>Simple format; Create a dictionary with all the fields that need to be set:<br>{\\"summary\\": \\"Zeus detected on endpoint\\", \\"description\\": \\"Investigate further\\"}</li><li>Using the <i>update</i> key; Some issue fields support operations like <i>remove</i> and <i>add</i>, these operations can be combined to update a ticket: <br>{\\"<b>update</b>\\": {\\"components\\" : [{\\"remove\\" : {\\"name\\" : \\"secondcomponent\\"}}, {\\"add\\" : {\\"name\\" : \\"firstcomponent\\"}}]}}<br>{\\"<b>update</b>\\": {\\"comment\\": [{\\"add\\": {\\"body\\": \\"test comment update\\"}}]}} </li><li>Using the <i>fields</i> key;</br>{\\"<b>fields</b>\\":{\\"labels\\" : [\\"FIRSTLABEL\\"]}}</li></ul></br>The app supports updating custom fields; depending on the custom field type, some operations might not be available. Review the <b>jira_app</b> playbook for examples.<br><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><br>This action requires that either the <b>update_fields</b> parameter or the <b>vault_id</b> parameter is filled out. The action will fail if it either unsuccessfully attempts to add the attachment to the ticket or update the fields on the ticket.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to update fields related to user resources in the Jira ticket using username for Jira cloud, we will use the user's account_id to update fields related to user resources. Use 'lookup users' action to find out user's account_id. Use 'get ticket' action results to obtain the [update_fields] parameters. Please find out below-mentioned examples for the [update_fields] parameter which is related to user resources.<ul><li>Add assignee to the Jira ticket for Jira on-prem:<br>{\\"fields\\":{\\"assignee\\" : {\\"name\\": \\"username\\"}}}</li><li>Add assignee to the Jira ticket for Jira cloud:<br>{\\"fields\\":{\\"assignee\\" : {\\"accountId\\": \\"6d1ef6xy52z7360c267f27bb\\"}}}</li></ul>.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** | required | Issue ID | string | `jira ticket key` |
**update_fields** | optional | JSON containing field values | string | |
**vault_id** | optional | Vault ID of attachment | string | `vault id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.id | string | `jira ticket key` | |
action_result.parameter.update_fields | string | | |
action_result.parameter.vault_id | string | `vault id` | |
action_result.data.\*.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.Epic Link | string | | |
action_result.data.\*.fields.Sprint | string | | com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97\[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1\] |
action_result.data.\*.fields.aggregateprogress.progress | numeric | | 0 |
action_result.data.\*.fields.aggregateprogress.total | numeric | | 0 |
action_result.data.\*.fields.aggregatetimeestimate | numeric | | |
action_result.data.\*.fields.aggregatetimeoriginalestimate | numeric | | |
action_result.data.\*.fields.aggregatetimespent | numeric | | |
action_result.data.\*.fields.assignee.accountId | string | `jira user account id` | 5d2ef6ab52a8370c567f27bb |
action_result.data.\*.fields.assignee.accountType | string | | atlassian |
action_result.data.\*.fields.assignee.active | boolean | | True False |
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.displayName | string | `jira user display name` | Test Name |
action_result.data.\*.fields.assignee.emailAddress | string | `email` | abc@domain.com |
action_result.data.\*.fields.assignee.key | string | | test |
action_result.data.\*.fields.assignee.name | string | `user name` | test |
action_result.data.\*.fields.assignee.self | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.assignee.timeZone | string | | |
action_result.data.\*.fields.attachment.\*.author.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.attachment.\*.author.accountType | string | | atlassian |
action_result.data.\*.fields.attachment.\*.author.active | boolean | | True False |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.attachment.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.attachment.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.attachment.\*.author.key | string | | admin |
action_result.data.\*.fields.attachment.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.attachment.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.attachment.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.attachment.\*.content | string | `url` | http://jira.instance.ip/secure/attachment/10403/Add+Comment.png |
action_result.data.\*.fields.attachment.\*.created | string | | 2018-09-19T18:15:01.060-0700 |
action_result.data.\*.fields.attachment.\*.filename | string | | Add Comment.png |
action_result.data.\*.fields.attachment.\*.id | string | | 10403 |
action_result.data.\*.fields.attachment.\*.mimeType | string | | image/png |
action_result.data.\*.fields.attachment.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/attachment/10403 |
action_result.data.\*.fields.attachment.\*.size | numeric | | 97613 |
action_result.data.\*.fields.attachment.\*.thumbnail | string | `url` | http://jira.instance.ip/secure/thumbnail/10403/\_thumb_10403.png |
action_result.data.\*.fields.comment.comments.\*.author.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.author.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.author.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.author.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.author.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.body | string | | This is a sample testing body for the comment |
action_result.data.\*.fields.comment.comments.\*.created | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.id | string | | 10004 |
action_result.data.\*.fields.comment.comments.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean | | True False |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string | | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string | `user name` | admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string | | UTC |
action_result.data.\*.fields.comment.comments.\*.updated | string | | 2016-03-15T17:11:49.767-0700 |
action_result.data.\*.fields.comment.comments.\*.visibility.type | string | | group role |
action_result.data.\*.fields.comment.comments.\*.visibility.value | string | | jira-software-users |
action_result.data.\*.fields.comment.maxResults | numeric | | 7 |
action_result.data.\*.fields.comment.startAt | numeric | | 0 |
action_result.data.\*.fields.comment.total | numeric | | 7 |
action_result.data.\*.fields.components.\*.id | string | | 10104 |
action_result.data.\*.fields.components.\*.name | string | | comp_test1 |
action_result.data.\*.fields.components.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/component/10104 |
action_result.data.\*.fields.created | string | | 2016-03-13T13:22:08.254-0700 |
action_result.data.\*.fields.creator.accountId | string | `jira user account id` | 557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce |
action_result.data.\*.fields.creator.accountType | string | | atlassian |
action_result.data.\*.fields.creator.active | boolean | | True False |
action_result.data.\*.fields.creator.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.creator.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.creator.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.creator.key | string | | admin |
action_result.data.\*.fields.creator.name | string | `user name` | admin |
action_result.data.\*.fields.creator.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.creator.timeZone | string | | UTC |
action_result.data.\*.fields.description | string | | This is a sample testing description of the ticket |
action_result.data.\*.fields.duedate | string | | |
action_result.data.\*.fields.environment | string | | above ground |
action_result.data.\*.fields.fixVersions.\*.archived | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.id | string | | 10000 |
action_result.data.\*.fields.fixVersions.\*.name | string | | 1.0 |
action_result.data.\*.fields.fixVersions.\*.released | boolean | | True False |
action_result.data.\*.fields.fixVersions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.issuelinks.\*.id | string | | 10615 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string | | 21237 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string | | SPOL-133 |
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string | | http://jira.instance.ip/rest/api/2/issue/21237 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string | | 10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string | | Sample summary |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string | | 11849 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string | `jira ticket key` | ZEP-14 |
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/11849 |
action_result.data.\*.fields.issuelinks.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLink/10615 |
action_result.data.\*.fields.issuelinks.\*.type.id | string | | 10000 |
action_result.data.\*.fields.issuelinks.\*.type.inward | string | | is blocked by |
action_result.data.\*.fields.issuelinks.\*.type.name | string | | Blocks |
action_result.data.\*.fields.issuelinks.\*.type.outward | string | | blocks |
action_result.data.\*.fields.issuelinks.\*.type.self | string | `url` | http://jira.instance.ip/rest/api/2/issueLinkType/10000 |
action_result.data.\*.fields.issuetype.avatarId | numeric | | 10303 |
action_result.data.\*.fields.issuetype.description | string | | A problem which impairs or prevents the functions of the product |
action_result.data.\*.fields.issuetype.iconUrl | string | `url` | http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype |
action_result.data.\*.fields.issuetype.id | string | | 1 |
action_result.data.\*.fields.issuetype.name | string | `jira issue type` | Defect |
action_result.data.\*.fields.issuetype.self | string | `url` | http://jira.instance.ip/rest/api/2/issuetype/1 |
action_result.data.\*.fields.issuetype.subtask | boolean | | True False |
action_result.data.\*.fields.labels.\* | string | | |
action_result.data.\*.fields.lastViewed | string | | 2018-09-20T23:54:50.643-0700 |
action_result.data.\*.fields.priority.iconUrl | string | `url` | http://jira.instance.ip/images/icons/priorities/medium.svg |
action_result.data.\*.fields.priority.id | string | | 3 |
action_result.data.\*.fields.priority.name | string | `jira ticket priority` | Medium |
action_result.data.\*.fields.priority.self | string | `url` | http://jira.instance.ip/rest/api/2/priority/3 |
action_result.data.\*.fields.progress.progress | numeric | | 0 |
action_result.data.\*.fields.progress.total | numeric | | 0 |
action_result.data.\*.fields.project.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.project.id | string | | 10100 |
action_result.data.\*.fields.project.key | string | `jira project key` | MAN |
action_result.data.\*.fields.project.name | string | | TestProject |
action_result.data.\*.fields.project.projectCategory.description | string | | test |
action_result.data.\*.fields.project.projectCategory.id | string | | 10000 |
action_result.data.\*.fields.project.projectCategory.name | string | | QA-Team |
action_result.data.\*.fields.project.projectCategory.self | string | | https://testlab.atlassian.net/rest/api/2/projectCategory/10000 |
action_result.data.\*.fields.project.projectTypeKey | string | | software |
action_result.data.\*.fields.project.self | string | `url` | http://jira.instance.ip/rest/api/2/project/10100 |
action_result.data.\*.fields.project.simplified | boolean | | True False |
action_result.data.\*.fields.reporter.accountType | string | | atlassian |
action_result.data.\*.fields.reporter.active | boolean | | True False |
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string | `url` | http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string | `url` | http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string | `url` | http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string | `url` | http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 |
action_result.data.\*.fields.reporter.displayName | string | `jira user display name` | Test Admin |
action_result.data.\*.fields.reporter.emailAddress | string | `email` | notifications@domain.us |
action_result.data.\*.fields.reporter.key | string | | admin |
action_result.data.\*.fields.reporter.name | string | `user name` | admin |
action_result.data.\*.fields.reporter.self | string | `url` | http://jira.instance.ip/rest/api/2/user?username=admin |
action_result.data.\*.fields.reporter.timeZone | string | | UTC |
action_result.data.\*.fields.resolution.description | string | | Work has been completed on this issue |
action_result.data.\*.fields.resolution.id | string | | 10000 |
action_result.data.\*.fields.resolution.name | string | `jira ticket resolution` | Done |
action_result.data.\*.fields.resolution.self | string | `url` | http://jira.instance.ip/rest/api/2/resolution/10000 |
action_result.data.\*.fields.resolutiondate | string | | 2018-09-20T19:02:38.646-0700 |
action_result.data.\*.fields.security | string | | |
action_result.data.\*.fields.status.description | string | | This is a sample testing description |
action_result.data.\*.fields.status.iconUrl | string | `url` | http://jira.instance.ip/images/icons/statuses/closed.png |
action_result.data.\*.fields.status.id | string | | 10001 |
action_result.data.\*.fields.status.name | string | | Done |
action_result.data.\*.fields.status.self | string | `url` | http://jira.instance.ip/rest/api/2/status/10001 |
action_result.data.\*.fields.status.statusCategory.colorName | string | | green |
action_result.data.\*.fields.status.statusCategory.id | numeric | | 3 |
action_result.data.\*.fields.status.statusCategory.key | string | | done |
action_result.data.\*.fields.status.statusCategory.name | string | | Done |
action_result.data.\*.fields.status.statusCategory.self | string | `url` | http://jira.instance.ip/rest/api/2/statuscategory/3 |
action_result.data.\*.fields.statuscategorychangedate | string | | 2019-07-22T22:43:07.771-0700 |
action_result.data.\*.fields.summary | string | | Sample summary |
action_result.data.\*.fields.timeestimate | numeric | | |
action_result.data.\*.fields.timeoriginalestimate | numeric | | |
action_result.data.\*.fields.timespent | numeric | | |
action_result.data.\*.fields.updated | string | | 2018-09-25T06:49:43.523-0700 |
action_result.data.\*.fields.versions.\*.archived | boolean | | True False |
action_result.data.\*.fields.versions.\*.id | string | | 10000 |
action_result.data.\*.fields.versions.\*.name | string | | 1.0 |
action_result.data.\*.fields.versions.\*.released | boolean | | True False |
action_result.data.\*.fields.versions.\*.self | string | `url` | http://jira.instance.ip/rest/api/2/version/10000 |
action_result.data.\*.fields.votes.hasVoted | boolean | | True False |
action_result.data.\*.fields.votes.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/votes |
action_result.data.\*.fields.votes.votes | numeric | | 0 |
action_result.data.\*.fields.watches.isWatching | boolean | | True False |
action_result.data.\*.fields.watches.self | string | `url` | http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers |
action_result.data.\*.fields.watches.watchCount | numeric | | 1 |
action_result.data.\*.fields.worklog.maxResults | numeric | | 20 |
action_result.data.\*.fields.worklog.startAt | numeric | | 0 |
action_result.data.\*.fields.worklog.total | numeric | | 0 |
action_result.data.\*.fields.workratio | numeric | | -1 |
action_result.data.\*.id | string | | 10246 |
action_result.data.\*.issue_type | string | `jira issue type` | Defect |
action_result.data.\*.name | string | `jira ticket key` | MAN-1 |
action_result.data.\*.priority | string | `jira ticket priority` | Medium |
action_result.data.\*.project_key | string | `jira project key` | MAN |
action_result.data.\*.reporter | string | `jira user display name` | Test Admin |
action_result.data.\*.resolution | string | `jira ticket resolution` | Done |
action_result.data.\*.status | string | | Done |
action_result.data.\*.summary | string | | Sample summary |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'on poll'

Ingest Jira tickets as SOAR containers with field, comment, and attachment artifacts.

State is stored in `asset.ingest_state` (SDK-managed, encrypted at rest):

- `first_run` (bool): True until the first scheduled poll completes.
- `last_time` (int): UTC epoch seconds of the `updated` field of the last ingested issue.

Three execution modes (mirrors legacy connector):

- Poll Now (params.is_manual_poll()): uses params.container_count as limit; never writes state.
- First Run (state["first_run"] == True): uses asset.first_run_max_tickets; no time filter.
- Scheduled (ongoing): uses asset.max_tickets; adds `updated>="..."` JQL filter.

Type: **ingest** <br>
Read only: **True**

Callback action for the on_poll ingest functionality

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_time** | optional | Start of time range, in epoch time (milliseconds). | numeric | |
**end_time** | optional | End of time range, in epoch time (milliseconds). | numeric | |
**container_count** | optional | Maximum number of container records to query for. | numeric | |
**artifact_count** | optional | Maximum number of artifact records to query for. | numeric | |
**container_id** | optional | Comma-separated list of container IDs to limit the ingestion to. | string | |

#### Action Output

No Output

## action: 'test connectivity'

test connectivity

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
