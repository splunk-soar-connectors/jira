[comment]: # "Auto-generated SOAR connector documentation"
# Jira

Publisher: Splunk  
Connector Version: 3\.2\.4  
Product Vendor: Atlassian  
Product Name: Jira  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.0\.0  

This app integrates with JIRA to perform several ticket management actions

[comment]: # " File: readme.md"
[comment]: # "  Copyright (c) 2016-2021 Splunk Inc."
[comment]: # ""
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
## JIRA

This app uses the python JIRA module, which is licensed under the BSD License (BSD), Copyright (c)
2001-2021. Python Software Foundation

## oauthlib

This app uses the python oauthlib module, which is licensed under the OSI Approved, BSD License
(BSD), Copyright (c) 2001-2021. Python Software Foundation

## pbr

This app uses the python pbr module, which is licensed under the Apache Software License, Copyright
(c) 2001-2021. Python Software Foundation

## PyJWT

This app uses the python PyJWT module, which is licensed under the MIT License (MIT), Copyright (c)
2001-2021. Python Software Foundation

## requests-oauthlib

This app uses the python requests-oauthlib module, which is licensed under the BSD License (ISC),
Copyright (c) 2001-2021. Python Software Foundation

## requests-toolbelt

This app uses the python requests-toolbelt module, which is licensed under the Apache Software
License (Apache 2.0), Copyright (c) 2001-2021. Python Software Foundation

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

      

**The functioning of On Poll**

-   **NOTE (Consider below points due to a minute's granularity (instead of a second or lesser) for
    querying tickets in the JIRA)**

      

    -   It is highly recommended for configuring a significantly large value (larger than the number
        of existing tickets on the user's instance) in the asset configuration parameter to bring
        the ingested tickets in the Phantom in sync entirely with the JIRA instance in the first run
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
            be provided in the Phantom asset configuration
    2.  Cloud JIRA
        -   The timezone parameter here is the system settings timezone of the JIRA instance
        -   For checking the system settings timezone, navigate to the JIRA instance; navigate to
            the option **Jira Settings --> System** in the settings page; the value of the **Default
            user time zone** parameter is the timezone that has to be provided in the Phantom asset
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
            user time zone** parameter is the timezone that has to be provided in the Phantom asset
            configuration

-   If there is any error while fetching the custom fields metadata due to project configuration or
    lack of permissions, then, the custom fields will be ignored and the ingestion based on the
    system fields of the tickets (issues) will be executed successfully

      
      

-   Two approaches for fetching offenses

      
      

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
            parameter (default: 100)) and then, from the next consecutive runs, it will fetch **N**
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
    because of the Jira SDK issue. Due to this, action behaves differently with the various Phantom
    platforms. As a result, we have deployed the below-mentioned workflow which will ensure a
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

The app uses HTTP/ HTTPS protocol for communicating with the Mattermost server. Below are the
default ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http         | tcp                | 80   |
|         https        | tcp                | 443  |


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Jira asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device\_url** |  required  | string | Device URL including the port, e\.g\. https\://myjira\.enterprise\.com\:8080
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**password** |  required  | password | Password \(or API token if using Jira Cloud\)
**project\_key** |  optional  | string | Project key to ingest tickets \(issues\) from
**query** |  optional  | string | Additional parameters to query for during ingestion in JQL
**first\_run\_max\_tickets** |  optional  | numeric | Maximum tickets \(issues\) to poll first time
**max\_tickets** |  optional  | numeric | Maximum tickets \(issues\) for scheduled polling
**custom\_fields** |  optional  | string | JSON formatted list of names of custom fields \(case\-sensitive\) to be ingested
**timezone** |  required  | timezone | Jira instance timezone \(used for timezone conversions for querying in ingestion\)\. Refer to README

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using the supplied credentials  
[create ticket](#action-create-ticket) - Create a ticket \(issue\)  
[get attachments](#action-get-attachments) - Gets specific attachments from a Jira Ticket \(issue\)  
[update ticket](#action-update-ticket) - Update ticket \(issue\)  
[add comment](#action-add-comment) - Add a comment to the ticket \(issue\)  
[delete ticket](#action-delete-ticket) - Delete ticket \(issue\)  
[list projects](#action-list-projects) - List all projects  
[list tickets](#action-list-tickets) - Get a list of tickets \(issues\) in a specified project  
[lookup users](#action-lookup-users) - Get a list of user resources that match the specified search string  
[get ticket](#action-get-ticket) - Get ticket \(issue\) information  
[set status](#action-set-status) - Set ticket \(issue\) status  
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
Create a ticket \(issue\)

Type: **generic**  
Read only: **False**

The <b>fields</b> parameter is provided for advanced use of the JIRA API\. It is passed directly to the &quot;fields&quot; attribute in the JIRA API call\. Values in the <b>fields</b> parameter will take precedence over the individual parameters such as <b>summary</b>, <b>description</b>, <b>project\_key</b>, <b>issue\_type</b>, etc\.<br><br>When using the <b>fields</b> parameter, you are required to know how a particular field is inputted\. To give a few examples \(might differ in your JIRA environment\)\:<ul><li>The <b>description</b> of a ticket can be added as the first level key with a value like \{ "description"\: "ticket description" \}</li><li><b>issuetype</b> needs to be set as a dictionary like \{ "issuetype"\: \{ "name"\: "Task" \} \}</li><li><b>priority</b> is set as \{ "priority"\: \{ "name"\: "Medium" \} \}</li><li>The <b>project</b> key is set like \{ "project"\: \{ "key"\: "SPLUNK\_APP" \} \}</li></ul><br>The <b>vault\_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket\.<br><b>Assignee</b> and attachments by <b>vault\_id</b> are addressed in a separate call to JIRA made after ticket creation\.<br><br>The <b>project\_key</b> parameter is case sensitive\.<h3>Default Values</h3>Previous versions of the app set default values for <b>priority</b> and <b>issue\_type</b>\. This caused issues in situations where the default values used by the app were incompatible with the configured values\. The app does not set default values anymore\. If an optional field below is required by the JIRA environment and it is not provided, JIRA will give an error causing the action to fail\.<br><br>This action will pass if a ticket is successfully created, even if it fails to assign the ticket, add an attachment to the ticket, or fill out the custom fields\. These failures will be indicated in the result message\.<h3>Creating a subtask</h3>The following <b>fields</b> parameter value can be used to create a sub\-task, the key is to use the correct <b>issuetype</b>\.<pre>\{"fields"\:\{"project"\:\{"key"\:"AP"\},"parent"\:\{"key"\:"AP\-231"\},"summary"\:"Sub\-taskofAP\-231","description"\:"Don'tforgettodothistoo\.","issuetype"\:\{"name"\:"Sub\-Task"\}\}\}</pre><h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites\. They are also removing username support from their product APIs for Jira Cloud\. Since it is not possible to add an assignee to the Jira ticket using a username for the Jira cloud, we will use the user's account\_id to add the assignee\. Use 'lookup users' action to find out a user's account\_id\. You can use the \[assignee\_account\_id\] action parameter to add an assignee to the Jira ticket for the Jira cloud, and, \[assignee\] action parameter will be used to add an assignee to the Jira ticket for Jira on\-prem\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project\_key** |  required  | Project key to add the issue to \(case\-sensitive\) | string |  `jira project key` 
**summary** |  required  | Summary of the issue | string | 
**description** |  optional  | Description of the issue | string | 
**issue\_type** |  required  | Type of the issue \(case\-sensitive\) | string |  `jira issue type` 
**priority** |  optional  | Priority of the issue | string |  `jira ticket priority` 
**assignee** |  optional  | Assignee username \(required for Jira on\-prem, assign required permissions\) | string |  `user name` 
**assignee\_account\_id** |  optional  | Assignee user account ID \(required for Jira cloud, assign required permissions\) | string |  `jira user account id` 
**fields** |  optional  | JSON containing field values | string | 
**vault\_id** |  optional  | Vault ID of attachment | string |  `vault id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.assignee | string |  `user name` 
action\_result\.parameter\.assignee\_account\_id | string |  `jira user account id` 
action\_result\.parameter\.description | string | 
action\_result\.parameter\.fields | string | 
action\_result\.parameter\.issue\_type | string |  `jira issue type` 
action\_result\.parameter\.priority | string |  `jira ticket priority` 
action\_result\.parameter\.project\_key | string |  `jira project key` 
action\_result\.parameter\.summary | string | 
action\_result\.parameter\.vault\_id | string |  `vault id` 
action\_result\.data\.\*\.assign\_error | string | 
action\_result\.data\.\*\.attach\_error | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.fields\.Custom Checkbox Field Three | string | 
action\_result\.data\.\*\.fields\.Custom Label Field Two | string | 
action\_result\.data\.\*\.fields\.Custom Text Field One | string | 
action\_result\.data\.\*\.fields\.CustomerSanText | string | 
action\_result\.data\.\*\.fields\.Domain Test | string | 
action\_result\.data\.\*\.fields\.Epic Link | string | 
action\_result\.data\.\*\.fields\.Epic Name | string | 
action\_result\.data\.\*\.fields\.Phantom Test | string | 
action\_result\.data\.\*\.fields\.Severity | string | 
action\_result\.data\.\*\.fields\.Sprint | string | 
action\_result\.data\.\*\.fields\.\["á é í ó ú à è ë ï ö ü ĳ ë, ï, ü"\] | string | 
action\_result\.data\.\*\.fields\.\["こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，"\] | string | 
action\_result\.data\.\*\.fields\.aggregateprogress\.progress | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.total | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimespent | string | 
action\_result\.data\.\*\.fields\.assignee | string | 
action\_result\.data\.\*\.fields\.assignee\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.assignee\.accountType | string | 
action\_result\.data\.\*\.fields\.assignee\.active | boolean | 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.assignee\.emailAddress | string | 
action\_result\.data\.\*\.fields\.assignee\.key | string | 
action\_result\.data\.\*\.fields\.assignee\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.assignee\.self | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.16x16 | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.24x24 | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.32x32 | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.48x48 | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.displayName | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.emailAddress | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.name | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.self | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.content | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.created | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.filename | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.id | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.mimeType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.self | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.size | numeric | 
action\_result\.data\.\*\.fields\.attachment\.\*\.thumbnail | string | 
action\_result\.data\.\*\.fields\.comment\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.comment\.startAt | numeric | 
action\_result\.data\.\*\.fields\.comment\.total | numeric | 
action\_result\.data\.\*\.fields\.created | string | 
action\_result\.data\.\*\.fields\.creator\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.creator\.accountType | string | 
action\_result\.data\.\*\.fields\.creator\.active | boolean | 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.creator\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.creator\.key | string | 
action\_result\.data\.\*\.fields\.creator\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.creator\.self | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.timeZone | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10100 | string | 
action\_result\.data\.\*\.fields\.customfield\_10101 | string | 
action\_result\.data\.\*\.fields\.customfield\_10102 | string | 
action\_result\.data\.\*\.fields\.customfield\_10103 | string | 
action\_result\.data\.\*\.fields\.customfield\_10104 | string | 
action\_result\.data\.\*\.fields\.customfield\_10106 | string | 
action\_result\.data\.\*\.fields\.customfield\_10107\.id | string | 
action\_result\.data\.\*\.fields\.customfield\_10107\.self | string | 
action\_result\.data\.\*\.fields\.customfield\_10107\.value | string | 
action\_result\.data\.\*\.fields\.customfield\_10108 | string | 
action\_result\.data\.\*\.fields\.customfield\_10109 | string | 
action\_result\.data\.\*\.fields\.customfield\_10200 | string | 
action\_result\.data\.\*\.fields\.customfield\_10201 | string | 
action\_result\.data\.\*\.fields\.customfield\_10202 | string | 
action\_result\.data\.\*\.fields\.customfield\_10300 | string | 
action\_result\.data\.\*\.fields\.customfield\_10301 | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10401 | string | 
action\_result\.data\.\*\.fields\.customfield\_10402 | string | 
action\_result\.data\.\*\.fields\.customfield\_10500 | string | 
action\_result\.data\.\*\.fields\.customfield\_10501 | string | 
action\_result\.data\.\*\.fields\.customfield\_10600 | string | 
action\_result\.data\.\*\.fields\.customfield\_10601 | string | 
action\_result\.data\.\*\.fields\.customfield\_10602 | string | 
action\_result\.data\.\*\.fields\.customfield\_10603 | string | 
action\_result\.data\.\*\.fields\.customfield\_10605 | string | 
action\_result\.data\.\*\.fields\.customfield\_10606 | string | 
action\_result\.data\.\*\.fields\.customfield\_10701 | string | 
action\_result\.data\.\*\.fields\.customfield\_10702 | string | 
action\_result\.data\.\*\.fields\.customfield\_10703 | string | 
action\_result\.data\.\*\.fields\.customfield\_10704 | string | 
action\_result\.data\.\*\.fields\.customfield\_10801 | string | 
action\_result\.data\.\*\.fields\.customfield\_10802 | string | 
action\_result\.data\.\*\.fields\.customfield\_10900 | string | 
action\_result\.data\.\*\.fields\.customfield\_10901 | string | 
action\_result\.data\.\*\.fields\.customfield\_10902 | string | 
action\_result\.data\.\*\.fields\.customfield\_10903 | string | 
action\_result\.data\.\*\.fields\.customfield\_10904 | string | 
action\_result\.data\.\*\.fields\.customfield\_10905 | string | 
action\_result\.data\.\*\.fields\.customfield\_10906 | string | 
action\_result\.data\.\*\.fields\.customfield\_10907 | string | 
action\_result\.data\.\*\.fields\.customfield\_10908 | string | 
action\_result\.data\.\*\.fields\.customfield\_10909 | string | 
action\_result\.data\.\*\.fields\.customfield\_10910 | string | 
action\_result\.data\.\*\.fields\.customfield\_10911 | string | 
action\_result\.data\.\*\.fields\.customfield\_10912 | string | 
action\_result\.data\.\*\.fields\.customfield\_10915 | string | 
action\_result\.data\.\*\.fields\.customfield\_10916 | string | 
action\_result\.data\.\*\.fields\.customfield\_10917 | string | 
action\_result\.data\.\*\.fields\.customfield\_10918 | string | 
action\_result\.data\.\*\.fields\.customfield\_10919 | string | 
action\_result\.data\.\*\.fields\.customfield\_10920 | string | 
action\_result\.data\.\*\.fields\.customfield\_10921 | string | 
action\_result\.data\.\*\.fields\.customfield\_10922 | string | 
action\_result\.data\.\*\.fields\.customfield\_10923 | string | 
action\_result\.data\.\*\.fields\.customfield\_10924 | string | 
action\_result\.data\.\*\.fields\.customfield\_10925 | string | 
action\_result\.data\.\*\.fields\.customfield\_10926 | string | 
action\_result\.data\.\*\.fields\.customfield\_10927 | string | 
action\_result\.data\.\*\.fields\.customfield\_11002 | string | 
action\_result\.data\.\*\.fields\.customfield\_11003 | string | 
action\_result\.data\.\*\.fields\.customfield\_11100 | string | 
action\_result\.data\.\*\.fields\.customfield\_11101 | string | 
action\_result\.data\.\*\.fields\.customfield\_11102 | string | 
action\_result\.data\.\*\.fields\.customfield\_11103 | string | 
action\_result\.data\.\*\.fields\.customtextfield1 | string | 
action\_result\.data\.\*\.fields\.description | string | 
action\_result\.data\.\*\.fields\.duedate | string | 
action\_result\.data\.\*\.fields\.environment | string | 
action\_result\.data\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.lastViewed | string | 
action\_result\.data\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.progress\.progress | numeric | 
action\_result\.data\.\*\.fields\.progress\.total | numeric | 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.id | string | 
action\_result\.data\.\*\.fields\.project\.key | string |  `jira project key` 
action\_result\.data\.\*\.fields\.project\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.description | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.id | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.self | string | 
action\_result\.data\.\*\.fields\.project\.projectTypeKey | string | 
action\_result\.data\.\*\.fields\.project\.self | string |  `url` 
action\_result\.data\.\*\.fields\.project\.simplified | boolean | 
action\_result\.data\.\*\.fields\.reporter\.accountType | string | 
action\_result\.data\.\*\.fields\.reporter\.active | boolean | 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.reporter\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.reporter\.key | string | 
action\_result\.data\.\*\.fields\.reporter\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.reporter\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.timeZone | string | 
action\_result\.data\.\*\.fields\.resolution | string | 
action\_result\.data\.\*\.fields\.resolutiondate | string | 
action\_result\.data\.\*\.fields\.security | string | 
action\_result\.data\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.statuscategorychangedate | string | 
action\_result\.data\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.timeestimate | string | 
action\_result\.data\.\*\.fields\.timeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.timespent | string | 
action\_result\.data\.\*\.fields\.updated | string | 
action\_result\.data\.\*\.fields\.votes\.hasVoted | boolean | 
action\_result\.data\.\*\.fields\.votes\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.votes | numeric | 
action\_result\.data\.\*\.fields\.watches\.isWatching | boolean | 
action\_result\.data\.\*\.fields\.watches\.self | string |  `url` 
action\_result\.data\.\*\.fields\.watches\.watchCount | numeric | 
action\_result\.data\.\*\.fields\.worklog\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.worklog\.startAt | numeric | 
action\_result\.data\.\*\.fields\.worklog\.total | numeric | 
action\_result\.data\.\*\.fields\.workratio | numeric | 
action\_result\.data\.\*\.fields\.こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，日活百万\+的漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリティインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€	₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\#$%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à è ë ï ö ü ĳ ë, ï, üاردو تہجی | string | 
action\_result\.data\.\*\.fields\.漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリテ ィインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€ ₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\# $%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à ë ï ö üاردو تہجیગુજરાતીहिन्दीгуджаратиგუჯარათიগুজরাটি | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.issue\_type | string |  `jira issue type` 
action\_result\.data\.\*\.json\_fields\_error | string | 
action\_result\.data\.\*\.name | string |  `jira ticket key` 
action\_result\.data\.\*\.priority | string |  `jira ticket priority` 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.data\.\*\.reporter | string |  `jira user display name` 
action\_result\.data\.\*\.resolution | string |  `jira ticket resolution` 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.summary | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get attachments'
Gets specific attachments from a Jira Ticket \(issue\)

Type: **investigate**  
Read only: **True**

The function will store specific attachments from a given Jira ticket inside the vault\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | The key of the Jira issue | string |  `jira ticket key` 
**retrieve\_all** |  optional  | If this is set to true all attachments will be retrieved from the issue \(if the value is not provided, it will internally be treated as 'false'\) | boolean | 
**container\_id** |  required  | The Container ID to associate the file with | string | 
**extension\_filter** |  optional  | Comma\-separated list of file extensions to be returned from the issue | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.container\_id | string | 
action\_result\.parameter\.extension\_filter | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.retrieve\_all | boolean | 
action\_result\.data\.\*\.container | numeric | 
action\_result\.data\.\*\.hash | string |  `md5` 
action\_result\.data\.\*\.id | numeric | 
action\_result\.data\.\*\.message | string | 
action\_result\.data\.\*\.size | numeric | 
action\_result\.data\.\*\.succeeded | boolean | 
action\_result\.data\.\*\.vault\_id | string |  `vault id` 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'update ticket'
Update ticket \(issue\)

Type: **generic**  
Read only: **False**

Update an existing issue with the values specified in the <b>update\_fields</b> parameter\.<br>The results of the <b>get ticket</b> action may be used to obtain the <b>update\_fields</b> parameters, including any custom fields present in the JIRA\.</br>The JSON specified in the <b>update\_fields</b> parameter requires the keys and the values specified in case\-sensitive and double\-quotes string format, except in the case of boolean values, which should be either <i>true</i> or <i>false</i> for example\:</br>\{"summary"\: "Zeus, multiple action need to be taken", "description"\: "A new summary was added"\}</br></br>The App supports multiple methods for specifying the input dictionary\. Please see <a href="https\://developer\.atlassian\.com/server/jira/platform/jira\-rest\-api\-examples/\#editing\-an\-issue\-examples"><b>the Atlassian documentation for the JIRA REST <i>update issue</i> API</b></a> for more information\.<br>The following formats can be passed as input\: <ul><li>Simple format; Create a dictionary with all the fields that need to be set\:<br>\{"summary"\: "Zeus detected on endpoint", "description"\: "Investigate further"\}</li><li>Using the <i>update</i> key; Some issue fields support operations like <i>remove</i> and <i>add</i>, these operations can be combined to update a ticket\: <br>\{"<b>update</b>"\: \{"components" \: \[\{"remove" \: \{"name" \: "secondcomponent"\}\}, \{"add" \: \{"name" \: "firstcomponent"\}\}\]\}\}<br>\{"<b>update</b>"\: \{"comment"\: \[\{"add"\: \{"body"\: "test comment update"\}\}\]\}\} </li><li>Using the <i>fields</i> key;</br>\{"<b>fields</b>"\:\{"labels" \: \["FIRSTLABEL"\]\}\}</li></ul></br>The app supports updating custom fields; depending on the custom field type, some operations might not be available\. Review the <b>jira\_app</b> playbook for examples\.<br><br>The <b>vault\_id</b> parameter takes the vault ID of a file in the vault and attaches the file to the JIRA ticket\.<br><br>This action requires that either the <b>update\_fields</b> parameter or the <b>vault\_id</b> parameter is filled out\. The action will fail if it either unsuccessfully attempts to add the attachment to the ticket or update the fields on the ticket\.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites\. They are also removing username support from their product APIs for Jira Cloud\. Since it is not possible to update fields related to user resources in the Jira ticket using username for Jira cloud, we will use the user's account\_id to update fields related to user resources\. Use 'lookup users' action to find out user's account\_id\. Use 'get ticket' action results to obtain the \[update\_fields\] parameters\. Please find out below\-mentioned examples for the \[update\_fields\] parameter which is related to user resources\.<ul><li>Add assignee to the Jira ticket for Jira on\-prem\:<br>\{"fields"\:\{"assignee" \: \{"name"\: "username"\}\}\}</li><li>Add assignee to the Jira ticket for Jira cloud\:<br>\{"fields"\:\{"assignee" \: \{"accountId"\: "6d1ef6xy52z7360c267f27bb"\}\}\}</li></ul>\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**update\_fields** |  optional  | JSON containing field values | string | 
**vault\_id** |  optional  | Vault ID of attachment | string |  `vault id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.update\_fields | string | 
action\_result\.parameter\.vault\_id | string |  `vault id` 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.fields\.Custom Checkbox Field Three | string | 
action\_result\.data\.\*\.fields\.Custom Label Field Two | string | 
action\_result\.data\.\*\.fields\.Custom Text Field One | string | 
action\_result\.data\.\*\.fields\.CustomerSanText | string | 
action\_result\.data\.\*\.fields\.Domain Test | string | 
action\_result\.data\.\*\.fields\.Epic Link | string | 
action\_result\.data\.\*\.fields\.Phantom Test | string | 
action\_result\.data\.\*\.fields\.Sprint | string | 
action\_result\.data\.\*\.fields\.\["á é í ó ú à è ë ï ö ü ĳ ë, ï, ü"\] | string | 
action\_result\.data\.\*\.fields\.\["こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，"\] | string | 
action\_result\.data\.\*\.fields\.aggregateprogress\.progress | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.total | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimespent | string | 
action\_result\.data\.\*\.fields\.assignee | string | 
action\_result\.data\.\*\.fields\.assignee\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.assignee\.accountType | string | 
action\_result\.data\.\*\.fields\.assignee\.active | boolean | 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.assignee\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.assignee\.key | string | 
action\_result\.data\.\*\.fields\.assignee\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.assignee\.self | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.content | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.created | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.filename | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.id | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.mimeType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.size | numeric | 
action\_result\.data\.\*\.fields\.attachment\.\*\.thumbnail | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.body | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.created | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.id | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updated | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.type | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.value | string | 
action\_result\.data\.\*\.fields\.comment\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.comment\.startAt | numeric | 
action\_result\.data\.\*\.fields\.comment\.total | numeric | 
action\_result\.data\.\*\.fields\.components\.\*\.id | string | 
action\_result\.data\.\*\.fields\.components\.\*\.name | string | 
action\_result\.data\.\*\.fields\.components\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.created | string | 
action\_result\.data\.\*\.fields\.creator\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.creator\.accountType | string | 
action\_result\.data\.\*\.fields\.creator\.active | boolean | 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.creator\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.creator\.key | string | 
action\_result\.data\.\*\.fields\.creator\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.creator\.self | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.timeZone | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10100 | string | 
action\_result\.data\.\*\.fields\.customfield\_10101 | string | 
action\_result\.data\.\*\.fields\.customfield\_10104 | string | 
action\_result\.data\.\*\.fields\.customfield\_10106 | string | 
action\_result\.data\.\*\.fields\.customfield\_10109 | string | 
action\_result\.data\.\*\.fields\.customfield\_10200 | string | 
action\_result\.data\.\*\.fields\.customfield\_10201 | string | 
action\_result\.data\.\*\.fields\.customfield\_10202 | string | 
action\_result\.data\.\*\.fields\.customfield\_10300 | string | 
action\_result\.data\.\*\.fields\.customfield\_10301 | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10401 | string | 
action\_result\.data\.\*\.fields\.customfield\_10402 | string | 
action\_result\.data\.\*\.fields\.customfield\_10500 | string | 
action\_result\.data\.\*\.fields\.customfield\_10501 | string | 
action\_result\.data\.\*\.fields\.customfield\_10600 | string | 
action\_result\.data\.\*\.fields\.customfield\_10601 | string | 
action\_result\.data\.\*\.fields\.customfield\_10602 | string | 
action\_result\.data\.\*\.fields\.customfield\_10603 | string | 
action\_result\.data\.\*\.fields\.customfield\_10605 | string | 
action\_result\.data\.\*\.fields\.customfield\_10606 | string | 
action\_result\.data\.\*\.fields\.customfield\_10701 | string | 
action\_result\.data\.\*\.fields\.customfield\_10702 | string | 
action\_result\.data\.\*\.fields\.customfield\_10703 | string | 
action\_result\.data\.\*\.fields\.customfield\_10704 | string | 
action\_result\.data\.\*\.fields\.customfield\_10801 | string | 
action\_result\.data\.\*\.fields\.customfield\_10802 | string | 
action\_result\.data\.\*\.fields\.customfield\_10900 | string | 
action\_result\.data\.\*\.fields\.customfield\_10901 | string | 
action\_result\.data\.\*\.fields\.customfield\_10902 | string | 
action\_result\.data\.\*\.fields\.customfield\_10903 | string | 
action\_result\.data\.\*\.fields\.customfield\_10904 | string | 
action\_result\.data\.\*\.fields\.customfield\_10905 | string | 
action\_result\.data\.\*\.fields\.customfield\_10906 | string | 
action\_result\.data\.\*\.fields\.customfield\_10907 | string | 
action\_result\.data\.\*\.fields\.customfield\_10908 | string | 
action\_result\.data\.\*\.fields\.customfield\_10909 | string | 
action\_result\.data\.\*\.fields\.customfield\_10910 | string | 
action\_result\.data\.\*\.fields\.customfield\_10911 | string | 
action\_result\.data\.\*\.fields\.customfield\_10912 | string | 
action\_result\.data\.\*\.fields\.customfield\_10915 | string | 
action\_result\.data\.\*\.fields\.customfield\_10916 | string | 
action\_result\.data\.\*\.fields\.customfield\_10917 | string | 
action\_result\.data\.\*\.fields\.customfield\_10918 | string | 
action\_result\.data\.\*\.fields\.customfield\_10919 | string | 
action\_result\.data\.\*\.fields\.customfield\_10920 | string | 
action\_result\.data\.\*\.fields\.customfield\_10921 | string | 
action\_result\.data\.\*\.fields\.customfield\_10922 | string | 
action\_result\.data\.\*\.fields\.customfield\_10923 | string | 
action\_result\.data\.\*\.fields\.customfield\_10924 | string | 
action\_result\.data\.\*\.fields\.customfield\_10925 | string | 
action\_result\.data\.\*\.fields\.customfield\_10926 | string | 
action\_result\.data\.\*\.fields\.customfield\_10927 | string | 
action\_result\.data\.\*\.fields\.customfield\_11002 | string | 
action\_result\.data\.\*\.fields\.customfield\_11003 | string | 
action\_result\.data\.\*\.fields\.customfield\_11100 | string | 
action\_result\.data\.\*\.fields\.customfield\_11101 | string | 
action\_result\.data\.\*\.fields\.customfield\_11102 | string | 
action\_result\.data\.\*\.fields\.customfield\_11103 | string | 
action\_result\.data\.\*\.fields\.customtextfield1 | string | 
action\_result\.data\.\*\.fields\.description | string | 
action\_result\.data\.\*\.fields\.duedate | string | 
action\_result\.data\.\*\.fields\.environment | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.key | string |  `jira ticket key` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.inward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.outward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.labels | string | 
action\_result\.data\.\*\.fields\.lastViewed | string | 
action\_result\.data\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.progress\.progress | numeric | 
action\_result\.data\.\*\.fields\.progress\.total | numeric | 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.id | string | 
action\_result\.data\.\*\.fields\.project\.key | string |  `jira project key` 
action\_result\.data\.\*\.fields\.project\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.description | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.id | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.self | string | 
action\_result\.data\.\*\.fields\.project\.projectTypeKey | string | 
action\_result\.data\.\*\.fields\.project\.self | string |  `url` 
action\_result\.data\.\*\.fields\.project\.simplified | boolean | 
action\_result\.data\.\*\.fields\.reporter\.accountType | string | 
action\_result\.data\.\*\.fields\.reporter\.active | boolean | 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.reporter\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.reporter\.key | string | 
action\_result\.data\.\*\.fields\.reporter\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.reporter\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.timeZone | string | 
action\_result\.data\.\*\.fields\.resolution | string | 
action\_result\.data\.\*\.fields\.resolution\.description | string | 
action\_result\.data\.\*\.fields\.resolution\.id | string | 
action\_result\.data\.\*\.fields\.resolution\.name | string |  `jira ticket resolution` 
action\_result\.data\.\*\.fields\.resolution\.self | string |  `url` 
action\_result\.data\.\*\.fields\.resolutiondate | string | 
action\_result\.data\.\*\.fields\.security | string | 
action\_result\.data\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.statuscategorychangedate | string | 
action\_result\.data\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.timeestimate | string | 
action\_result\.data\.\*\.fields\.timeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.timespent | string | 
action\_result\.data\.\*\.fields\.updated | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.hasVoted | boolean | 
action\_result\.data\.\*\.fields\.votes\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.votes | numeric | 
action\_result\.data\.\*\.fields\.watches\.isWatching | boolean | 
action\_result\.data\.\*\.fields\.watches\.self | string |  `url` 
action\_result\.data\.\*\.fields\.watches\.watchCount | numeric | 
action\_result\.data\.\*\.fields\.worklog\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.worklog\.startAt | numeric | 
action\_result\.data\.\*\.fields\.worklog\.total | numeric | 
action\_result\.data\.\*\.fields\.workratio | numeric | 
action\_result\.data\.\*\.fields\.こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，日活百万\+的漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリティインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€	₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\#$%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à è ë ï ö ü ĳ ë, ï, üاردو تہجی | string | 
action\_result\.data\.\*\.fields\.漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリテ ィインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€ ₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\# $%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à ë ï ö üاردو تہجیગુજરાતીहिन्दीгуджаратиგუჯარათიগুজরাটি | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.issue\_type | string |  `jira issue type` 
action\_result\.data\.\*\.name | string |  `jira ticket key` 
action\_result\.data\.\*\.priority | string |  `jira ticket priority` 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.data\.\*\.reporter | string |  `jira user display name` 
action\_result\.data\.\*\.resolution | string |  `jira ticket resolution` 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.summary | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add comment'
Add a comment to the ticket \(issue\)

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**comment** |  required  | Comment to add | string | 
**internal** |  optional  | Whether comment should be internal only or not in Jira Service Desk \(if the value is not provided, it will internally be treated as 'false'\) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.internal | boolean | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'delete ticket'
Delete ticket \(issue\)

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list projects'
List all projects

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.summary\.total\_projects | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list tickets'
Get a list of tickets \(issues\) in a specified project

Type: **investigate**  
Read only: **True**

The default value for the parameter <b>'start\_index'</b> is <b>0</b> and for <b>'max\_results'</b> is <b>1000</b>\. The maximum number of tickets as specified by the parameter <b>'max\_results'</b> will be fetched starting from the index specified by the parameter <b>'start\_index'</b>\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**project\_key** |  required  | Project key to list the tickets \(issues\) of | string |  `jira project key` 
**query** |  optional  | Additional parameters to query for in JQL | string | 
**start\_index** |  optional  | Start index of the list | numeric | 
**max\_results** |  optional  | Maximum number of issues to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.max\_results | numeric | 
action\_result\.parameter\.project\_key | string |  `jira project key` 
action\_result\.parameter\.query | string | 
action\_result\.parameter\.start\_index | numeric | 
action\_result\.data\.\*\.description | string |  `url` 
action\_result\.data\.\*\.fields\.Custom Checkbox Field Three | string | 
action\_result\.data\.\*\.fields\.Custom Label Field Two | string | 
action\_result\.data\.\*\.fields\.Custom Text Field One | string | 
action\_result\.data\.\*\.fields\.CustomerSanText | string | 
action\_result\.data\.\*\.fields\.Domain Test | string | 
action\_result\.data\.\*\.fields\.aggregateprogress\.progress | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.total | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimespent | string | 
action\_result\.data\.\*\.fields\.assignee | string | 
action\_result\.data\.\*\.fields\.assignee\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.assignee\.accountType | string | 
action\_result\.data\.\*\.fields\.assignee\.active | boolean | 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.assignee\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.assignee\.key | string | 
action\_result\.data\.\*\.fields\.assignee\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.assignee\.self | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountType | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.type | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.value | string | 
action\_result\.data\.\*\.fields\.comment\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.comment\.startAt | numeric | 
action\_result\.data\.\*\.fields\.comment\.total | numeric | 
action\_result\.data\.\*\.fields\.created | string | 
action\_result\.data\.\*\.fields\.creator\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.creator\.accountType | string | 
action\_result\.data\.\*\.fields\.creator\.active | boolean | 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.creator\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.creator\.key | string | 
action\_result\.data\.\*\.fields\.creator\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.creator\.self | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.timeZone | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10704\.id | string | 
action\_result\.data\.\*\.fields\.customfield\_10704\.self | string |  `url` 
action\_result\.data\.\*\.fields\.customfield\_10704\.value | string | 
action\_result\.data\.\*\.fields\.description | string |  `url` 
action\_result\.data\.\*\.fields\.duedate | string | 
action\_result\.data\.\*\.fields\.environment | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.key | string |  `jira ticket key` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.inward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.outward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.lastViewed | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.parent\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.parent\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.parent\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.parent\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.parent\.id | string | 
action\_result\.data\.\*\.fields\.parent\.key | string | 
action\_result\.data\.\*\.fields\.parent\.self | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.progress\.progress | numeric | 
action\_result\.data\.\*\.fields\.progress\.total | numeric | 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.id | string | 
action\_result\.data\.\*\.fields\.project\.key | string |  `jira project key` 
action\_result\.data\.\*\.fields\.project\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.description | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.id | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.self | string | 
action\_result\.data\.\*\.fields\.project\.projectTypeKey | string | 
action\_result\.data\.\*\.fields\.project\.self | string |  `url` 
action\_result\.data\.\*\.fields\.project\.simplified | boolean | 
action\_result\.data\.\*\.fields\.reporter\.accountType | string | 
action\_result\.data\.\*\.fields\.reporter\.active | boolean | 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.reporter\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.reporter\.key | string | 
action\_result\.data\.\*\.fields\.reporter\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.reporter\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.timeZone | string | 
action\_result\.data\.\*\.fields\.resolution | string | 
action\_result\.data\.\*\.fields\.resolution\.description | string | 
action\_result\.data\.\*\.fields\.resolution\.id | string | 
action\_result\.data\.\*\.fields\.resolution\.name | string |  `jira ticket resolution` 
action\_result\.data\.\*\.fields\.resolution\.self | string |  `url` 
action\_result\.data\.\*\.fields\.resolutiondate | string | 
action\_result\.data\.\*\.fields\.security | string | 
action\_result\.data\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.statuscategorychangedate | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.subtasks\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.id | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.key | string | 
action\_result\.data\.\*\.fields\.subtasks\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.timeestimate | string | 
action\_result\.data\.\*\.fields\.timeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.timespent | string | 
action\_result\.data\.\*\.fields\.updated | string | 
action\_result\.data\.\*\.fields\.votes\.hasVoted | boolean | 
action\_result\.data\.\*\.fields\.votes\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.votes | numeric | 
action\_result\.data\.\*\.fields\.watches\.isWatching | boolean | 
action\_result\.data\.\*\.fields\.watches\.self | string |  `url` 
action\_result\.data\.\*\.fields\.watches\.watchCount | numeric | 
action\_result\.data\.\*\.fields\.worklog\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.worklog\.startAt | numeric | 
action\_result\.data\.\*\.fields\.worklog\.total | numeric | 
action\_result\.data\.\*\.fields\.workratio | numeric | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.issue\_type | string |  `jira issue type` 
action\_result\.data\.\*\.name | string |  `jira ticket key` 
action\_result\.data\.\*\.priority | string |  `jira ticket priority` 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.data\.\*\.reporter | string |  `jira user display name` 
action\_result\.data\.\*\.resolution | string |  `jira ticket resolution` 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.summary | string | 
action\_result\.summary\.total\_issues | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'lookup users'
Get a list of user resources that match the specified search string

Type: **investigate**  
Read only: **True**

This action will be used to fetch the username of user resources for Jira on\-prem and account\_id of user resources for Jira cloud\. The default value for \[max\_results\] action parameter is <b>1000</b>\. The maximum number of users as specified by the parameter \[max\_results\] will be fetched starting from the first\.<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites\. They are also removing username support from their product APIs for Jira Cloud\. Since it is not possible to search users using username for Jira cloud, we will use the user's display name to search users\. You can use the \[display\_name\] action parameter to search users for Jira cloud, and, \[username\] action parameter will be used to search users for Jira on\-prem\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**username** |  optional  | A string to match with usernames, name, or email against for JIRA on\-prem \(required for Jira on\-prem\) | string |  `user name` 
**display\_name** |  optional  | A string to match with display name for JIRA cloud \(required for Jira cloud\) | string |  `jira user display name` 
**max\_results** |  optional  | Maximum number of users to return | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.display\_name | string |  `jira user display name` 
action\_result\.parameter\.max\_results | numeric | 
action\_result\.parameter\.username | string |  `user name` 
action\_result\.data\.\*\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.accountType | string | 
action\_result\.data\.\*\.active | boolean | 
action\_result\.data\.\*\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.emailAddress | string |  `email` 
action\_result\.data\.\*\.key | string | 
action\_result\.data\.\*\.locale | string | 
action\_result\.data\.\*\.name | string |  `user name` 
action\_result\.data\.\*\.self | string |  `url` 
action\_result\.data\.\*\.timeZone | string | 
action\_result\.summary\.total\_users | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get ticket'
Get ticket \(issue\) information

Type: **investigate**  
Read only: **True**

The keys in the <b>action\_result\.data\.\*\.fields</b> output section of the results can differ based on the JIRA server configuration\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket \(issue\) key | string |  `jira ticket key` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.fields\.Custom Checkbox Field Three | string | 
action\_result\.data\.\*\.fields\.Custom Label Field Two | string | 
action\_result\.data\.\*\.fields\.Custom Text Field One | string | 
action\_result\.data\.\*\.fields\.CustomerSanText | string | 
action\_result\.data\.\*\.fields\.Domain Test | string | 
action\_result\.data\.\*\.fields\.Epic Link | string | 
action\_result\.data\.\*\.fields\.Phantom Test | string | 
action\_result\.data\.\*\.fields\.Sprint | string | 
action\_result\.data\.\*\.fields\.\["á é í ó ú à è ë ï ö ü ĳ ë, ï, ü"\] | string | 
action\_result\.data\.\*\.fields\.\["こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，"\] | string | 
action\_result\.data\.\*\.fields\.aggregateprogress\.progress | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.total | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimespent | string | 
action\_result\.data\.\*\.fields\.assignee | string | 
action\_result\.data\.\*\.fields\.assignee\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.assignee\.accountType | string | 
action\_result\.data\.\*\.fields\.assignee\.active | boolean | 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.assignee\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.assignee\.key | string | 
action\_result\.data\.\*\.fields\.assignee\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.assignee\.self | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.accountType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.content | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.created | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.filename | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.id | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.mimeType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.size | numeric | 
action\_result\.data\.\*\.fields\.attachment\.\*\.thumbnail | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.body | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.created | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.id | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updated | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.type | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.value | string | 
action\_result\.data\.\*\.fields\.comment\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.comment\.startAt | numeric | 
action\_result\.data\.\*\.fields\.comment\.total | numeric | 
action\_result\.data\.\*\.fields\.components\.\*\.id | string | 
action\_result\.data\.\*\.fields\.components\.\*\.name | string | 
action\_result\.data\.\*\.fields\.components\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.created | string | 
action\_result\.data\.\*\.fields\.creator\.accountId | string |  `jira user account id` 
action\_result\.data\.\*\.fields\.creator\.accountType | string | 
action\_result\.data\.\*\.fields\.creator\.active | boolean | 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.creator\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.creator\.key | string | 
action\_result\.data\.\*\.fields\.creator\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.creator\.self | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.timeZone | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10100 | string | 
action\_result\.data\.\*\.fields\.customfield\_10101 | string | 
action\_result\.data\.\*\.fields\.customfield\_10104 | string | 
action\_result\.data\.\*\.fields\.customfield\_10106 | string | 
action\_result\.data\.\*\.fields\.customfield\_10109 | string | 
action\_result\.data\.\*\.fields\.customfield\_10200 | string | 
action\_result\.data\.\*\.fields\.customfield\_10201 | string | 
action\_result\.data\.\*\.fields\.customfield\_10202 | string | 
action\_result\.data\.\*\.fields\.customfield\_10300 | string | 
action\_result\.data\.\*\.fields\.customfield\_10301 | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10401 | string | 
action\_result\.data\.\*\.fields\.customfield\_10402 | string | 
action\_result\.data\.\*\.fields\.customfield\_10500 | string | 
action\_result\.data\.\*\.fields\.customfield\_10501 | string | 
action\_result\.data\.\*\.fields\.customfield\_10600 | string | 
action\_result\.data\.\*\.fields\.customfield\_10601 | string | 
action\_result\.data\.\*\.fields\.customfield\_10602 | string | 
action\_result\.data\.\*\.fields\.customfield\_10603 | string | 
action\_result\.data\.\*\.fields\.customfield\_10605 | string | 
action\_result\.data\.\*\.fields\.customfield\_10606 | string | 
action\_result\.data\.\*\.fields\.customfield\_10701 | string | 
action\_result\.data\.\*\.fields\.customfield\_10702 | string | 
action\_result\.data\.\*\.fields\.customfield\_10703 | string | 
action\_result\.data\.\*\.fields\.customfield\_10704 | string | 
action\_result\.data\.\*\.fields\.customfield\_10801 | string | 
action\_result\.data\.\*\.fields\.customfield\_10802 | string | 
action\_result\.data\.\*\.fields\.customfield\_10900 | string | 
action\_result\.data\.\*\.fields\.customfield\_10901 | string | 
action\_result\.data\.\*\.fields\.customfield\_10902 | string | 
action\_result\.data\.\*\.fields\.customfield\_10903 | string | 
action\_result\.data\.\*\.fields\.customfield\_10904 | string | 
action\_result\.data\.\*\.fields\.customfield\_10905 | string | 
action\_result\.data\.\*\.fields\.customfield\_10906 | string | 
action\_result\.data\.\*\.fields\.customfield\_10907 | string | 
action\_result\.data\.\*\.fields\.customfield\_10908 | string | 
action\_result\.data\.\*\.fields\.customfield\_10909 | string | 
action\_result\.data\.\*\.fields\.customfield\_10910 | string | 
action\_result\.data\.\*\.fields\.customfield\_10911 | string | 
action\_result\.data\.\*\.fields\.customfield\_10912 | string | 
action\_result\.data\.\*\.fields\.customfield\_10915 | string | 
action\_result\.data\.\*\.fields\.customfield\_10916 | string | 
action\_result\.data\.\*\.fields\.customfield\_10917 | string | 
action\_result\.data\.\*\.fields\.customfield\_10918 | string | 
action\_result\.data\.\*\.fields\.customfield\_10919 | string | 
action\_result\.data\.\*\.fields\.customfield\_10920 | string | 
action\_result\.data\.\*\.fields\.customfield\_10921 | string | 
action\_result\.data\.\*\.fields\.customfield\_10922 | string | 
action\_result\.data\.\*\.fields\.customfield\_10923 | string | 
action\_result\.data\.\*\.fields\.customfield\_10924 | string | 
action\_result\.data\.\*\.fields\.customfield\_10925 | string | 
action\_result\.data\.\*\.fields\.customfield\_10926 | string | 
action\_result\.data\.\*\.fields\.customfield\_10927 | string | 
action\_result\.data\.\*\.fields\.customfield\_11002 | string | 
action\_result\.data\.\*\.fields\.customfield\_11003 | string | 
action\_result\.data\.\*\.fields\.customfield\_11100 | string | 
action\_result\.data\.\*\.fields\.customfield\_11101 | string | 
action\_result\.data\.\*\.fields\.customfield\_11102 | string | 
action\_result\.data\.\*\.fields\.customfield\_11103 | string | 
action\_result\.data\.\*\.fields\.customtextfield1 | string | 
action\_result\.data\.\*\.fields\.description | string | 
action\_result\.data\.\*\.fields\.duedate | string | 
action\_result\.data\.\*\.fields\.environment | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.key | string |  `jira ticket key` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.inward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.outward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.labels | string | 
action\_result\.data\.\*\.fields\.lastViewed | string | 
action\_result\.data\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.progress\.progress | numeric | 
action\_result\.data\.\*\.fields\.progress\.total | numeric | 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.id | string | 
action\_result\.data\.\*\.fields\.project\.key | string |  `jira project key` 
action\_result\.data\.\*\.fields\.project\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.description | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.id | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.name | string | 
action\_result\.data\.\*\.fields\.project\.projectCategory\.self | string | 
action\_result\.data\.\*\.fields\.project\.projectTypeKey | string | 
action\_result\.data\.\*\.fields\.project\.self | string |  `url` 
action\_result\.data\.\*\.fields\.project\.simplified | boolean | 
action\_result\.data\.\*\.fields\.reporter\.accountType | string | 
action\_result\.data\.\*\.fields\.reporter\.active | boolean | 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.reporter\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.reporter\.key | string | 
action\_result\.data\.\*\.fields\.reporter\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.reporter\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.timeZone | string | 
action\_result\.data\.\*\.fields\.resolution | string | 
action\_result\.data\.\*\.fields\.resolution\.description | string | 
action\_result\.data\.\*\.fields\.resolution\.id | string | 
action\_result\.data\.\*\.fields\.resolution\.name | string |  `jira ticket resolution` 
action\_result\.data\.\*\.fields\.resolution\.self | string |  `url` 
action\_result\.data\.\*\.fields\.resolutiondate | string | 
action\_result\.data\.\*\.fields\.security | string | 
action\_result\.data\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.statuscategorychangedate | string | 
action\_result\.data\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.timeestimate | string | 
action\_result\.data\.\*\.fields\.timeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.timespent | string | 
action\_result\.data\.\*\.fields\.updated | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.hasVoted | boolean | 
action\_result\.data\.\*\.fields\.votes\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.votes | numeric | 
action\_result\.data\.\*\.fields\.watches\.isWatching | boolean | 
action\_result\.data\.\*\.fields\.watches\.self | string |  `url` 
action\_result\.data\.\*\.fields\.watches\.watchCount | numeric | 
action\_result\.data\.\*\.fields\.worklog\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.worklog\.startAt | numeric | 
action\_result\.data\.\*\.fields\.worklog\.total | numeric | 
action\_result\.data\.\*\.fields\.workratio | numeric | 
action\_result\.data\.\*\.fields\.こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，日活百万\+的漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリティインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€	₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\#$%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à è ë ï ö ü ĳ ë, ï, üاردو تہجی | string | 
action\_result\.data\.\*\.fields\.漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリテ ィインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€ ₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\# $%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à ë ï ö üاردو تہجیગુજરાતીहिन्दीгуджаратиგუჯარათიগুজরাটি | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.issue\_type | string |  `jira issue type` 
action\_result\.data\.\*\.name | string |  `jira ticket key` 
action\_result\.data\.\*\.priority | string |  `jira ticket priority` 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.data\.\*\.reporter | string |  `jira user display name` 
action\_result\.data\.\*\.resolution | string |  `jira ticket resolution` 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.summary | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'set status'
Set ticket \(issue\) status

Type: **generic**  
Read only: **False**

In JIRA, the status transition of an issue is determined by the workflow defined for the project\. The app will return an error if an un\-allowed status transition is attempted\. In such cases, the possible statuses are returned based on the issue's current status value\.<br>The same is the case for invalid resolutions\. Do note that some combinations of status and resolution values might be invalid, even if they are allowed individually\.<br>To get valid values to use as input for the parameters\:<ul><li>For valid <b>status</b> values\:<ul><li>Log in to the JIRA server from the UI</li><li>Go to http\://my\_jira\_ip/rest/api/2/issue/<i>\[jira\_issue\_key\]</i>/transitions</li><li>The returned JSON should contain a list of transitions</li><li>The name field denotes the status that can be set using this action</li></ul></li><li>For valid <b>resolution</b> values\: <ul><li>Log in to the JIRA server from the UI</li><li>Go to http\://my\_jira\_ip/rest/api/2/resolution</li><li>The returned JSON should contain a list of resolutions</li><li>The name field in each resolution denotes the value to be used</li></ul></li></ul>\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket \(issue\) key | string |  `jira ticket key` 
**status** |  required  | Status to set | string |  `jira ticket status` 
**resolution** |  optional  | Resolution to set | string |  `jira ticket resolution` 
**comment** |  optional  | Comment to set | string | 
**update\_fields** |  optional  | JSON containing field values | string | 
**time\_spent** |  optional  | Time Spent to Log | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.resolution | string |  `jira ticket resolution` 
action\_result\.parameter\.status | string |  `jira ticket status` 
action\_result\.parameter\.time\_spent | string | 
action\_result\.parameter\.update\_fields | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.fields\. | string | 
action\_result\.data\.\*\.fields\.Chinese 文字\- Kanji 漢字\- Hanja 漢字\(UTF\-8\) | string | 
action\_result\.data\.\*\.fields\.Custom Checkbox Field Three | string | 
action\_result\.data\.\*\.fields\.Custom Label Field Two | string | 
action\_result\.data\.\*\.fields\.Custom Text Field One | string | 
action\_result\.data\.\*\.fields\.CustomerSanText | string | 
action\_result\.data\.\*\.fields\.Domain Test | string | 
action\_result\.data\.\*\.fields\.Epic Link | string | 
action\_result\.data\.\*\.fields\.Phantom Test | string | 
action\_result\.data\.\*\.fields\.Severity | string | 
action\_result\.data\.\*\.fields\.Sprint | string | 
action\_result\.data\.\*\.fields\.Test1 | string | 
action\_result\.data\.\*\.fields\.Test\_label1 | string | 
action\_result\.data\.\*\.fields\.Test\_user\_field\_cf | string | 
action\_result\.data\.\*\.fields\.\["á é í ó ú à è ë ï ö ü ĳ ë, ï, ü"\] | string | 
action\_result\.data\.\*\.fields\.\["こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，"\] | string | 
action\_result\.data\.\*\.fields\.aggregateprogress\.percent | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.progress | numeric | 
action\_result\.data\.\*\.fields\.aggregateprogress\.total | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeestimate | numeric | 
action\_result\.data\.\*\.fields\.aggregatetimeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.aggregatetimespent | numeric | 
action\_result\.data\.\*\.fields\.assignee | string | 
action\_result\.data\.\*\.fields\.assignee\.active | boolean | 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.assignee\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.assignee\.key | string | 
action\_result\.data\.\*\.fields\.assignee\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.assignee\.self | string |  `url` 
action\_result\.data\.\*\.fields\.assignee\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.content | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.created | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.filename | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.id | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.mimeType | string | 
action\_result\.data\.\*\.fields\.attachment\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.attachment\.\*\.size | numeric | 
action\_result\.data\.\*\.fields\.attachment\.\*\.thumbnail | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.body | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.created | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.id | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.active | boolean | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.key | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.self | string |  `url` 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updateAuthor\.timeZone | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.updated | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.type | string | 
action\_result\.data\.\*\.fields\.comment\.comments\.\*\.visibility\.value | string | 
action\_result\.data\.\*\.fields\.comment\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.comment\.startAt | numeric | 
action\_result\.data\.\*\.fields\.comment\.total | numeric | 
action\_result\.data\.\*\.fields\.components\.\*\.id | string | 
action\_result\.data\.\*\.fields\.components\.\*\.name | string | 
action\_result\.data\.\*\.fields\.components\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.created | string | 
action\_result\.data\.\*\.fields\.creator\.active | boolean | 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.creator\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.creator\.key | string | 
action\_result\.data\.\*\.fields\.creator\.name | string | 
action\_result\.data\.\*\.fields\.creator\.self | string |  `url` 
action\_result\.data\.\*\.fields\.creator\.timeZone | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10000\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10002\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10100 | string | 
action\_result\.data\.\*\.fields\.customfield\_10101 | string | 
action\_result\.data\.\*\.fields\.customfield\_10104 | string | 
action\_result\.data\.\*\.fields\.customfield\_10106 | string | 
action\_result\.data\.\*\.fields\.customfield\_10109 | string | 
action\_result\.data\.\*\.fields\.customfield\_10200 | string | 
action\_result\.data\.\*\.fields\.customfield\_10201 | string | 
action\_result\.data\.\*\.fields\.customfield\_10202 | string | 
action\_result\.data\.\*\.fields\.customfield\_10300 | string | 
action\_result\.data\.\*\.fields\.customfield\_10301 | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.errorMessage | string | 
action\_result\.data\.\*\.fields\.customfield\_10400\.i18nErrorMessage\.i18nKey | string | 
action\_result\.data\.\*\.fields\.customfield\_10401 | string | 
action\_result\.data\.\*\.fields\.customfield\_10402 | string | 
action\_result\.data\.\*\.fields\.customfield\_10500 | string | 
action\_result\.data\.\*\.fields\.customfield\_10501 | string | 
action\_result\.data\.\*\.fields\.customfield\_10600 | string | 
action\_result\.data\.\*\.fields\.customfield\_10601 | string | 
action\_result\.data\.\*\.fields\.customfield\_10602 | string | 
action\_result\.data\.\*\.fields\.customfield\_10603 | string | 
action\_result\.data\.\*\.fields\.customfield\_10605 | string | 
action\_result\.data\.\*\.fields\.customfield\_10606 | string | 
action\_result\.data\.\*\.fields\.customfield\_10701 | string | 
action\_result\.data\.\*\.fields\.customfield\_10702 | string | 
action\_result\.data\.\*\.fields\.customfield\_10703 | string | 
action\_result\.data\.\*\.fields\.customfield\_10704 | string | 
action\_result\.data\.\*\.fields\.customfield\_10801 | string | 
action\_result\.data\.\*\.fields\.customfield\_10802 | string | 
action\_result\.data\.\*\.fields\.customfield\_10900 | string | 
action\_result\.data\.\*\.fields\.customfield\_10901 | string | 
action\_result\.data\.\*\.fields\.customfield\_10902 | string | 
action\_result\.data\.\*\.fields\.customfield\_10903 | string | 
action\_result\.data\.\*\.fields\.customfield\_10904 | string | 
action\_result\.data\.\*\.fields\.customfield\_10905 | string | 
action\_result\.data\.\*\.fields\.customfield\_10906 | string | 
action\_result\.data\.\*\.fields\.customfield\_10907 | string | 
action\_result\.data\.\*\.fields\.customfield\_10908 | string | 
action\_result\.data\.\*\.fields\.customfield\_10909 | string | 
action\_result\.data\.\*\.fields\.customfield\_10910 | string | 
action\_result\.data\.\*\.fields\.customfield\_10911 | string | 
action\_result\.data\.\*\.fields\.customfield\_10912 | string | 
action\_result\.data\.\*\.fields\.customfield\_10913 | string | 
action\_result\.data\.\*\.fields\.customfield\_10914 | string | 
action\_result\.data\.\*\.fields\.customfield\_10915 | string | 
action\_result\.data\.\*\.fields\.customfield\_10916 | string | 
action\_result\.data\.\*\.fields\.customfield\_10917 | string | 
action\_result\.data\.\*\.fields\.customfield\_10918 | string | 
action\_result\.data\.\*\.fields\.customfield\_10919 | string | 
action\_result\.data\.\*\.fields\.customfield\_10920 | string | 
action\_result\.data\.\*\.fields\.customfield\_10921 | string | 
action\_result\.data\.\*\.fields\.customfield\_10922 | string | 
action\_result\.data\.\*\.fields\.customfield\_10923 | string | 
action\_result\.data\.\*\.fields\.customfield\_10924 | string | 
action\_result\.data\.\*\.fields\.customfield\_10925 | string | 
action\_result\.data\.\*\.fields\.customfield\_10926 | string | 
action\_result\.data\.\*\.fields\.customfield\_10927 | string | 
action\_result\.data\.\*\.fields\.customfield\_11000 | string | 
action\_result\.data\.\*\.fields\.customfield\_11001 | string | 
action\_result\.data\.\*\.fields\.customfield\_11002 | string | 
action\_result\.data\.\*\.fields\.customfield\_11003 | string | 
action\_result\.data\.\*\.fields\.customfield\_11100 | string | 
action\_result\.data\.\*\.fields\.customfield\_11101 | string | 
action\_result\.data\.\*\.fields\.customfield\_11102 | string | 
action\_result\.data\.\*\.fields\.customfield\_11103 | string | 
action\_result\.data\.\*\.fields\.customtextfield1 | string | 
action\_result\.data\.\*\.fields\.description | string | 
action\_result\.data\.\*\.fields\.duedate | string | 
action\_result\.data\.\*\.fields\.environment | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.fixVersions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.priority\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.status\.statusCategory\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.inwardIssue\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.priority\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.iconUrl | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.status\.statusCategory\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.key | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.outwardIssue\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.self | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.id | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.inward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.name | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.outward | string | 
action\_result\.data\.\*\.fields\.issuelinks\.\*\.type\.self | string | 
action\_result\.data\.\*\.fields\.issuetype\.avatarId | numeric | 
action\_result\.data\.\*\.fields\.issuetype\.description | string | 
action\_result\.data\.\*\.fields\.issuetype\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.id | string | 
action\_result\.data\.\*\.fields\.issuetype\.name | string |  `jira issue type` 
action\_result\.data\.\*\.fields\.issuetype\.self | string |  `url` 
action\_result\.data\.\*\.fields\.issuetype\.subtask | boolean | 
action\_result\.data\.\*\.fields\.labels | string | 
action\_result\.data\.\*\.fields\.lastViewed | string | 
action\_result\.data\.\*\.fields\.priority\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.priority\.id | string | 
action\_result\.data\.\*\.fields\.priority\.name | string |  `jira ticket priority` 
action\_result\.data\.\*\.fields\.priority\.self | string |  `url` 
action\_result\.data\.\*\.fields\.progress\.percent | numeric | 
action\_result\.data\.\*\.fields\.progress\.progress | numeric | 
action\_result\.data\.\*\.fields\.progress\.total | numeric | 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.project\.id | string | 
action\_result\.data\.\*\.fields\.project\.key | string |  `jira project key` 
action\_result\.data\.\*\.fields\.project\.name | string | 
action\_result\.data\.\*\.fields\.project\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.active | boolean | 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.16x16 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.24x24 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.32x32 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.avatarUrls\.48x48 | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.displayName | string |  `jira user display name` 
action\_result\.data\.\*\.fields\.reporter\.emailAddress | string |  `email` 
action\_result\.data\.\*\.fields\.reporter\.key | string | 
action\_result\.data\.\*\.fields\.reporter\.name | string |  `user name` 
action\_result\.data\.\*\.fields\.reporter\.self | string |  `url` 
action\_result\.data\.\*\.fields\.reporter\.timeZone | string | 
action\_result\.data\.\*\.fields\.resolution | string | 
action\_result\.data\.\*\.fields\.resolution\.description | string | 
action\_result\.data\.\*\.fields\.resolution\.id | string | 
action\_result\.data\.\*\.fields\.resolution\.name | string |  `jira ticket resolution` 
action\_result\.data\.\*\.fields\.resolution\.self | string |  `url` 
action\_result\.data\.\*\.fields\.resolutiondate | string | 
action\_result\.data\.\*\.fields\.status\.description | string | 
action\_result\.data\.\*\.fields\.status\.iconUrl | string |  `url` 
action\_result\.data\.\*\.fields\.status\.id | string | 
action\_result\.data\.\*\.fields\.status\.name | string | 
action\_result\.data\.\*\.fields\.status\.self | string |  `url` 
action\_result\.data\.\*\.fields\.status\.statusCategory\.colorName | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.id | numeric | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.key | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.name | string | 
action\_result\.data\.\*\.fields\.status\.statusCategory\.self | string |  `url` 
action\_result\.data\.\*\.fields\.summary | string | 
action\_result\.data\.\*\.fields\.timeestimate | numeric | 
action\_result\.data\.\*\.fields\.timeoriginalestimate | string | 
action\_result\.data\.\*\.fields\.timespent | numeric | 
action\_result\.data\.\*\.fields\.timetracking\.remainingEstimate | string | 
action\_result\.data\.\*\.fields\.timetracking\.remainingEstimateSeconds | numeric | 
action\_result\.data\.\*\.fields\.timetracking\.timeSpent | string | 
action\_result\.data\.\*\.fields\.timetracking\.timeSpentSeconds | numeric | 
action\_result\.data\.\*\.fields\.updated | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.archived | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.id | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.name | string | 
action\_result\.data\.\*\.fields\.versions\.\*\.released | boolean | 
action\_result\.data\.\*\.fields\.versions\.\*\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.hasVoted | boolean | 
action\_result\.data\.\*\.fields\.votes\.self | string |  `url` 
action\_result\.data\.\*\.fields\.votes\.votes | numeric | 
action\_result\.data\.\*\.fields\.watches\.isWatching | boolean | 
action\_result\.data\.\*\.fields\.watches\.self | string |  `url` 
action\_result\.data\.\*\.fields\.watches\.watchCount | numeric | 
action\_result\.data\.\*\.fields\.worklog\.maxResults | numeric | 
action\_result\.data\.\*\.fields\.worklog\.startAt | numeric | 
action\_result\.data\.\*\.fields\.worklog\.total | numeric | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.active | boolean | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.avatarUrls\.16x16 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.avatarUrls\.24x24 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.avatarUrls\.32x32 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.avatarUrls\.48x48 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.displayName | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.emailAddress | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.key | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.name | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.self | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.author\.timeZone | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.comment | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.created | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.id | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.issueId | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.self | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.started | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.timeSpent | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.timeSpentSeconds | numeric | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.active | boolean | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.avatarUrls\.16x16 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.avatarUrls\.24x24 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.avatarUrls\.32x32 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.avatarUrls\.48x48 | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.displayName | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.emailAddress | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.key | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.name | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.self | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updateAuthor\.timeZone | string | 
action\_result\.data\.\*\.fields\.worklog\.worklogs\.\*\.updated | string | 
action\_result\.data\.\*\.fields\.workratio | numeric | 
action\_result\.data\.\*\.fields\.こ֍漢<ਊḈឦᡤᇗ∰᳀字过亿，日活百万\+的漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリティインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€	₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\#$%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à è ë ï ö ü ĳ ë, ï, üاردو تہجی | string | 
action\_result\.data\.\*\.fields\.漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリテ ィインシデント日本標準時⛰⛱⛲⛳⛵✔️❤️ﬗ╬⎋⌚⅍ⅎ€ ₭⁂ᾧ҈₮₯⅏⌛⎎☆Ḃ平仮名, ひらがな~\!\@\# $%^&\*\(\)\_\+<>?\:"\}\|\{,\./;'\[\]\\/\`á é í ó ú à ë ï ö üاردو تہجیગુજરાતીहिन्दीгуджаратиგუჯარათიগুজরাটি | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.issue\_type | string |  `jira issue type` 
action\_result\.data\.\*\.name | string |  `jira ticket key` 
action\_result\.data\.\*\.priority | string |  `jira ticket priority` 
action\_result\.data\.\*\.project\_key | string |  `jira project key` 
action\_result\.data\.\*\.reporter | string |  `jira user display name` 
action\_result\.data\.\*\.resolution | string |  `jira ticket resolution` 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.summary | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'link tickets'
Create a link between two separate tickets

Type: **generic**  
Read only: **False**

If the comment is not added, comment\_visibility and comment\_visibility\_type values will not affect the action result\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**from\_id** |  required  | First ticket \(issue\) key | string |  `jira ticket key` 
**to\_id** |  required  | Second ticket \(issue\) key | string |  `jira ticket key` 
**link\_type** |  required  | Type of link to create | string | 
**comment** |  optional  | Comment to add | string | 
**comment\_visibility\_type** |  optional  | How to limit the comment visibility | string | 
**comment\_visibility\_name** |  optional  | Name of group/role able to see the comment | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.comment\_visibility\_name | string | 
action\_result\.parameter\.comment\_visibility\_type | string | 
action\_result\.parameter\.from\_id | string |  `jira ticket key` 
action\_result\.parameter\.link\_type | string | 
action\_result\.parameter\.to\_id | string |  `jira ticket key` 
action\_result\.data\.\*\.result | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'add watcher'
Add a user to an issue's watchers list

Type: **generic**  
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites\. They are also removing username support from their product APIs for Jira Cloud\. Since it is not possible to add a watcher using username for Jira cloud, we will use a user's account\_id to add a watcher for Jira cloud\. Use 'lookup users' action to find out a user's account\_id\. You can use the \[user\_account\_id\] action parameter to add a watcher to the Jira ticket for Jira cloud, and, \[username\] action parameter will be used to add a watcher to the Jira ticket for Jira on\-prem\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**username** |  optional  | Username of the user to add to the watchers list \(required for Jira on\-prem\) | string |  `user name` 
**user\_account\_id** |  optional  | Account ID of the user to add to the watchers list \(required for Jira cloud\) | string |  `jira user account id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.user\_account\_id | string |  `jira user account id` 
action\_result\.parameter\.username | string |  `user name` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'remove watcher'
Remove a user from an issue's watchers list

Type: **generic**  
Read only: **False**

<h3>Caveats</h3>Jira Cloud is removing the username field from user profiles in Atlassian Cloud sites\. They are also removing username support from their product APIs for Jira Cloud\. Since it is not possible to remove a watcher using username for Jira cloud, we will use a user's account\_id to remove a watcher for Jira cloud\. Use 'lookup users' action to find out a user's account\_id\. You can use the \[user\_account\_id\] action parameter to remove a watcher from the Jira ticket for Jira cloud, and, \[username\] action parameter will be used to remove a watcher from the Jira ticket for Jira on\-prem\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Issue ID | string |  `jira ticket key` 
**username** |  optional  | Username of the user to remove from watchers list \(required for Jira on\-prem\) | string |  `user name` 
**user\_account\_id** |  optional  | Account ID of the user to remove from the watchers list \(required for Jira cloud\) | string |  `jira user account id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `jira ticket key` 
action\_result\.parameter\.user\_account\_id | string |  `jira user account id` 
action\_result\.parameter\.username | string |  `user name` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'on poll'
Ingest tickets from JIRA

Type: **ingest**  
Read only: **True**

Basic configuration parameters for this action are available in the asset configuration\.<br><br>If the <b>project\_key</b> parameter is set, polling will only ingest tickets \(issues\) from the specified project\.<br><br>If the <b>query</b> parameter is set, polling will filter tickets based on the JQL query specified in the parameter\.<br><br>If the <b>first\_run\_max\_tickets</b> parameter is set, the first poll will only ingest up to the specified amount of tickets\. If the field is left empty, the first poll will ingest all the available tickets\.<br><br>If the <b>max\_tickets</b> parameter is set, each poll will ingest only up to the specified amount of newly updated tickets\. If the field is left empty, all tickets available at the time of the poll will be ingested\.<br><br>During each polling interval, the app will query the JIRA server for tickets that have been updated since the previous poll\. The app will check if each ticket has already been ingested, if it has not, it will create a new container for the ticket\. An artifact will be created in the container that will have a selection of the ticket's fields listed as CEF fields\. All the data of tickets will be added to the container's data field\. Each attachment and comment on the ticket will be ingested as artifacts\. All attachments will also be added to the vault\. If a ticket has been previously ingested, the app will update the ticket container's data field\. The app will also add a new artifact with updated fields and it will add new artifacts for new comments and attachments\. If a comment on a ticket is edited, a new artifact will be added to the container\.<br><br>For a poll now, the app will ingest as many tickets as specified by the <b>container\_count</b>\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start\_time** |  optional  | Parameter ignored in this app | numeric | 
**end\_time** |  optional  | Parameter ignored in this app | numeric | 
**container\_id** |  optional  | Parameter ignored in this app | string | 
**container\_count** |  optional  | Maximum number of tickets to be ingested during poll now | numeric | 
**artifact\_count** |  optional  | Parameter ignored in this app | numeric | 

#### Action Output
No Output