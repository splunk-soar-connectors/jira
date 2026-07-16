**Unreleased**
* Jira on-prem is deprecated for this app. If you are still connecting to a Jira on-prem instance, continue using the legacy app version; upgrade to this version only if you are on Jira Cloud.
* Added `make request` action, which lets playbooks call any Jira REST API endpoint directly. Pass the path after the base device URL (e.g. `rest/api/3/issue/PROJ-1`), optional headers, query parameters, request body, and HTTP method. The full response body and HTTP status code are returned as action output.
* Added OAuth 2.0 client credentials authentication for Atlassian service accounts. New asset configuration parameters `client_id` and `client_secret` can be used instead of `username`/`password`; when set, they take priority. Service accounts (username ending in `@serviceaccount.atlassian.com`) using API tokens are also now supported automatically.
* Fixed `add watcher` and `remove watcher`: the `username` parameter (Jira on-prem) had stopped working and always required `user_account_id` (Jira cloud) instead. Both parameters now work as documented, matching their respective deployment type.
* Fixed `on poll` to reject invalid poll limits (`container_count`, `first_run_max_tickets`, `max_tickets`) instead of silently ingesting an unpredictable number of tickets.
* Fixed `on poll` so attachments on newly ingested tickets are reliably saved to the vault.
* Fixed ticket ingestion checkpoints so they carry over when upgrading from the legacy (non-SDK) app version, preventing tickets from being re-ingested from the beginning after an upgrade.
