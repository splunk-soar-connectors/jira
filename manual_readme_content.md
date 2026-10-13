## Backward compatibility

**Version Requirements**

- This app now requires minimum Splunk SOAR version 7.0.0 and will not support versions below 7.0.0.

**Major Changes**

- **JIRA Cloud List Tickets Behavior Change**: Previously, if you provided an invalid project ID or query in the "list tickets" action, it would fail with an error. Now for JIRA Cloud instances, it will pass and return 0 tickets instead of failing. This provides better error handling and prevents workflow interruption.
- This SDK version supports Jira Cloud. Jira Server and Data Center deployments must continue using the legacy connector.
- Existing gateway URLs (`https://api.atlassian.com/ex/jira/{cloudId}`) remain supported. Service-account assets may also use a site URL; the app resolves its cloud ID automatically.
- OAuth requires both `client_id` and `client_secret`. Incomplete OAuth configuration is an error.
- Existing ticket keys and positive numeric issue IDs remain supported. Custom-field names on existing issues are resolved using that issue's editable fields. For creation, supply explicit Jira field IDs.
- SDK result tables replace the legacy custom widgets. Legacy selectable whole-field datapaths are retained alongside nested SDK paths.

## JIRA

JIRA is a highly configurable ticketing system, and the actions performed by these API calls are
highly dependent on the process defined in each Jira instance.

If your action fails, you may need to try an alternate method, or sequence, to perform the actions
desired for Jira to process them properly. One helpful debugging tool: simplify your action, instead
of filling out all the fields, attempt to make only one change at a time.

Unfortunately, the JIRA API in most cases returns a generic error message with no valuable
information to assist in debugging.

**Playbook Backward Compatibility**

- The existing action parameters have been modified in the actions given below. Hence, it is
  requested to the end-user to please update their existing playbooks by re-inserting the
  corresponding action blocks or by providing appropriate values to these action parameters to
  ensure the correct functioning of the playbooks created on the earlier versions of the app.

  - Add Watcher - The new [user_account_id] parameter has been added for the Jira cloud to add
    a watcher into a provided issue.
  - Remove Watcher - The new [user_account_id] parameter has been added for the Jira cloud to
    remove a watcher from a provided issue.
  - Create Ticket - The new [assignee_account_id] parameter has been added for the Jira cloud
    to add the assignee while creating a Jira ticket.
  - Lookup Users - Added a new action. This action will get a list of User resources that match
    the specified search string.
  - Add Comment - The new [internal] parameter has been added for comment that whether it
    should be internal only or not in Jira Service Desk. This parameter is an optional Boolean
    parameter. If the value is not provided for it, then it defaults to `True` (internal comment). Specify `False` explicitly for a public comment.
  - Get Attachments - Added a new action. The action will store specific attachments from a
    given Jira ticket inside the vault.
  - Make Request - Added a new action. This action allows playbooks to call any Jira REST API
    endpoint directly using any HTTP method, with optional headers, query parameters, and body.

**Authentication steps for JIRA Cloud**

- Create an API token

  - Log in to [Click here.](https://id.atlassian.com/manage/api-tokens)

  - Click **Create an API token.**

  - From the dialog that appears, enter a unique and concise **Label** for your token and click
    **Create** .

  - Click **Copy to clipboard** , then paste the token to your script, or elsewhere to save.

    Notes:

  - For security reasons it isn't possible to view the token after closing the creation dialog;
    if necessary, create a new token.

  - You should store the token securely, just as for any password.

- Use an API token

  - A primary use case for API tokens is to allow scripts to access REST APIs for Atlassian
    Cloud applications using HTTP basic authentication.
  - HTTP basic authentication would require a username and API token to access REST APIs for
    Atlassian Cloud applications.

**Service-account authentication and migration**

Configure the service-account email and API token for Basic authentication, or provide both OAuth client credentials. OAuth takes priority. Existing gateway device URLs remain valid. Password-only Bearer authentication is retained; on-premises PAT deployments require the legacy connector.

When upgrading an existing asset, verify test connectivity, Poll Now, its configured ingest label, existing playbook datapaths and attachment retrieval. The SDK's connectivity hook uses the identifier `test_connectivity`.

**The functioning of On Poll**

- Jira Cloud issue search returns the issue fields, comments and attachment metadata used to create or update one SOAR container per issue.
- Poll Now uses the requested `container_count` and does not change scheduled polling state. The action form defaults to one container. Scheduled polling uses `max_tickets` (default 100); the first scheduled run uses `first_run_max_tickets` (default 1000).
- Scheduled searches overlap the last checkpoint by one minute because Jira's updated-time filter has minute-level granularity. Legacy checkpoints are migrated when the asset runs the SDK app.
- Container updates, artifact creation and attachment vault imports must succeed before the scheduled checkpoint advances. Polling downloads attachments to temporary files before vault import.
- Set the optional timezone field when Jira's configured timezone differs from the connector host. Jira Cloud uses the instance's default user timezone. Leave it blank to use UTC.
- The `custom_fields` asset setting accepts a JSON list of Jira custom-field names to include in ingested field artifacts. If field metadata cannot be read, ingestion continues with raw Jira field IDs.

**Some example caveats**

- Attempting to set both Status and Resolution fails because the process set by the user doesn't
  require a resolution to be set by the user, such as if there is only one resolution for a
  particular status.
- Attempting to add a comment while setting Status may return success, however, the comment isn't
  posted. In this case, when the status change is made via the Jira UI, no dialogue appears to
  offer any additional input, therefore the API expects the same.
- The "simple" format for the update ticket may not work to add a comment, while the "update"
  method does.
- Test connectivity may fail due to invalid credentials, such as accidentally using the user's
  email address as the authentication login instead of the user's login name.
- While adding an attachment to the Jira ticket using 'Update ticket' or 'Create ticket' actions,
  the app first uploads the original filename. If that attempt fails and the filename contains Unicode characters, it retries with non-ASCII characters removed and the prefix `FILENAME_ASCII_`. Vault metadata associated with the executing container is preferred.

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the Jira server. Below are the default
ports used by the Splunk SOAR Connector.

| SERVICE NAME | TRANSPORT PROTOCOL | PORT |
|--------------|--------------------|------|
| http | tcp | 80 |
| https | tcp | 443 |
