**Unreleased**
* This app version is built specifically for Jira Cloud. Jira Data Center and Jira Server are not supported. Customers connecting to an on-premises Jira deployment must continue using the legacy app version.
* Fixed `list tickets` pagination for Jira Cloud's cursor-based enhanced search API so that `start_index` and results beyond the first page are handled correctly.
* Added `make request` action, which lets playbooks call any Jira REST API endpoint directly. Pass the path after the base device URL (e.g. `rest/api/3/issue/PROJ-1`), optional headers, query parameters, request body, and HTTP method. The full response body and HTTP status code are returned as action output.
* Added OAuth 2.0 client credentials authentication for Atlassian service accounts. New asset configuration parameters `client_id` and `client_secret` can be used instead of `username`/`password`; when set, they take priority. Service accounts (username ending in `@serviceaccount.atlassian.com`) using API tokens are also now supported automatically.
* Fixed `add watcher` and `remove watcher` handling of the Jira Cloud `user_account_id` parameter.
* Fixed `on poll` to reject invalid poll limits (`container_count`, `first_run_max_tickets`, `max_tickets`) instead of silently ingesting an unpredictable number of tickets.
* Fixed `on poll` so attachments on newly ingested tickets are reliably saved to the vault.
* Fixed ticket ingestion checkpoints so they carry over when upgrading from the legacy (non-SDK) app version, preventing tickets from being re-ingested from the beginning after an upgrade.

* Restored legacy issue-key and positive numeric issue-ID validation for issue-specific actions.
* Preserved existing service-account gateway URLs and corrected authenticated attachment downloads.
* Restored mixed update payload handling, status update validation, contextual custom-field resolution, directional issue links, positive ticket limits, partial-operation messages, original attachment filenames and current-container vault metadata selection.
* Restored empty attachment result semantics, case-sensitive extension filters and unsafe filename failures.
* Preserved raw user lookup response fields and legacy selectable issue datapaths.
* Restored configured ingestion labels and detection of application-level container update failures; polling attachment downloads now stream to disk.
* Incomplete OAuth credential pairs now fail with a configuration error.
