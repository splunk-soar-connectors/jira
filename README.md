[comment]: # "Auto-generated SOAR connector documentation"
# Jira

Publisher: Splunk  
Connector Version: 3.5.0  
Product Vendor: Atlassian  
Product Name: Jira  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 5.3.0  

This app integrates with JIRA to perform several ticket management actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2022 Splunk Inc."
[comment]: # "  Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "  you may not use this file except in compliance with the License."
[comment]: # "  You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "      http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # "  Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "  the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "  either express or implied. See the License for the specific language governing permissions"
[comment]: # "  and limitations under the License."
[comment]: # ""
## JIRA

This app uses the python JIRA module, which is licensed under the BSD License (BSD), Copyright (c)
2001-2022. Python Software Foundation

## oauthlib

This app uses the python oauthlib module, which is licensed under the OSI Approved, BSD License
(BSD), Copyright (c) 2001-2022. Python Software Foundation

## pbr

This app uses the python pbr module, which is licensed under the Apache Software License, Copyright
(c) 2001-2022. Python Software Foundation

## PyJWT

This app uses the python PyJWT module, which is licensed under the MIT License (MIT), Copyright (c)
2001-2022. Python Software Foundation

## requests-oauthlib

This app uses the python requests-oauthlib module, which is licensed under the BSD License (ISC),
Copyright (c) 2001-2022. Python Software Foundation

## requests-toolbelt

This app uses the python requests-toolbelt module, which is licensed under the Apache Software
License (Apache 2.0), Copyright (c) 2001-2022. Python Software Foundation

## JIRA

JIRA is a highly configurable ticketing system, and the actions performed by these API calls are
highly dependent on the process defined in each Jira instance.

If your action fails, you may need to try an alternate method, or sequence, to perform the actions
desired for Jira to process them properly. One helpful debugging tool: simplify your action, instead
of filling out all the fields, attempt to make only one change at a time.

Unfortunately, the JIRA API in most cases returns a generic error message with no valuable
information to assist in debugging.

**Playbook Backward Compatibility**

-   The existing action parameters have been modified in the actions given below. Hence, it is
    requested to the end-user to please update their existing playbooks by re-inserting the
    corresponding action blocks or by providing appropriate values to these action parameters to
    ensure the correct functioning of the playbooks created on the earlier versions of the app.

      

    -   Add Watcher - The new \[user_account_id\] parameter has been added for the Jira cloud to add
        a watcher into a provided issue.
    -   Remove Watcher - The new \[user_account_id\] parameter has been added for the Jira cloud to
        remove a watcher from a provided issue.
    -   Create Ticket - The new \[assignee_account_id\] parameter has been added for the Jira cloud
        to add the assignee while creating a Jira ticket.
    -   Lookup Users - Added a new action. This action will get a list of User resources that match
        the specified search string.
    -   Add Comment - The new \[internal\] parameter has been added for comment that whether it
        should be internal only or not in Jira Service Desk. This parameter is an optional Boolean
        parameter. If the value is not provided for it, then it will be considered as a 'False'
        value.
    -   Get Attachments - Added a new action. The action will store specific attachments from a
        given Jira ticket inside the vault.

**Authentication steps for JIRA Cloud**

-   Create an API token

      

    -   Log in to [Click here.](https://id.atlassian.com/manage/api-tokens)

    -   Click **Create an API token.**

    -   From the dialog that appears, enter a unique and concise **Label** for your token and click
        **Create** .

    -   Click **Copy to clipboard** , then paste the token to your script, or elsewhere to save.

          
          
        Notes:

    -   For security reasons it isn't possible to view the token after closing the creation dialog;
        if necessary, create a new token.

    -   You should store the token securely, just as for any password.

      

-   Use an API token

      

    -   A primary use case for API tokens is to allow scripts to access REST APIs for Atlassian
        Cloud applications using HTTP basic authentication.
    -   HTTP basic authentication would require a username and API token to access REST APIs for
        Atlassian Cloud applications.

      

**Authentication via Personal Access Token (PAT)**

-   [Click
    here](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html#UsingPersonalAccessTokens-CreatingPATsinapplication)
    for instructions to create PATs

      

    Personal Access Tokens are a safe alternative to using username and password for authentication
    with various services in **Data Center and server editions** of the following applications:

    -   Jira Core 8.14 and later
    -   Jira Software 8.14 and later
    -   Jira Service Management 4.15 and later
    -   Confluence 7.9 and later

      

-   Use a PAT

      

    -   A primary use case for PATs is to use scripts and integrate external apps with your
        Atlassian application by leveraging REST APIs upon Bearer Token Authorization.
    -   To use Bearer Token Authorization, configure your asset with PAT in the "Password" field and
        leave "Username" blank.

-   Note:

      

    -   For security reasons it isn't possible to view the token after closing the creation dialog;
        if necessary, create a new token.
    -   For any invalid PAT value, the test_connectivity will pass as per the API behaviour.

      

**The functioning of On Poll**

-   **NOTE (Consider below points due to a minute's granularity (instead of a second or lesser) for
    querying tickets in the JIRA)**

      

    -   It is highly recommended for configuring a significantly large value (larger than the number
        of existing tickets on the user's instance) in the asset configuration parameter to bring
        the ingested tickets in the Splunk SOAR in sync entirely with the JIRA instance in the first
        run
    -   It is highly recommended for configuring a significantly large value (larger than the
        possible number of tickets that can be updated in 1 minute or any value larger than the
        average number of tickets getting created every unit of time (based on the frequency of
        scheduled or interval polling)) in the asset configuration parameter to avoid the duplicate
        tickets ingestion

      

-   The On Poll action works in 2 steps. In the first step, all the tickets (issues) in a defined
    time duration will be fetched. In the second step, all the components (e.g. fields, comments,
    and attachments) of the tickets (retrieved in the first step) will be fetched. A container will
    be created for each ticket and for each ticket all the components will be created as the
    respective artifacts.

-   The tickets will be fetched in the oldest first order based on the **updated** time in the On
    Poll action

-   The updated timestamps of the components have been appended to the end of the artifact name to
    maintain the uniqueness of a particular component

-   The timezone parameter in the asset configurations defines the timezone used to query the
    tickets from the JIRA instance. If you do not find your exact timezone in the available list in
    the dropdown, please select a timezone having the same time offset from the GMT timezone as
    yours. Below are the details of setting the timezone parameter for on-prem and cloud JIRA
    instances.

      

    1.  On-premise JIRA
        -   The timezone parameter here is the profile timezone of the JIRA instance
        -   For checking the profile timezone, navigate to the JIRA instance; navigate to the
            profile settings; the value of the **Time Zone** parameter is the timezone that has to
            be provided in the app asset configuration
    2.  Cloud JIRA
        -   The timezone parameter here is the system settings timezone of the JIRA instance
        -   For checking the system settings timezone, navigate to the JIRA instance; navigate to
            the option **Jira Settings --> System** in the settings page; the value of the **Default
            user time zone** parameter is the timezone that has to be provided in the app asset
            configuration

-   Users can provide the JSON formatted list of names of the custom fields (to be considered for
    the ingestion) in the asset configuration parameter **custom_fields** e.g. \["Test \\"CF\\" 1",
    "test_cf_2"\]. It's a valid JSON formatted list of strings, so the user should use escape
    sequences whenever needed. Please find the below points for getting exact names for the custom
    fields.

      

    1.  On-premise JIRA
        -   Navigate to the JIRA instance; navigate to the issues settings; navigate to the **Custom
            fields** section under the **Fields** section; in the **Name** column, search for the
            custom field that the user wants to be added in the asset configuration parameter
            **custom_fields**
    2.  Cloud JIRA
        -   The timezone parameter here is the system settings timezone of the JIRA instance
        -   For checking the system settings timezone, navigate to the JIRA instance; navigate to
            the option **Jira Settings --> System** in the settings page; the value of the **Default
            user time zone** parameter is the timezone that has to be provided in the app asset
            configuration

-   If there is any error while fetching the custom fields metadata due to project configuration or
    lack of permissions, then, the custom fields will be ignored and the ingestion based on the
    system fields of the tickets (issues) will be executed successfully

      
      

-   Two approaches for fetching tickets

      
      

    -   Manual polling

          

        -   Fetch the tickets

              

            -   The tickets will be fetched from the project mentioned in the **Project key to
                ingest tickets (issues) from** app configuration parameter
            -   The tickets will be fetched in the oldest first order based on the **updated** time
                and governed by the **container_count** parameter in the On Poll action

        -   Fetch the components

              

            -   Fetch all created or updated components (e.g. fields, comments, and attachments) for
                each ticket (retrieved in the previous step)

        -   Create containers for the tickets and artifacts for the fields, comments, and the
            attachments

        -   It is recommended to provide a sufficiently large value in the **container_count**
            parameter for polling because manual polling does not remember the timestamp of last
            fetched ticket and it starts polling from the beginning every time. Hence, if the user
            runs the manual polling with e.g. 10 as the container count (the tickets are ingested
            successfully), then, the user again runs the manual polling with the same value in the
            container count; the app will fetch the same 10 tickets from the beginning and it will
            display the message as 'duplicate artifacts found' because the same artifacts were
            already ingested in the earlier manual polling run.

          

    -   Scheduled Polling

          

        -   Follows the same steps as manual polling with the below-mentioned points getting
            considered
        -   The application will fetch the number of tickets governed by the **Maximum tickets
            (issues) for scheduled polling** parameter (default: 100) in the On Poll action, whose
            **updated** time is greater than or equal to one minute less than the time stored in the
            **last_time** variable in the state file. The reason for reducing one minute from the
            **last_time** is to ensure that no tickets created or updated on the same minute are not
            getting skipped due to the granularity of Jira being 1 minute for the time-based
            filtering of the tickets.
        -   If the **last_time** variable is not present in the state file i.e. the On Poll is
            executing for the first time, the application will fetch the last **M** tickets ( **M:**
            Value provided in the **Maximum tickets (issues) to poll first time** app configuration
            parameter (default: 1000)) and then, from the next consecutive runs, it will fetch **N**
            tickets ( **N:** Value provided in the **Maximum tickets (issues) for scheduled
            polling** app configuration parameter (default: 100)).
        -   The last_time will be updated by the **updated** time of the last ticket which was
            ingested

      

**Some example caveats**

-   Attempting to set both Status and Resolution fails because the process set by the user doesn't
    require a resolution to be set by the user, such as if there is only one resolution for a
    particular status.
-   Attempting to add a comment while setting Status may return success, however, the comment isn't
    posted. In this case, when the status change is made via the Jira UI, no dialogue appears to
    offer any additional input, therefore the API expects the same.
-   The "simple" format for the update ticket may not work to add a comment, while the "update"
    method does.
-   Test connectivity may fail due to invalid credentials, such as accidentally using the user's
    email address as the authentication login instead of the user's login name.
-   While adding an attachment to the Jira ticket using 'Update ticket' action, if the filename
    contains Unicode characters, the action is getting failed with the 500 Internal Server Error
    because of the Jira SDK issue. Due to this, action behaves differently with the various Splunk
    SOAR platforms. As a result, we have deployed the below-mentioned workflow which will ensure a
    minimal change in the filename and minimal/no data loss.
    1.  For the first time we try to add an attachment to the Jira ticket with the same name as the
        filename, if it may get successful, then it will add an attachment with the same name
    2.  But if it fails, then, we will check whether there are Unicode characters or not in the
        filename, if it has, there are highly possible chances that Jira SDK might get throws an
        exception due to these Unicode characters.
    3.  And in such a case, we removed those non-ASCII Unicode characters from the filename and add
        prefix FILENAME_ASCII to the filename. And, we again try to add an attachment with a newly
        created name to the Jira ticket.
    4.  If it passes, then it's okay and if it doesn't, then, there might be some other genuine
        issue rather than the SDK issue and we fail the action by rethrowing the same error.

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the Jira server. Below are the default
ports used by the Splunk SOAR Connector.

| SERVICE NAME | TRANSPORT PROTOCOL | PORT |
|--------------|--------------------|------|
| http         | tcp                | 80   |
| https        | tcp                | 443  |


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Jira asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device_url** |  required  | string | Device URL including the port, e.g. https://myjira.enterprise.com:8080
**verify_server_cert** |  optional  | boolean | Verify server certificate
**username** |  optional  | string | Username
**password** |  required  | password | Password / API token (Jira Cloud) / PAT
**project_key** |  optional  | string | Project key to ingest tickets (issues) from
**query** |  optional  | string | Additional parameters to query for during ingestion in JQL
**first_run_max_tickets** |  optional  | numeric | Maximum tickets (issues) to poll first time
**max_tickets** |  optional  | numeric | Maximum tickets (issues) for scheduled polling
**custom_fields** |  optional  | string | JSON formatted list of names of custom fields (case-sensitive) to be ingested
**timezone** |  required  | timezone | Jira instance timezone (used for timezone conversions for querying in ingestion). Refer to README

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using the supplied credentials  
[create ticket](#action-create-ticket) - Create a ticket (issue)  
[get attachments](#action-get-attachments) - Gets specific attachments from a Jira Ticket (issue)  
[update ticket](#action-update-ticket) - Update ticket (issue)  
[add comment](#action-add-comment) - Add a comment to the ticket (issue)  
[delete ticket](#action-delete-ticket) - Delete ticket (issue)  
[list projects](#action-list-projects) - List all projects  
[list tickets](#action-list-tickets) - Get a list of tickets (issues) in a specified project  
[lookup users](#action-lookup-users) - Get a list of user resources that match the specified search string  
[get ticket](#action-get-ticket) - Get ticket (issue) information  
[set status](#action-set-status) - Set ticket (issue) status  
[link tickets](#action-link-tickets) - Create a link between two separate tickets  
[add watcher](#action-add-watcher) - Add a user to an issue's watchers list  
[remove watcher](#action-remove-watcher) - Remove a user from an issue's watchers list  
[on poll](#action-on-poll) - Ingest tickets from JIRA  

## action: 'test connectivity'
Validate the asset configuration for connectivity using the supplied credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'create ticket'
Create a ticket (issue)

Type: **generic**  
Read only: **False**

The <b>fields</b> parameter is provided for advanced use of the JIRA API. It is passed directly to the &quot;fields&quot; attribute in the JIRA API call. Values in the <b>fields</b> parameter will take precedence over the individual parameters such as <b>summary</b>, <b>description</b>, <b>project_key</b>, <b>issue_type</b>, etc.<br><br>When using the <b>fields</b> parameter, you are required to know how a particular field is inputted. To give a few examples (might differ in your JIRA environment):<ul><li>The <b>description</b> of a ticket can be added as the first level key with a value like { "description": "ticket description" }</li><li><b>issuetype</b> needs to be set as a dictionary like { "issuetype": { "name": "Task" } }</li><li><b>priority</b> is set as { "priority": { "name": "Medium" } }</li><li>The <b>project</b> key is set like { "project": { "key": "SPLUNK_APP" } }</li></ul><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><b>Assignee</b> and attachments by <b>vault_id</b> are addressed in a separate call to JIRA made after ticket creation.<br><br>The <b>project_key</b> parameter is case sensitive.<h3>Default Values</h3>Previous versions of the app set default values for <b>priority</b> and <b>issue_type</b>. This caused issues in situations where the default values used by the app were incompatible with the configured values. The app does not set default values anymore. If an optional field below is required by the JIRA environment and it is not provided, JIRA will give an error causing the action to fail.<br><br>This action will pass if a ticket is successfully created, even if it fails to assign the ticket, add an attachment to the ticket, or fill out the custom fields. These failures will be indicated in the result message.<h3>Creating a subtask</h3>The following <b>fields</b> parameter value can be used to create a sub-task, the key is to use the correct <b>issuetype</b>.<pre>{"fields":{"project":{"key":"AP"},"parent":{"key":"AP-231"},"summary":"Sub-taskofAP-231","description":"Don'tforgettodothistoo.","issuetype":{"name":"Sub-Task"}}}</pre><h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add an assignee to the Jira ticket using a username for the Jira cloud, we will use the user's account_id to add the assignee. Use 'lookup users' action to find out a user's account_id. You can use the [assignee_account_id] action parameter to add an assignee to the Jira ticket for the Jira cloud, and, [assignee] action parameter will be used to add an assignee to the Jira ticket for Jira on-prem.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project_key** |  required  | Project key to add the issue to (case-sensitive) | string |  `jira project key` 
**summary** |  required  | Summary of the issue | string | 
**description** |  optional  | Description of the issue | string | 
**issue_type** |  required  | Type of the issue (case-sensitive) | string |  `jira issue type` 
**priority** |  optional  | Priority of the issue | string |  `jira ticket priority` 
**assignee** |  optional  | Assignee username (required for Jira on-prem, assign required permissions) | string |  `user name` 
**assignee_account_id** |  optional  | Assignee user account ID (required for Jira cloud, assign required permissions) | string |  `jira user account id` 
**fields** |  optional  | JSON containing field values | string | 
**vault_id** |  optional  | Vault ID of attachment | string |  `vault id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.assignee | string |  `user name`  |   Test Name 
action_result.parameter.assignee_account_id | string |  `jira user account id`  |   5d2ef6ab52a8370c567f27bb 
action_result.parameter.description | string |  |   Jira QA automation ticket description 
action_result.parameter.fields | string |  |   {"priority": {"name": "Normal"}}  {"fields": {"customfield_10105": "Test epic link name"}} 
action_result.parameter.issue_type | string |  `jira issue type`  |   Story  Task 
action_result.parameter.priority | string |  `jira ticket priority`  |   Normal 
action_result.parameter.project_key | string |  `jira project key`  |   MAN 
action_result.parameter.summary | string |  |   Jira QA ticket 
action_result.parameter.vault_id | string |  `vault id`  |   fe3ac82064175835a67c279cbb9373f96c367566 
action_result.data.\*.assign_error | string |  |  
action_result.data.\*.attach_error | string |  |  
action_result.data.\*.description | string |  |   Jira QA automation ticket description 
action_result.data.\*.fields.Epic Link | string |  |  
action_result.data.\*.fields.Epic Name | string |  |   Test epic 
action_result.data.\*.fields.Severity | string |  |  
action_result.data.\*.fields.Sprint | string |  |  
action_result.data.\*.fields.aggregateprogress.progress | numeric |  |   0 
action_result.data.\*.fields.aggregateprogress.total | numeric |  |   0 
action_result.data.\*.fields.aggregatetimeestimate | string |  |  
action_result.data.\*.fields.aggregatetimeoriginalestimate | string |  |  
action_result.data.\*.fields.aggregatetimespent | string |  |  
action_result.data.\*.fields.assignee | string |  |  
action_result.data.\*.fields.assignee.accountId | string |  `jira user account id`  |   5d2ef6ab52a8370c567f27bb 
action_result.data.\*.fields.assignee.accountType | string |  |   atlassian 
action_result.data.\*.fields.assignee.active | boolean |  |   False  True 
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.displayName | string |  `jira user display name`  |   Test Name 
action_result.data.\*.fields.assignee.emailAddress | string |  |  
action_result.data.\*.fields.assignee.key | string |  |  
action_result.data.\*.fields.assignee.name | string |  `user name`  |   test 
action_result.data.\*.fields.assignee.self | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.timeZone | string |  |  
action_result.data.\*.fields.attachment.\*.author.active | boolean |  |   True 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string |  |   http://1jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string |  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string |  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string |  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.displayName | string |  |   Admin 
action_result.data.\*.fields.attachment.\*.author.emailAddress | string |  |   notifications@test.us 
action_result.data.\*.fields.attachment.\*.author.key | string |  |   admin 
action_result.data.\*.fields.attachment.\*.author.name | string |  |   admin 
action_result.data.\*.fields.attachment.\*.author.self | string |  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.attachment.\*.author.timeZone | string |  |   Etc/GMT 
action_result.data.\*.fields.attachment.\*.content | string |  |   http://jira.instance.ip/secure/attachment/11634/testfile%281%29.jpg 
action_result.data.\*.fields.attachment.\*.created | string |  |   2021-12-09T05:35:30.242+0000 
action_result.data.\*.fields.attachment.\*.filename | string |  |   testfile(1).jpg 
action_result.data.\*.fields.attachment.\*.id | string |  |   11634 
action_result.data.\*.fields.attachment.\*.mimeType | string |  |   image/jpeg 
action_result.data.\*.fields.attachment.\*.self | string |  |   http://jira.instance.ip/rest/api/2/attachment/11634 
action_result.data.\*.fields.attachment.\*.size | numeric |  |   6667 
action_result.data.\*.fields.attachment.\*.thumbnail | string |  |   http://jira.instance.ip/secure/thumbnail/11634/_thumb_11634.png 
action_result.data.\*.fields.comment.maxResults | numeric |  |   0 
action_result.data.\*.fields.comment.startAt | numeric |  |   0 
action_result.data.\*.fields.comment.total | numeric |  |   0 
action_result.data.\*.fields.created | string |  |   2018-09-25T06:31:58.854-0700 
action_result.data.\*.fields.creator.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.creator.accountType | string |  |   atlassian 
action_result.data.\*.fields.creator.active | boolean |  |   False  True 
action_result.data.\*.fields.creator.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.creator.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.creator.key | string |  |   admin 
action_result.data.\*.fields.creator.name | string |  `user name`  |   admin 
action_result.data.\*.fields.creator.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.creator.timeZone | string |  |   UTC 
action_result.data.\*.fields.description | string |  |   Jira QA automation ticket description 
action_result.data.\*.fields.duedate | string |  |  
action_result.data.\*.fields.environment | string |  |  
action_result.data.\*.fields.issuetype.avatarId | numeric |  |   10318 
action_result.data.\*.fields.issuetype.description | string |  |   This is a task 
action_result.data.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/issuetypes/story.svg 
action_result.data.\*.fields.issuetype.id | string |  |   10101 
action_result.data.\*.fields.issuetype.name | string |  `jira issue type`  |   Story  Task 
action_result.data.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/10101 
action_result.data.\*.fields.issuetype.subtask | boolean |  |   False  True 
action_result.data.\*.fields.lastViewed | string |  |  
action_result.data.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.progress.progress | numeric |  |   0 
action_result.data.\*.fields.progress.total | numeric |  |   0 
action_result.data.\*.fields.project.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=xsmall&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.24x24 | string |  `url`  |   http://1jira.instance.ip/secure/projectavatar?size=small&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=medium&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?avatarId=10403 
action_result.data.\*.fields.project.id | string |  |   10100 
action_result.data.\*.fields.project.key | string |  `jira project key`  |   MAN 
action_result.data.\*.fields.project.name | string |  |   TestProject 
action_result.data.\*.fields.project.projectCategory.description | string |  |   test 
action_result.data.\*.fields.project.projectCategory.id | string |  |   10000 
action_result.data.\*.fields.project.projectCategory.name | string |  |   QA-Team 
action_result.data.\*.fields.project.projectCategory.self | string |  |   https://testlab.atlassian.net/rest/api/2/projectCategory/10000 
action_result.data.\*.fields.project.projectTypeKey | string |  |   software 
action_result.data.\*.fields.project.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/project/10100 
action_result.data.\*.fields.project.simplified | boolean |  |   False  True 
action_result.data.\*.fields.reporter.accountType | string |  |   atlassian 
action_result.data.\*.fields.reporter.active | boolean |  |   False  True 
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string |  `url`  |   http://1jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.reporter.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.reporter.key | string |  |   admin 
action_result.data.\*.fields.reporter.name | string |  `user name`  |   admin 
action_result.data.\*.fields.reporter.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.reporter.timeZone | string |  |   UTC 
action_result.data.\*.fields.resolution | string |  |  
action_result.data.\*.fields.resolutiondate | string |  |   2018-10-03T03:42:10.912-0700 
action_result.data.\*.fields.security | string |  |  
action_result.data.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.status.id | string |  |   10000 
action_result.data.\*.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip0/rest/api/2/status/10000 
action_result.data.\*.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.statuscategorychangedate | string |  |   2019-07-22T22:43:07.771-0700 
action_result.data.\*.fields.summary | string |  |   Jira QA ticket 
action_result.data.\*.fields.timeestimate | string |  |  
action_result.data.\*.fields.timeoriginalestimate | string |  |  
action_result.data.\*.fields.timespent | string |  |  
action_result.data.\*.fields.updated | string |  |   2018-09-25T06:31:58.854-0700 
action_result.data.\*.fields.votes.hasVoted | boolean |  |   False  True 
action_result.data.\*.fields.votes.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-240/votes 
action_result.data.\*.fields.votes.votes | numeric |  |   0 
action_result.data.\*.fields.watches.isWatching | boolean |  |   False  True 
action_result.data.\*.fields.watches.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-240/watchers 
action_result.data.\*.fields.watches.watchCount | numeric |  |   1 
action_result.data.\*.fields.worklog.maxResults | numeric |  |   20 
action_result.data.\*.fields.worklog.startAt | numeric |  |   0 
action_result.data.\*.fields.worklog.total | numeric |  |   0 
action_result.data.\*.fields.workratio | numeric |  |   -1 
action_result.data.\*.id | string |  |   11850 
action_result.data.\*.issue_type | string |  `jira issue type`  |   Story  Task 
action_result.data.\*.json_fields_error | string |  |  
action_result.data.\*.name | string |  `jira ticket key`  |   MAN-240 
action_result.data.\*.priority | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.project_key | string |  `jira project key`  |   MAN 
action_result.data.\*.reporter | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.resolution | string |  `jira ticket resolution`  |   Unresolved 
action_result.data.\*.status | string |  |   To Do 
action_result.data.\*.summary | string |  |   Jira QA ticket 
action_result.summary | string |  |  
action_result.message | string |  |   Created ticket with id: 11850, key: MAN-240 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get attachments'
Gets specific attachments from a Jira Ticket (issue)

Type: **investigate**  
Read only: **True**

The function will store specific attachments from a given Jira ticket inside the vault.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | The key of the Jira issue | string |  `jira ticket key` 
**retrieve_all** |  optional  | If this is set to true all attachments will be retrieved from the issue (if the value is not provided, it will internally be treated as 'false') | boolean | 
**container_id** |  required  | The Container ID to associate the file with | string | 
**extension_filter** |  optional  | Comma-separated list of file extensions to be returned from the issue | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.container_id | string |  |   234 
action_result.parameter.extension_filter | string |  |   txt,png,exe 
action_result.parameter.id | string |  `jira ticket key`  |   AUA 
action_result.parameter.retrieve_all | boolean |  |   True  False 
action_result.data.\*.container | numeric |  |   2446 
action_result.data.\*.hash | string |  `md5`  |   9c03244555e41685dc5f03ec7d9de1c6db26c318 
action_result.data.\*.id | numeric |  |   501 
action_result.data.\*.message | string |  |   success 
action_result.data.\*.size | numeric |  |   231003 
action_result.data.\*.succeeded | boolean |  |   True  False 
action_result.data.\*.vault_id | string |  `vault id`  |   9c03244555e41685dc5f03ec7d9de1c6db26c318 
action_result.summary | string |  |  
action_result.message | string |  |   Successfully retrieved attachments from Jira ticket 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'update ticket'
Update ticket (issue)

Type: **generic**  
Read only: **False**

Update an existing issue with the values specified in the <b>update_fields</b> parameter.<br>The results of the <b>get ticket</b> action may be used to obtain the <b>update_fields</b> parameters, including any custom fields present in the JIRA.</br>The JSON specified in the <b>update_fields</b> parameter requires the keys and the values specified in case-sensitive and double-quotes string format, except in the case of boolean values, which should be either <i>true</i> or <i>false</i> for example:</br>{"summary": "Zeus, multiple action need to be taken", "description": "A new summary was added"}</br></br>The App supports multiple methods for specifying the input dictionary. Please see <a href="https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#editing-an-issue-examples" target='_blank'><b>the Atlassian documentation for the JIRA REST <i>update issue</i> API</b></a> for more information.<br>The following formats can be passed as input: <ul><li>Simple format; Create a dictionary with all the fields that need to be set:<br>{"summary": "Zeus detected on endpoint", "description": "Investigate further"}</li><li>Using the <i>update</i> key; Some issue fields support operations like <i>remove</i> and <i>add</i>, these operations can be combined to update a ticket: <br>{"<b>update</b>": {"components" : [{"remove" : {"name" : "secondcomponent"}}, {"add" : {"name" : "firstcomponent"}}]}}<br>{"<b>update</b>": {"comment": [{"add": {"body": "test comment update"}}]}} </li><li>Using the <i>fields</i> key;</br>{"<b>fields</b>":{"labels" : ["FIRSTLABEL"]}}</li></ul></br>The app supports updating custom fields; depending on the custom field type, some operations might not be available. Review the <b>jira_app</b> playbook for examples.<br><br>The <b>vault_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket.<br><br>This action requires that either the <b>update_fields</b> parameter or the <b>vault_id</b> parameter is filled out. The action will fail if it either unsuccessfully attempts to add the attachment to the ticket or update the fields on the ticket.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to update fields related to user resources in the Jira ticket using username for Jira cloud, we will use the user's account_id to update fields related to user resources. Use 'lookup users' action to find out user's account_id. Use 'get ticket' action results to obtain the [update_fields] parameters. Please find out below-mentioned examples for the [update_fields] parameter which is related to user resources.<ul><li>Add assignee to the Jira ticket for Jira on-prem:<br>{"fields":{"assignee" : {"name": "username"}}}</li><li>Add assignee to the Jira ticket for Jira cloud:<br>{"fields":{"assignee" : {"accountId": "6d1ef6xy52z7360c267f27bb"}}}</li></ul>.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**update_fields** |  optional  | JSON containing field values | string | 
**vault_id** |  optional  | Vault ID of attachment | string |  `vault id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.id | string |  `jira ticket key`  |   MAN-1 
action_result.parameter.update_fields | string |  |   {"update": {"comment": [{"add": {"body": "test comment update"}}]}}  { "priority":{ "name": "test/\\""}}  {"fields":{"test-label" : ["test"]}} 
action_result.parameter.vault_id | string |  `vault id`  |   fe3ac82064175835a67c279cbb9373f96c367566 
action_result.data.\*.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields.Epic Link | string |  |  
action_result.data.\*.fields.Sprint | string |  |   com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1] 
action_result.data.\*.fields.aggregateprogress.progress | numeric |  |   0 
action_result.data.\*.fields.aggregateprogress.total | numeric |  |   0 
action_result.data.\*.fields.aggregatetimeestimate | string |  |  
action_result.data.\*.fields.aggregatetimeoriginalestimate | string |  |  
action_result.data.\*.fields.aggregatetimespent | string |  |  
action_result.data.\*.fields.assignee | string |  |  
action_result.data.\*.fields.assignee.accountId | string |  `jira user account id`  |   5d2ef6ab52a8370c567f27bb 
action_result.data.\*.fields.assignee.accountType | string |  |   atlassian 
action_result.data.\*.fields.assignee.active | boolean |  |   False  True 
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.displayName | string |  `jira user display name`  |   Test Name 
action_result.data.\*.fields.assignee.emailAddress | string |  `email`  |   abc@domain.com 
action_result.data.\*.fields.assignee.key | string |  |   test 
action_result.data.\*.fields.assignee.name | string |  `user name`  |   test 
action_result.data.\*.fields.assignee.self | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.timeZone | string |  |  
action_result.data.\*.fields.attachment.\*.author.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.attachment.\*.author.accountType | string |  |   atlassian 
action_result.data.\*.fields.attachment.\*.author.active | boolean |  |   True  False 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.attachment.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.attachment.\*.author.key | string |  |   admin 
action_result.data.\*.fields.attachment.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.attachment.\*.author.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.attachment.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.attachment.\*.content | string |  `url`  |   http://jira.instance.ip/secure/attachment/10403/Add+Comment.png 
action_result.data.\*.fields.attachment.\*.created | string |  |   2018-09-19T18:15:01.060-0700 
action_result.data.\*.fields.attachment.\*.filename | string |  |   Add Comment.png 
action_result.data.\*.fields.attachment.\*.id | string |  |   10403 
action_result.data.\*.fields.attachment.\*.mimeType | string |  |   image/png 
action_result.data.\*.fields.attachment.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/attachment/10403 
action_result.data.\*.fields.attachment.\*.size | numeric |  |   97613 
action_result.data.\*.fields.attachment.\*.thumbnail | string |  `url`  |   http://jira.instance.ip/secure/thumbnail/10403/_thumb_10403.png 
action_result.data.\*.fields.comment.comments.\*.author.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.author.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.self | string |  `url`  |   http://1jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.body | string |  |   This is a sample testing body for the comment 
action_result.data.\*.fields.comment.comments.\*.created | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.id | string |  |   10004 
action_result.data.\*.fields.comment.comments.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.updated | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.visibility.type | string |  |   group  role 
action_result.data.\*.fields.comment.comments.\*.visibility.value | string |  |   jira-software-users 
action_result.data.\*.fields.comment.maxResults | numeric |  |   7 
action_result.data.\*.fields.comment.startAt | numeric |  |   0 
action_result.data.\*.fields.comment.total | numeric |  |   7 
action_result.data.\*.fields.components.\*.id | string |  |   10104 
action_result.data.\*.fields.components.\*.name | string |  |   comp_test1 
action_result.data.\*.fields.components.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/component/10104 
action_result.data.\*.fields.created | string |  |   2016-03-13T13:22:08.254-0700 
action_result.data.\*.fields.creator.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.creator.accountType | string |  |   atlassian 
action_result.data.\*.fields.creator.active | boolean |  |   False  True 
action_result.data.\*.fields.creator.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.creator.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.creator.key | string |  |   admin 
action_result.data.\*.fields.creator.name | string |  `user name`  |   admin 
action_result.data.\*.fields.creator.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.creator.timeZone | string |  |   UTC 
action_result.data.\*.fields.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields.duedate | string |  |  
action_result.data.\*.fields.environment | string |  |   above ground 
action_result.data.\*.fields.fixVersions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.id | string |  |   10000 
action_result.data.\*.fields.fixVersions.\*.name | string |  |   1.0 
action_result.data.\*.fields.fixVersions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.issuelinks.\*.id | string |  |   10615 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric |  |   10300 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string |  |   gh.issue.epic.desc 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string |  |   http://jira.instance.ip/images/icons/issuetypes/epic.svg 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string |  |   10100 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string |  |   Epic 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string |  |   http://jira.instance.ip/rest/api/2/issuetype/10100 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean |  |   False 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string |  |   http://jira.instance.ip/images/border/spacer.gif 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string |  |   10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string |  |   High 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string |  |   http://jira.instance.ip/rest/api/2/priority/10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string |  |   The issue is open and ready for the assignee to start work on it. 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string |  |   http://jira.instance.ip/images/icons/statuses/generic.png 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string |  |   10500 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string |  |   Done 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string |  |   http://jira.instance.ip/rest/api/2/status/10500 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string |  |   yellow 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric |  |   4 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string |  |   indeterminate 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string |  |   In Progress 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string |  |   http://jira.instance.ip/rest/api/2/statuscategory/4 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string |  |   Test epic 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string |  |   21237 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string |  |   SPOL-133 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string |  |   http://jira.instance.ip/rest/api/2/issue/21237 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string |  |   This Issue Type is used to create Zephyr Test within Jira 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/download/resources/com.thed.zephyr.je/images/icons/ico_zephyr_issuetype.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string |  |   10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string |  |   Test 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean |  |   True  False 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/high.svg 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string |  |   High 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string |  |  
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string |  |   Mission Control Functionality 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string |  |   11849 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string |  `jira ticket key`  |   ZEP-14 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/11849 
action_result.data.\*.fields.issuelinks.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLink/10615 
action_result.data.\*.fields.issuelinks.\*.type.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.type.inward | string |  |   is blocked by 
action_result.data.\*.fields.issuelinks.\*.type.name | string |  |   Blocks 
action_result.data.\*.fields.issuelinks.\*.type.outward | string |  |   blocks 
action_result.data.\*.fields.issuelinks.\*.type.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLinkType/10000 
action_result.data.\*.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuetype.description | string |  |   A problem which impairs or prevents the functions of the product 
action_result.data.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype 
action_result.data.\*.fields.issuetype.id | string |  |   1 
action_result.data.\*.fields.issuetype.name | string |  `jira issue type`  |   Defect 
action_result.data.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/1 
action_result.data.\*.fields.issuetype.subtask | boolean |  |   False  True 
action_result.data.\*.fields.labels | string |  |   test51 
action_result.data.\*.fields.lastViewed | string |  |   2018-09-20T23:54:50.643-0700 
action_result.data.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.progress.progress | numeric |  |   0 
action_result.data.\*.fields.progress.total | numeric |  |   0 
action_result.data.\*.fields.project.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=xsmall&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=small&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=medium&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?avatarId=10403 
action_result.data.\*.fields.project.id | string |  |   10100 
action_result.data.\*.fields.project.key | string |  `jira project key`  |   MAN 
action_result.data.\*.fields.project.name | string |  |   TestProject 
action_result.data.\*.fields.project.projectCategory.description | string |  |   test 
action_result.data.\*.fields.project.projectCategory.id | string |  |   10000 
action_result.data.\*.fields.project.projectCategory.name | string |  |   QA-Team 
action_result.data.\*.fields.project.projectCategory.self | string |  |   https://testlab.atlassian.net/rest/api/2/projectCategory/10000 
action_result.data.\*.fields.project.projectTypeKey | string |  |   software 
action_result.data.\*.fields.project.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/project/10100 
action_result.data.\*.fields.project.simplified | boolean |  |   False  True 
action_result.data.\*.fields.reporter.accountType | string |  |   atlassian 
action_result.data.\*.fields.reporter.active | boolean |  |   False  True 
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.reporter.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.reporter.key | string |  |   admin 
action_result.data.\*.fields.reporter.name | string |  `user name`  |   admin 
action_result.data.\*.fields.reporter.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.reporter.timeZone | string |  |   UTC 
action_result.data.\*.fields.resolution | string |  |  
action_result.data.\*.fields.resolution.description | string |  |   Work has been completed on this issue 
action_result.data.\*.fields.resolution.id | string |  |   10000 
action_result.data.\*.fields.resolution.name | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.fields.resolution.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/resolution/10000 
action_result.data.\*.fields.resolutiondate | string |  |   2018-09-20T19:02:38.646-0700 
action_result.data.\*.fields.security | string |  |  
action_result.data.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/closed.png 
action_result.data.\*.fields.status.id | string |  |   10001 
action_result.data.\*.fields.status.name | string |  |   Done 
action_result.data.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10001 
action_result.data.\*.fields.status.statusCategory.colorName | string |  |   green 
action_result.data.\*.fields.status.statusCategory.id | numeric |  |   3 
action_result.data.\*.fields.status.statusCategory.key | string |  |   done 
action_result.data.\*.fields.status.statusCategory.name | string |  |   Done 
action_result.data.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/3 
action_result.data.\*.fields.statuscategorychangedate | string |  |   2019-07-22T22:43:07.771-0700 
action_result.data.\*.fields.summary | string |  |   Sample summary 
action_result.data.\*.fields.timeestimate | string |  |  
action_result.data.\*.fields.timeoriginalestimate | string |  |  
action_result.data.\*.fields.timespent | string |  |  
action_result.data.\*.fields.updated | string |  |   2018-09-25T06:49:43.523-0700 
action_result.data.\*.fields.versions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.id | string |  |   10000 
action_result.data.\*.fields.versions.\*.name | string |  |   1.0 
action_result.data.\*.fields.versions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.votes.hasVoted | boolean |  |   False  True 
action_result.data.\*.fields.votes.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/votes 
action_result.data.\*.fields.votes.votes | numeric |  |   0 
action_result.data.\*.fields.watches.isWatching | boolean |  |   False  True 
action_result.data.\*.fields.watches.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers 
action_result.data.\*.fields.watches.watchCount | numeric |  |   1 
action_result.data.\*.fields.worklog.maxResults | numeric |  |   20 
action_result.data.\*.fields.worklog.startAt | numeric |  |   0 
action_result.data.\*.fields.worklog.total | numeric |  |   0 
action_result.data.\*.fields.workratio | numeric |  |   -1 
action_result.data.\*.id | string |  |   10246 
action_result.data.\*.issue_type | string |  `jira issue type`  |   Defect 
action_result.data.\*.name | string |  `jira ticket key`  |   MAN-1 
action_result.data.\*.priority | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.project_key | string |  `jira project key`  |   MAN 
action_result.data.\*.reporter | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.resolution | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.status | string |  |   Done 
action_result.data.\*.summary | string |  |   Sample summary 
action_result.summary | string |  |  
action_result.message | string |  |   Successfully updated ticket 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add comment'
Add a comment to the ticket (issue)

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**comment** |  required  | Comment to add | string | 
**internal** |  optional  | Whether comment should be internal only or not in Jira Service Desk (if the value is not provided, it will internally be treated as 'false') | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.comment | string |  |   test comment 
action_result.parameter.id | string |  `jira ticket key`  |   MAN-1 
action_result.parameter.internal | boolean |  |   True  False 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully added comment 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'delete ticket'
Delete ticket (issue)

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.id | string |  `jira ticket key`  |   MAN-240 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully deleted ticket 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list projects'
List all projects

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.data.\*.id | string |  |   10207 
action_result.data.\*.name | string |  |   Access Uplift Alerts 
action_result.data.\*.project_key | string |  `jira project key`  |   AUA 
action_result.summary.total_projects | numeric |  |   16 
action_result.message | string |  |   Total projects: 16 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list tickets'
Get a list of tickets (issues) in a specified project

Type: **investigate**  
Read only: **True**

The default value for the parameter <b>'start_index'</b> is <b>0</b> and for <b>'max_results'</b> is <b>1000</b>. The maximum number of tickets as specified by the parameter <b>'max_results'</b> will be fetched starting from the index specified by the parameter <b>'start_index'</b>.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project_key** |  required  | Project key to list the tickets (issues) of | string |  `jira project key` 
**query** |  optional  | Additional parameters to query for in JQL | string | 
**start_index** |  optional  | Start index of the list | numeric | 
**max_results** |  optional  | Maximum number of issues to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.max_results | numeric |  |   50 
action_result.parameter.project_key | string |  `jira project key`  |   PRJ 
action_result.parameter.query | string |  |  
action_result.parameter.start_index | numeric |  |  
action_result.data.\*.description | string |  `url`  |   This is a sample testing description 
action_result.data.\*.fields.aggregateprogress.progress | numeric |  |   0 
action_result.data.\*.fields.aggregateprogress.total | numeric |  |   0 
action_result.data.\*.fields.aggregatetimeestimate | string |  |  
action_result.data.\*.fields.aggregatetimeoriginalestimate | string |  |  
action_result.data.\*.fields.aggregatetimespent | string |  |  
action_result.data.\*.fields.assignee | string |  |  
action_result.data.\*.fields.assignee.accountId | string |  `jira user account id`  |   5d2ef6ab52a8370c567f27bb 
action_result.data.\*.fields.assignee.accountType | string |  |   atlassian 
action_result.data.\*.fields.assignee.active | boolean |  |   False  True 
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.assignee.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.assignee.key | string |  |   admin 
action_result.data.\*.fields.assignee.name | string |  `user name`  |   admin 
action_result.data.\*.fields.assignee.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.assignee.timeZone | string |  |   UTC 
action_result.data.\*.fields.attachment.\*.author.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.attachment.\*.author.accountType | string |  |   atlassian 
action_result.data.\*.fields.comment.comments.\*.visibility.type | string |  |   group  role 
action_result.data.\*.fields.comment.comments.\*.visibility.value | string |  |   jira-software-users 
action_result.data.\*.fields.comment.maxResults | numeric |  |  
action_result.data.\*.fields.comment.startAt | numeric |  |  
action_result.data.\*.fields.comment.total | numeric |  |  
action_result.data.\*.fields.created | string |  |   2018-09-23T19:40:35.000-0700 
action_result.data.\*.fields.creator.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.creator.accountType | string |  |   atlassian 
action_result.data.\*.fields.creator.active | boolean |  |   False  True 
action_result.data.\*.fields.creator.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.creator.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.creator.key | string |  |   admin 
action_result.data.\*.fields.creator.name | string |  `user name`  |   admin 
action_result.data.\*.fields.creator.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.creator.timeZone | string |  |   UTC 
action_result.data.\*.fields.description | string |  `url`  |   This is a sample testing description 
action_result.data.\*.fields.duedate | string |  |  
action_result.data.\*.fields.environment | string |  |  
action_result.data.\*.fields.issuelinks.\*.id | string |  |   10615 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string |  |   This Issue Type is used to create Zephyr Test within Jira 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/download/resources/com.thed.zephyr.je/images/icons/ico_zephyr_issuetype.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string |  |   10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string |  |   Test 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean |  |   True  False 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/high.svg 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string |  `jira ticket priority`  |   High 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string |  |   This is a sample fields status description 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string |  |   Mission Control Functionality 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string |  |   11849 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string |  `jira ticket key`  |   ZEP-14 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/11849 
action_result.data.\*.fields.issuelinks.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLink/10615 
action_result.data.\*.fields.issuelinks.\*.type.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.type.inward | string |  |   is blocked by 
action_result.data.\*.fields.issuelinks.\*.type.name | string |  |   Blocks 
action_result.data.\*.fields.issuelinks.\*.type.outward | string |  |   blocks 
action_result.data.\*.fields.issuelinks.\*.type.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLinkType/10000 
action_result.data.\*.fields.issuetype.avatarId | numeric |  |   10316 
action_result.data.\*.fields.issuetype.description | string |  |   The sub-task of the issue 
action_result.data.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype 
action_result.data.\*.fields.issuetype.id | string |  |   5 
action_result.data.\*.fields.issuetype.name | string |  `jira issue type`  |   Sub-Task 
action_result.data.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/5 
action_result.data.\*.fields.issuetype.subtask | boolean |  |   False  True 
action_result.data.\*.fields.lastViewed | string |  |   2018-09-23T22:28:12.754-0700 
action_result.data.\*.fields.parent.fields.issuetype.avatarId | numeric |  |   10318 
action_result.data.\*.fields.parent.fields.issuetype.description | string |  |   A task that needs to be done 
action_result.data.\*.fields.parent.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype 
action_result.data.\*.fields.parent.fields.issuetype.id | string |  |   3 
action_result.data.\*.fields.parent.fields.issuetype.name | string |  `jira issue type`  |   Task 
action_result.data.\*.fields.parent.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/3 
action_result.data.\*.fields.parent.fields.issuetype.subtask | boolean |  |   True  False 
action_result.data.\*.fields.parent.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.parent.fields.priority.id | string |  |   3 
action_result.data.\*.fields.parent.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.parent.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.parent.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.parent.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.parent.fields.status.id | string |  |   10000 
action_result.data.\*.fields.parent.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.parent.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.parent.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.parent.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.parent.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.parent.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.parent.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.parent.fields.summary | string |  |   Phishing Investigation: The other way of doing this without a logo 
action_result.data.\*.fields.parent.id | string |  |   11811 
action_result.data.\*.fields.parent.key | string |  |   PHANINCIDE-315 
action_result.data.\*.fields.parent.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/11811 
action_result.data.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.progress.progress | numeric |  |   0 
action_result.data.\*.fields.progress.total | numeric |  |   0 
action_result.data.\*.fields.project.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=xsmall&pid=10000&avatarId=10011 
action_result.data.\*.fields.project.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=small&pid=10000&avatarId=10011 
action_result.data.\*.fields.project.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=medium&pid=10000&avatarId=10011 
action_result.data.\*.fields.project.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?pid=10000&avatarId=10011 
action_result.data.\*.fields.project.id | string |  |   10000 
action_result.data.\*.fields.project.key | string |  `jira project key`  |   PRJ 
action_result.data.\*.fields.project.name | string |  |   Test Create Incidents 
action_result.data.\*.fields.project.projectCategory.description | string |  |   test 
action_result.data.\*.fields.project.projectCategory.id | string |  |   10000 
action_result.data.\*.fields.project.projectCategory.name | string |  |   QA-Team 
action_result.data.\*.fields.project.projectCategory.self | string |  |   https://testlab.atlassian.net/rest/api/2/projectCategory/10000 
action_result.data.\*.fields.project.projectTypeKey | string |  |   software 
action_result.data.\*.fields.project.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/project/10000 
action_result.data.\*.fields.project.simplified | boolean |  |   False  True 
action_result.data.\*.fields.reporter.accountType | string |  |   atlassian 
action_result.data.\*.fields.reporter.active | boolean |  |   False  True 
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.reporter.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.reporter.key | string |  |   admin 
action_result.data.\*.fields.reporter.name | string |  `user name`  |   admin 
action_result.data.\*.fields.reporter.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.reporter.timeZone | string |  |   UTC 
action_result.data.\*.fields.resolution | string |  |  
action_result.data.\*.fields.resolution.description | string |  |   A fix for this issue is checked into the tree and tested 
action_result.data.\*.fields.resolution.id | string |  |   1 
action_result.data.\*.fields.resolution.name | string |  `jira ticket resolution`  |   Fixed 
action_result.data.\*.fields.resolution.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/resolution/1 
action_result.data.\*.fields.resolutiondate | string |  |   2018-09-23T19:40:35.000-0700 
action_result.data.\*.fields.security | string |  |  
action_result.data.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.status.id | string |  |   10000 
action_result.data.\*.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.statuscategorychangedate | string |  |   2019-07-22T22:43:07.771-0700 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.avatarId | numeric |  |   10316 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.description | string |  |   The sub-task of the issue 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.id | string |  |   5 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.name | string |  `jira issue type`  |   Sub-Task 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/5 
action_result.data.\*.fields.subtasks.\*.fields.issuetype.subtask | boolean |  |   True  False 
action_result.data.\*.fields.subtasks.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.subtasks.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.subtasks.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.subtasks.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.subtasks.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.subtasks.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.subtasks.\*.fields.status.id | string |  |   10000 
action_result.data.\*.fields.subtasks.\*.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.subtasks.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.subtasks.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.subtasks.\*.fields.summary | string |  |   Sub-taskofBigTask 
action_result.data.\*.fields.subtasks.\*.id | string |  |   11839 
action_result.data.\*.fields.subtasks.\*.key | string |  |   PHANINCIDE-316 
action_result.data.\*.fields.subtasks.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/11839 
action_result.data.\*.fields.summary | string |  |   Sub-taskofBigTask 
action_result.data.\*.fields.timeestimate | string |  |  
action_result.data.\*.fields.timeoriginalestimate | string |  |  
action_result.data.\*.fields.timespent | string |  |  
action_result.data.\*.fields.updated | string |  |   2018-09-23T22:28:12.000-0700 
action_result.data.\*.fields.votes.hasVoted | boolean |  |   False  True 
action_result.data.\*.fields.votes.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/PHANINCIDE-317/votes 
action_result.data.\*.fields.votes.votes | numeric |  |   0 
action_result.data.\*.fields.watches.isWatching | boolean |  |   False  True 
action_result.data.\*.fields.watches.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/PHANINCIDE-317/watchers 
action_result.data.\*.fields.watches.watchCount | numeric |  |   1 
action_result.data.\*.fields.worklog.maxResults | numeric |  |  
action_result.data.\*.fields.worklog.startAt | numeric |  |  
action_result.data.\*.fields.worklog.total | numeric |  |  
action_result.data.\*.fields.workratio | numeric |  |   -1 
action_result.data.\*.id | string |  |   11840 
action_result.data.\*.issue_type | string |  `jira issue type`  |   Sub-Task 
action_result.data.\*.name | string |  `jira ticket key`  |   PHANINCIDE-317 
action_result.data.\*.priority | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.project_key | string |  `jira project key`  |   PRJ 
action_result.data.\*.reporter | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.resolution | string |  `jira ticket resolution`  |   Unresolved 
action_result.data.\*.status | string |  |   To Do 
action_result.data.\*.summary | string |  |   Sub-taskofBigTask 
action_result.summary.total_issues | numeric |  |   50 
action_result.message | string |  |   Total issues: 50 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'lookup users'
Get a list of user resources that match the specified search string

Type: **investigate**  
Read only: **True**

This action will be used to fetch the username of user resources for Jira on-prem and account_id of user resources for Jira cloud. The default value for [max_results] action parameter is <b>1000</b>. The maximum number of users as specified by the parameter [max_results] will be fetched starting from the first.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to search users using username for Jira cloud, we will use the user's display name to search users. You can use the [display_name] action parameter to search users for Jira cloud, and, [username] action parameter will be used to search users for Jira on-prem.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**username** |  optional  | A string to match with usernames, name, or email against for JIRA on-prem (required for Jira on-prem) | string |  `user name` 
**display_name** |  optional  | A string to match with display name for JIRA cloud (required for Jira cloud) | string |  `jira user display name` 
**max_results** |  optional  | Maximum number of users to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.display_name | string |  `jira user display name`  |   Test Name 
action_result.parameter.max_results | numeric |  |   1000 
action_result.parameter.username | string |  `user name`  |   test 
action_result.data.\*.accountId | string |  `jira user account id`  |   5d2ef6aa6637260c19b78dfd 
action_result.data.\*.accountType | string |  |   atlassian 
action_result.data.\*.active | boolean |  |   True  False 
action_result.data.\*.avatarUrls.16x16 | string |  `url`  |   http://www.gravatar.com/avatar/da0ebe3acdd83aa3d82d1dbd1a15a3e1?d=mm&s=16 
action_result.data.\*.avatarUrls.24x24 | string |  `url`  |   http://www.gravatar.com/avatar/da0ebe3acdd83aa3d82d1dbd1a15a3e1?d=mm&s=24 
action_result.data.\*.avatarUrls.32x32 | string |  `url`  |   http://www.gravatar.com/avatar/da0ebe3acdd83aa3d82d1dbd1a15a3e1?d=mm&s=32 
action_result.data.\*.avatarUrls.48x48 | string |  `url`  |   http://www.gravatar.com/avatar/da0ebe3acdd83aa3d82d1dbd1a15a3e1?d=mm&s=48 
action_result.data.\*.displayName | string |  `jira user display name`  |   Test Name 
action_result.data.\*.emailAddress | string |  `email`  |   test@domain.us 
action_result.data.\*.key | string |  |   test 
action_result.data.\*.locale | string |  |   en_US 
action_result.data.\*.name | string |  `user name`  |   test 
action_result.data.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=test 
action_result.data.\*.timeZone | string |  |   America/Los_Angeles 
action_result.summary.total_users | numeric |  |   4 
action_result.message | string |  |   Total users: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get ticket'
Get ticket (issue) information

Type: **investigate**  
Read only: **True**

The keys in the <b>action_result.data.\*.fields</b> output section of the results can differ based on the JIRA server configuration.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket (issue) key | string |  `jira ticket key` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.id | string |  `jira ticket key`  |   MAN-1 
action_result.data.\*.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields.Epic Link | string |  |  
action_result.data.\*.fields.Sprint | string |  |   com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1] 
action_result.data.\*.fields.aggregateprogress.progress | numeric |  |   0 
action_result.data.\*.fields.aggregateprogress.total | numeric |  |   0 
action_result.data.\*.fields.aggregatetimeestimate | string |  |  
action_result.data.\*.fields.aggregatetimeoriginalestimate | string |  |  
action_result.data.\*.fields.aggregatetimespent | string |  |  
action_result.data.\*.fields.assignee | string |  |  
action_result.data.\*.fields.assignee.accountId | string |  `jira user account id`  |   5d2ef6ab52a8370c567f27bb 
action_result.data.\*.fields.assignee.accountType | string |  |   atlassian 
action_result.data.\*.fields.assignee.active | boolean |  |   False  True 
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string |  `url`  |  
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.displayName | string |  `jira user display name`  |  
action_result.data.\*.fields.assignee.emailAddress | string |  `email`  |   abc@domain.com 
action_result.data.\*.fields.assignee.key | string |  |   admin 
action_result.data.\*.fields.assignee.name | string |  `user name`  |   admin 
action_result.data.\*.fields.assignee.self | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.timeZone | string |  |  
action_result.data.\*.fields.attachment.\*.author.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.attachment.\*.author.accountType | string |  |   atlassian 
action_result.data.\*.fields.attachment.\*.author.active | boolean |  |   False  True 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.attachment.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.attachment.\*.author.key | string |  |   admin 
action_result.data.\*.fields.attachment.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.attachment.\*.author.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.attachment.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.attachment.\*.content | string |  `url`  |   http://jira.instance.ip/secure/attachment/10403/Add+Comment.png 
action_result.data.\*.fields.attachment.\*.created | string |  |   2018-09-19T18:15:01.060-0700 
action_result.data.\*.fields.attachment.\*.filename | string |  |   Add Comment.png 
action_result.data.\*.fields.attachment.\*.id | string |  |   10403 
action_result.data.\*.fields.attachment.\*.mimeType | string |  |   image/png 
action_result.data.\*.fields.attachment.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/attachment/10403 
action_result.data.\*.fields.attachment.\*.size | numeric |  |   97613 
action_result.data.\*.fields.attachment.\*.thumbnail | string |  `url`  |   http://jira.instance.ip/secure/thumbnail/10403/_thumb_10403.png 
action_result.data.\*.fields.comment.comments.\*.author.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.author.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.body | string |  |   This is a sample testing comment body 
action_result.data.\*.fields.comment.comments.\*.created | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.id | string |  |   10004 
action_result.data.\*.fields.comment.comments.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.updated | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.visibility.type | string |  |   group  role 
action_result.data.\*.fields.comment.comments.\*.visibility.value | string |  |   jira-software-users 
action_result.data.\*.fields.comment.maxResults | numeric |  |   5 
action_result.data.\*.fields.comment.startAt | numeric |  |   0 
action_result.data.\*.fields.comment.total | numeric |  |   5 
action_result.data.\*.fields.components.\*.id | string |  |   10104 
action_result.data.\*.fields.components.\*.name | string |  |   comp_test1 
action_result.data.\*.fields.components.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/component/10104 
action_result.data.\*.fields.created | string |  |   2016-03-13T13:22:08.254-0700 
action_result.data.\*.fields.creator.accountId | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.data.\*.fields.creator.accountType | string |  |   atlassian 
action_result.data.\*.fields.creator.active | boolean |  |   False  True 
action_result.data.\*.fields.creator.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.creator.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.creator.key | string |  |   admin 
action_result.data.\*.fields.creator.name | string |  `user name`  |   admin 
action_result.data.\*.fields.creator.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.creator.timeZone | string |  |   UTC 
action_result.data.\*.fields.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields.duedate | string |  |  
action_result.data.\*.fields.environment | string |  |   above ground 
action_result.data.\*.fields.fixVersions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.id | string |  |   10000 
action_result.data.\*.fields.fixVersions.\*.name | string |  |   1.0 
action_result.data.\*.fields.fixVersions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.issuelinks.\*.id | string |  |   10615 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric |  |   10300 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string |  |   gh.issue.epic.desc 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string |  |   http://jira.instance.ip/images/icons/issuetypes/epic.svg 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string |  |   10100 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string |  |   Epic 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string |  |   http://jira.instance.ip/rest/api/2/issuetype/10100 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean |  |   False 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string |  |   http://jira.instance.ip/images/border/spacer.gif 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string |  |   10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string |  |   High 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string |  |   http://jira.instance.ip/rest/api/2/priority/10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string |  |   The issue is open and ready for the assignee to start work on it. 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string |  |   http://jira.instance.ip/images/icons/statuses/generic.png 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string |  |   10500 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string |  |   Done 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string |  |   http://jira.instance.ip/rest/api/2/status/10500 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string |  |   yellow 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric |  |   4 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string |  |   indeterminate 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string |  |   In Progress 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string |  |   http://jira.instance.ip/rest/api/2/statuscategory/4 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string |  |   Test epic 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string |  |   21237 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string |  |   SPOL-133 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string |  |   http://jira.instance.ip/rest/api/2/issue/21237 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string |  |   This Issue Type is used to create Zephyr Test within Jira 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/download/resources/com.thed.zephyr.je/images/icons/ico_zephyr_issuetype.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string |  |   10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string |  |   Test 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/10400 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean |  |   True  False 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/high.svg 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string |  `jira ticket priority`  |   High 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string |  |  
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10000 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string |  |   Mission Control Functionality 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string |  |   11849 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string |  `jira ticket key`  |   ZEP-14 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/11849 
action_result.data.\*.fields.issuelinks.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLink/10615 
action_result.data.\*.fields.issuelinks.\*.type.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.type.inward | string |  |   is blocked by 
action_result.data.\*.fields.issuelinks.\*.type.name | string |  |   Blocks 
action_result.data.\*.fields.issuelinks.\*.type.outward | string |  |   blocks 
action_result.data.\*.fields.issuelinks.\*.type.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issueLinkType/10000 
action_result.data.\*.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuetype.description | string |  |   A problem which impairs or prevents the functions of the product 
action_result.data.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype 
action_result.data.\*.fields.issuetype.id | string |  |   1 
action_result.data.\*.fields.issuetype.name | string |  `jira issue type`  |   Defect 
action_result.data.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/1 
action_result.data.\*.fields.issuetype.subtask | boolean |  |   False  True 
action_result.data.\*.fields.labels | string |  |   area51 
action_result.data.\*.fields.lastViewed | string |  |   2018-09-20T23:54:50.643-0700 
action_result.data.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.progress.progress | numeric |  |   0 
action_result.data.\*.fields.progress.total | numeric |  |   0 
action_result.data.\*.fields.project.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=xsmall&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=small&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=medium&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?avatarId=10403 
action_result.data.\*.fields.project.id | string |  |   10100 
action_result.data.\*.fields.project.key | string |  `jira project key`  |   MAN 
action_result.data.\*.fields.project.name | string |  |   TestProject 
action_result.data.\*.fields.project.projectCategory.description | string |  |   test 
action_result.data.\*.fields.project.projectCategory.id | string |  |   10000 
action_result.data.\*.fields.project.projectCategory.name | string |  |   QA-Team 
action_result.data.\*.fields.project.projectCategory.self | string |  |   https://testlab.atlassian.net/rest/api/2/projectCategory/10000 
action_result.data.\*.fields.project.projectTypeKey | string |  |   software 
action_result.data.\*.fields.project.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/project/10100 
action_result.data.\*.fields.project.simplified | boolean |  |   False  True 
action_result.data.\*.fields.reporter.accountType | string |  |   atlassian 
action_result.data.\*.fields.reporter.active | boolean |  |   False  True 
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.reporter.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.reporter.key | string |  |   admin 
action_result.data.\*.fields.reporter.name | string |  `user name`  |   admin 
action_result.data.\*.fields.reporter.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.reporter.timeZone | string |  |   UTC 
action_result.data.\*.fields.resolution | string |  |  
action_result.data.\*.fields.resolution.description | string |  |   Work has been completed on this issue 
action_result.data.\*.fields.resolution.id | string |  |   10000 
action_result.data.\*.fields.resolution.name | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.fields.resolution.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/resolution/10000 
action_result.data.\*.fields.resolutiondate | string |  |   2018-09-20T19:02:38.646-0700 
action_result.data.\*.fields.security | string |  |  
action_result.data.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/closed.png 
action_result.data.\*.fields.status.id | string |  |   10001 
action_result.data.\*.fields.status.name | string |  |   Done 
action_result.data.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10001 
action_result.data.\*.fields.status.statusCategory.colorName | string |  |   green 
action_result.data.\*.fields.status.statusCategory.id | numeric |  |   3 
action_result.data.\*.fields.status.statusCategory.key | string |  |   done 
action_result.data.\*.fields.status.statusCategory.name | string |  |   Done 
action_result.data.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/3 
action_result.data.\*.fields.statuscategorychangedate | string |  |   2019-07-22T22:43:07.771-0700 
action_result.data.\*.fields.summary | string |  |   Sample summary 
action_result.data.\*.fields.timeestimate | string |  |  
action_result.data.\*.fields.timeoriginalestimate | string |  |  
action_result.data.\*.fields.timespent | string |  |  
action_result.data.\*.fields.updated | string |  |   2018-09-25T06:21:27.802-0700 
action_result.data.\*.fields.versions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.id | string |  |   10000 
action_result.data.\*.fields.versions.\*.name | string |  |   1.0 
action_result.data.\*.fields.versions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.votes.hasVoted | boolean |  |   False  True 
action_result.data.\*.fields.votes.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/votes 
action_result.data.\*.fields.votes.votes | numeric |  |   0 
action_result.data.\*.fields.watches.isWatching | boolean |  |   False  True 
action_result.data.\*.fields.watches.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers 
action_result.data.\*.fields.watches.watchCount | numeric |  |   1 
action_result.data.\*.fields.worklog.maxResults | numeric |  |   20 
action_result.data.\*.fields.worklog.startAt | numeric |  |   0 
action_result.data.\*.fields.worklog.total | numeric |  |   0 
action_result.data.\*.fields.workratio | numeric |  |   -1 
action_result.data.\*.id | string |  |   10246 
action_result.data.\*.issue_type | string |  `jira issue type`  |   Defect 
action_result.data.\*.name | string |  `jira ticket key`  |   MAN-1 
action_result.data.\*.priority | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.project_key | string |  `jira project key`  |   MAN 
action_result.data.\*.reporter | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.resolution | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.status | string |  |   Done 
action_result.data.\*.summary | string |  |   Sample summary 
action_result.summary | string |  |  
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'set status'
Set ticket (issue) status

Type: **generic**  
Read only: **False**

In JIRA, the status transition of an issue is determined by the workflow defined for the project. The app will return an error if an un-allowed status transition is attempted. In such cases, the possible statuses are returned based on the issue's current status value.<br>The same is the case for invalid resolutions. Do note that some combinations of status and resolution values might be invalid, even if they are allowed individually.<br>To get valid values to use as input for the parameters:<ul><li>For valid <b>status</b> values:<ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/issue/<i>[jira_issue_key]</i>/transitions</li><li>The returned JSON should contain a list of transitions</li><li>The name field denotes the status that can be set using this action</li></ul></li><li>For valid <b>resolution</b> values: <ul><li>Log in to the JIRA server from the UI</li><li>Go to http://my_jira_ip/rest/api/2/resolution</li><li>The returned JSON should contain a list of resolutions</li><li>The name field in each resolution denotes the value to be used</li></ul></li></ul>.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket (issue) key | string |  `jira ticket key` 
**status** |  required  | Status to set | string |  `jira ticket status` 
**resolution** |  optional  | Resolution to set | string |  `jira ticket resolution` 
**comment** |  optional  | Comment to set | string | 
**update_fields** |  optional  | JSON containing field values | string | 
**time_spent** |  optional  | Time Spent to Log | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.comment | string |  |   This is a sample status change comment of the ticket 
action_result.parameter.id | string |  `jira ticket key`  |   MAN-1 
action_result.parameter.resolution | string |  `jira ticket resolution`  |   In Progress 
action_result.parameter.status | string |  `jira ticket status`  |   Done 
action_result.parameter.time_spent | string |  |   3w 4d 12h 
action_result.parameter.update_fields | string |  |   {"update": {"comment": [{"add": {"body": "test comment update"}}]}}  { "priority":{ "name": "test/\\""}}  {"fields":{"test-label" : ["test"]}} 
action_result.data.\*.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields. | string |  |  
action_result.data.\*.fields.Epic Link | string |  |  
action_result.data.\*.fields.Severity | string |  |  
action_result.data.\*.fields.Sprint | string |  |   com.atlassian.greenhopper.service.sprint.Sprint@6bb9ab97[id=1,rapidViewId=1,state=ACTIVE,name=MAN Sprint 1,startDate=2017-10-30T16:22:44.954-07:00,endDate=2017-11-13T16:22:00.000-08:00,completeDate=<null>,sequence=1] 
action_result.data.\*.fields.aggregateprogress.percent | numeric |  |   100 
action_result.data.\*.fields.aggregateprogress.progress | numeric |  |   0 
action_result.data.\*.fields.aggregateprogress.total | numeric |  |   0 
action_result.data.\*.fields.aggregatetimeestimate | numeric |  |  
action_result.data.\*.fields.aggregatetimeoriginalestimate | string |  |  
action_result.data.\*.fields.aggregatetimespent | numeric |  |  
action_result.data.\*.fields.assignee | string |  |  
action_result.data.\*.fields.assignee.active | boolean |  |   False  True 
action_result.data.\*.fields.assignee.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.displayName | string |  `jira user display name`  |   Test Name 
action_result.data.\*.fields.assignee.emailAddress | string |  `email`  |   abc@domain.com 
action_result.data.\*.fields.assignee.key | string |  |   admin 
action_result.data.\*.fields.assignee.name | string |  `user name`  |   admin 
action_result.data.\*.fields.assignee.self | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.assignee.timeZone | string |  |  
action_result.data.\*.fields.attachment.\*.author.active | boolean |  |   True  False 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.attachment.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.attachment.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.attachment.\*.author.key | string |  |   admin 
action_result.data.\*.fields.attachment.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.attachment.\*.author.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.attachment.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.attachment.\*.content | string |  `url`  |   http://jira.instance.ip/secure/attachment/10403/Add+Comment.png 
action_result.data.\*.fields.attachment.\*.created | string |  |   2018-09-19T18:15:01.060-0700 
action_result.data.\*.fields.attachment.\*.filename | string |  |   Add Comment.png 
action_result.data.\*.fields.attachment.\*.id | string |  |   10403 
action_result.data.\*.fields.attachment.\*.mimeType | string |  |   image/png 
action_result.data.\*.fields.attachment.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/attachment/10403 
action_result.data.\*.fields.attachment.\*.size | numeric |  |   97613 
action_result.data.\*.fields.attachment.\*.thumbnail | string |  `url`  |   http://jira.instance.ip/secure/thumbnail/10403/_thumb_10403.png 
action_result.data.\*.fields.comment.comments.\*.author.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.author.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.author.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.author.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.author.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.author.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.body | string |  |   This is a sample testing comment body 
action_result.data.\*.fields.comment.comments.\*.created | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.id | string |  |   10004 
action_result.data.\*.fields.comment.comments.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/10246/comment/10004 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.active | boolean |  |   True  False 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.key | string |  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.name | string |  `user name`  |   admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.comment.comments.\*.updateAuthor.timeZone | string |  |   UTC 
action_result.data.\*.fields.comment.comments.\*.updated | string |  |   2016-03-15T17:11:49.767-0700 
action_result.data.\*.fields.comment.comments.\*.visibility.type | string |  |   role 
action_result.data.\*.fields.comment.comments.\*.visibility.value | string |  |   Users 
action_result.data.\*.fields.comment.maxResults | numeric |  |   5 
action_result.data.\*.fields.comment.startAt | numeric |  |   0 
action_result.data.\*.fields.comment.total | numeric |  |   5 
action_result.data.\*.fields.components.\*.id | string |  |   10104 
action_result.data.\*.fields.components.\*.name | string |  |   comp_test1 
action_result.data.\*.fields.components.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/component/10104 
action_result.data.\*.fields.created | string |  |   2016-03-13T13:22:08.254-0700 
action_result.data.\*.fields.creator.active | boolean |  |   False  True 
action_result.data.\*.fields.creator.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.creator.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.creator.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.creator.key | string |  |   admin 
action_result.data.\*.fields.creator.name | string |  |   admin 
action_result.data.\*.fields.creator.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.creator.timeZone | string |  |   UTC 
action_result.data.\*.fields.description | string |  |   This is a sample testing description of the ticket 
action_result.data.\*.fields.duedate | string |  |  
action_result.data.\*.fields.environment | string |  |   above ground 
action_result.data.\*.fields.fixVersions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.id | string |  |   10000 
action_result.data.\*.fields.fixVersions.\*.name | string |  |   1.0 
action_result.data.\*.fields.fixVersions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.fixVersions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.issuelinks.\*.id | string |  |   10727 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.avatarId | numeric |  |   10318 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.description | string |  |   A task that needs to be done. 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.iconUrl | string |  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.id | string |  |   3 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.name | string |  |   Task 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.self | string |  |   http://jira.instance.ip/rest/api/2/issuetype/3 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.issuetype.subtask | boolean |  |   False 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.iconUrl | string |  |   http://jira.instance.ip/images/border/spacer.gif 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.id | string |  |   10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.name | string |  |   High 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.priority.self | string |  |   http://jira.instance.ip/rest/api/2/priority/10002 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.description | string |  |   The issue is open and ready for the assignee to start work on it. 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.iconUrl | string |  |   http://jira.instance.ip/images/icons/statuses/open.png 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.id | string |  |   1 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.name | string |  |   Open 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.self | string |  |   http://jira.instance.ip/rest/api/2/status/1 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.colorName | string |  |   blue-gray 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.id | numeric |  |   2 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.key | string |  |   new 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.name | string |  |   To Do 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.status.statusCategory.self | string |  |   http://jira.instance.ip/rest/api/2/statuscategory/2 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.fields.summary | string |  |   CLONE - 7607 - test123 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.id | string |  |   21576 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.key | string |  |   MAN-278 
action_result.data.\*.fields.issuelinks.\*.inwardIssue.self | string |  |   http://jira.instance.ip/rest/api/2/issue/21576 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.avatarId | numeric |  |   10300 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.description | string |  |   test 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.iconUrl | string |  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10300&avatarType=issuetype 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.id | string |  |   10500 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.name | string |  |   Task 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.self | string |  |   http://jira.instance.ip/rest/api/2/issuetype/10500 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.issuetype.subtask | boolean |  |   False 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.iconUrl | string |  |   http://jira.instance.ip/images/border/spacer.gif 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.id | string |  |   10002 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.name | string |  |   High 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.priority.self | string |  |   http://jira.instance.ip/rest/api/2/priority/10002 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.description | string |  |   The issue is open and ready for the assignee to start work on it. 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.iconUrl | string |  |   http://jira.instance.ip/images/icons/statuses/generic.png 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.id | string |  |   10500 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.name | string |  |   Done 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.self | string |  |   http://jira.instance.ip/rest/api/2/status/10500 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.colorName | string |  |   yellow 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.id | numeric |  |   4 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.key | string |  |   indeterminate 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.name | string |  |   In Progress 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.status.statusCategory.self | string |  |   http://jira.instance.ip/rest/api/2/statuscategory/4 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.fields.summary | string |  |   Test 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.id | string |  |   21133 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.key | string |  |   SPOL-44 
action_result.data.\*.fields.issuelinks.\*.outwardIssue.self | string |  |   http://jira.instance.ip/rest/api/2/issue/21133 
action_result.data.\*.fields.issuelinks.\*.self | string |  |   http://jira.instance.ip/rest/api/2/issueLink/10727 
action_result.data.\*.fields.issuelinks.\*.type.id | string |  |   10000 
action_result.data.\*.fields.issuelinks.\*.type.inward | string |  |   is blocked by 
action_result.data.\*.fields.issuelinks.\*.type.name | string |  |   Blocks 
action_result.data.\*.fields.issuelinks.\*.type.outward | string |  |   blocks 
action_result.data.\*.fields.issuelinks.\*.type.self | string |  |   http://jira.instance.ip/rest/api/2/issueLinkType/10000 
action_result.data.\*.fields.issuetype.avatarId | numeric |  |   10303 
action_result.data.\*.fields.issuetype.description | string |  |   A problem which impairs or prevents the functions of the product 
action_result.data.\*.fields.issuetype.iconUrl | string |  `url`  |   http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype 
action_result.data.\*.fields.issuetype.id | string |  |   1 
action_result.data.\*.fields.issuetype.name | string |  `jira issue type`  |   Defect 
action_result.data.\*.fields.issuetype.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issuetype/1 
action_result.data.\*.fields.issuetype.subtask | boolean |  |   False  True 
action_result.data.\*.fields.labels | string |  |   test51 
action_result.data.\*.fields.lastViewed | string |  |   2018-09-20T23:54:50.643-0700 
action_result.data.\*.fields.priority.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/priorities/medium.svg 
action_result.data.\*.fields.priority.id | string |  |   3 
action_result.data.\*.fields.priority.name | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.fields.priority.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/priority/3 
action_result.data.\*.fields.progress.percent | numeric |  |   100 
action_result.data.\*.fields.progress.progress | numeric |  |   0 
action_result.data.\*.fields.progress.total | numeric |  |   0 
action_result.data.\*.fields.project.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=xsmall&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=small&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?size=medium&avatarId=10403 
action_result.data.\*.fields.project.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/projectavatar?avatarId=10403 
action_result.data.\*.fields.project.id | string |  |   10100 
action_result.data.\*.fields.project.key | string |  `jira project key`  |   MAN 
action_result.data.\*.fields.project.name | string |  |   TestProject 
action_result.data.\*.fields.project.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/project/10100 
action_result.data.\*.fields.reporter.active | boolean |  |   False  True 
action_result.data.\*.fields.reporter.avatarUrls.16x16 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.24x24 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.32x32 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.avatarUrls.48x48 | string |  `url`  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.reporter.displayName | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.fields.reporter.emailAddress | string |  `email`  |   notifications@domain.us 
action_result.data.\*.fields.reporter.key | string |  |   admin 
action_result.data.\*.fields.reporter.name | string |  `user name`  |   admin 
action_result.data.\*.fields.reporter.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.reporter.timeZone | string |  |   UTC 
action_result.data.\*.fields.resolution | string |  |  
action_result.data.\*.fields.resolution.description | string |  |   Work has been completed on this issue 
action_result.data.\*.fields.resolution.id | string |  |   10000 
action_result.data.\*.fields.resolution.name | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.fields.resolution.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/resolution/10000 
action_result.data.\*.fields.resolutiondate | string |  |   2018-09-20T19:02:38.646-0700 
action_result.data.\*.fields.status.description | string |  |   This is a sample testing description 
action_result.data.\*.fields.status.iconUrl | string |  `url`  |   http://jira.instance.ip/images/icons/statuses/closed.png 
action_result.data.\*.fields.status.id | string |  |   10001 
action_result.data.\*.fields.status.name | string |  |   Done 
action_result.data.\*.fields.status.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/status/10001 
action_result.data.\*.fields.status.statusCategory.colorName | string |  |   green 
action_result.data.\*.fields.status.statusCategory.id | numeric |  |   3 
action_result.data.\*.fields.status.statusCategory.key | string |  |   done 
action_result.data.\*.fields.status.statusCategory.name | string |  |   Done 
action_result.data.\*.fields.status.statusCategory.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/statuscategory/3 
action_result.data.\*.fields.summary | string |  |   Sample summary 
action_result.data.\*.fields.timeestimate | numeric |  |  
action_result.data.\*.fields.timeoriginalestimate | string |  |  
action_result.data.\*.fields.timespent | numeric |  |  
action_result.data.\*.fields.timetracking.remainingEstimate | string |  |   0m 
action_result.data.\*.fields.timetracking.remainingEstimateSeconds | numeric |  |   0 
action_result.data.\*.fields.timetracking.timeSpent | string |  |   2d 4h 
action_result.data.\*.fields.timetracking.timeSpentSeconds | numeric |  |   72000 
action_result.data.\*.fields.updated | string |  |   2018-09-25T06:21:27.802-0700 
action_result.data.\*.fields.versions.\*.archived | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.id | string |  |   10000 
action_result.data.\*.fields.versions.\*.name | string |  |   1.0 
action_result.data.\*.fields.versions.\*.released | boolean |  |   True  False 
action_result.data.\*.fields.versions.\*.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/version/10000 
action_result.data.\*.fields.votes.hasVoted | boolean |  |   False  True 
action_result.data.\*.fields.votes.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/votes 
action_result.data.\*.fields.votes.votes | numeric |  |   0 
action_result.data.\*.fields.watches.isWatching | boolean |  |   False  True 
action_result.data.\*.fields.watches.self | string |  `url`  |   http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers 
action_result.data.\*.fields.watches.watchCount | numeric |  |   1 
action_result.data.\*.fields.worklog.maxResults | numeric |  |   20 
action_result.data.\*.fields.worklog.startAt | numeric |  |   0 
action_result.data.\*.fields.worklog.total | numeric |  |   0 
action_result.data.\*.fields.worklog.worklogs.\*.author.active | boolean |  |   True 
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.16x16 | string |  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.24x24 | string |  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.32x32 | string |  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.author.avatarUrls.48x48 | string |  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.author.displayName | string |  |   Admin 
action_result.data.\*.fields.worklog.worklogs.\*.author.emailAddress | string |  |   notifications@test.us 
action_result.data.\*.fields.worklog.worklogs.\*.author.key | string |  |   admin 
action_result.data.\*.fields.worklog.worklogs.\*.author.name | string |  |   admin 
action_result.data.\*.fields.worklog.worklogs.\*.author.self | string |  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.worklog.worklogs.\*.author.timeZone | string |  |   Etc/GMT 
action_result.data.\*.fields.worklog.worklogs.\*.comment | string |  |  
action_result.data.\*.fields.worklog.worklogs.\*.created | string |  |   2021-12-06T06:35:45.703+0000 
action_result.data.\*.fields.worklog.worklogs.\*.id | string |  |   10200 
action_result.data.\*.fields.worklog.worklogs.\*.issueId | string |  |   27216 
action_result.data.\*.fields.worklog.worklogs.\*.self | string |  |   http://jira.instance.ip/rest/api/2/issue/27216/worklog/10200 
action_result.data.\*.fields.worklog.worklogs.\*.started | string |  |   2021-12-06T06:35:00.000+0000 
action_result.data.\*.fields.worklog.worklogs.\*.timeSpent | string |  |   4h 
action_result.data.\*.fields.worklog.worklogs.\*.timeSpentSeconds | numeric |  |   14400 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.active | boolean |  |   True 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.16x16 | string |  |   http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.24x24 | string |  |   http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.32x32 | string |  |   http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.avatarUrls.48x48 | string |  |   http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.displayName | string |  |   Admin 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.emailAddress | string |  |   notifications@test.us 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.key | string |  |   admin 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.name | string |  |   admin 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.self | string |  |   http://jira.instance.ip/rest/api/2/user?username=admin 
action_result.data.\*.fields.worklog.worklogs.\*.updateAuthor.timeZone | string |  |   Etc/GMT 
action_result.data.\*.fields.worklog.worklogs.\*.updated | string |  |   2021-12-06T06:35:45.703+0000 
action_result.data.\*.fields.workratio | numeric |  |   -1 
action_result.data.\*.id | string |  |   10246 
action_result.data.\*.issue_type | string |  `jira issue type`  |   Defect 
action_result.data.\*.name | string |  `jira ticket key`  |   MAN-1 
action_result.data.\*.priority | string |  `jira ticket priority`  |   Medium 
action_result.data.\*.project_key | string |  `jira project key`  |   MAN 
action_result.data.\*.reporter | string |  `jira user display name`  |   Test Admin 
action_result.data.\*.resolution | string |  `jira ticket resolution`  |   Done 
action_result.data.\*.status | string |  |   Done 
action_result.data.\*.summary | string |  |   Sample summary 
action_result.summary | string |  |  
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'link tickets'
Create a link between two separate tickets

Type: **generic**  
Read only: **False**

If the comment is not added, comment_visibility and comment_visibility_type values will not affect the action result.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**from_id** |  required  | First ticket (issue) key | string |  `jira ticket key` 
**to_id** |  required  | Second ticket (issue) key | string |  `jira ticket key` 
**link_type** |  required  | Type of link to create | string | 
**comment** |  optional  | Comment to add | string | 
**comment_visibility_type** |  optional  | How to limit the comment visibility | string | 
**comment_visibility_name** |  optional  | Name of group/role able to see the comment | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.comment | string |  |   This is a sample comment for the link tickets 
action_result.parameter.comment_visibility_name | string |  |   jira-users 
action_result.parameter.comment_visibility_type | string |  |   group  role 
action_result.parameter.from_id | string |  `jira ticket key`  |   MAN-1 
action_result.parameter.link_type | string |  |   Duplicate 
action_result.parameter.to_id | string |  `jira ticket key`  |   MAN-1 
action_result.data.\*.result | string |  |   success  failed 
action_result.summary | string |  |  
action_result.message | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add watcher'
Add a user to an issue's watchers list

Type: **generic**  
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to add a watcher using username for Jira cloud, we will use a user's account_id to add a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to add a watcher to the Jira ticket for Jira cloud, and, [username] action parameter will be used to add a watcher to the Jira ticket for Jira on-prem.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**username** |  optional  | Username of the user to add to the watchers list (required for Jira on-prem) | string |  `user name` 
**user_account_id** |  optional  | Account ID of the user to add to the watchers list (required for Jira cloud) | string |  `jira user account id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.id | string |  `jira ticket key`  |   PHANINCIDE-15 
action_result.parameter.user_account_id | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.parameter.username | string |  `user name`  |   admin-2 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully added the user to the watchers list of the issue ID: CJ-3 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'remove watcher'
Remove a user from an issue's watchers list

Type: **generic**  
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites. They are also removing username support from their product APIs for Jira Cloud. Since it is not possible to remove a watcher using username for Jira cloud, we will use a user's account_id to remove a watcher for Jira cloud. Use 'lookup users' action to find out a user's account_id. You can use the [user_account_id] action parameter to remove a watcher from the Jira ticket for Jira cloud, and, [username] action parameter will be used to remove a watcher from the Jira ticket for Jira on-prem.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**username** |  optional  | Username of the user to remove from watchers list (required for Jira on-prem) | string |  `user name` 
**user_account_id** |  optional  | Account ID of the user to remove from the watchers list (required for Jira cloud) | string |  `jira user account id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.id | string |  `jira ticket key`  |   PHANINCIDE-15 
action_result.parameter.user_account_id | string |  `jira user account id`  |   557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce 
action_result.parameter.username | string |  `user name`  |   admin-2 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully removed the user from the watchers list of the issue ID: CJ-3 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'on poll'
Ingest tickets from JIRA

Type: **ingest**  
Read only: **True**

Basic configuration parameters for this action are available in the asset configuration.<br><br>If the <b>project_key</b> parameter is set, polling will only ingest tickets (issues) from the specified project.<br><br>If the <b>query</b> parameter is set, polling will filter tickets based on the JQL query specified in the parameter.<br><br>If the <b>first_run_max_tickets</b> parameter is set, the first poll will only ingest up to the specified amount of tickets. If the field is left empty, the first poll will ingest all the available tickets.<br><br>If the <b>max_tickets</b> parameter is set, each poll will ingest only up to the specified amount of newly updated tickets. If the field is left empty, all tickets available at the time of the poll will be ingested.<br><br>During each polling interval, the app will query the JIRA server for tickets that have been updated since the previous poll. The app will check if each ticket has already been ingested, if it has not, it will create a new container for the ticket. An artifact will be created in the container that will have a selection of the ticket's fields listed as CEF fields. All the data of tickets will be added to the container's data field. Each attachment and comment on the ticket will be ingested as artifacts. All attachments will also be added to the vault. If a ticket has been previously ingested, the app will update the ticket container's data field. The app will also add a new artifact with updated fields and it will add new artifacts for new comments and attachments. If a comment on a ticket is edited, a new artifact will be added to the container.<br><br>For a poll now, the app will ingest as many tickets as specified by the <b>container_count</b>.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_time** |  optional  | Parameter ignored in this app | numeric | 
**end_time** |  optional  | Parameter ignored in this app | numeric | 
**container_id** |  optional  | Parameter ignored in this app | string | 
**container_count** |  optional  | Maximum number of tickets to be ingested during poll now | numeric | 
**artifact_count** |  optional  | Parameter ignored in this app | numeric | 

#### Action Output
No Output