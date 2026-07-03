**Unreleased**

* Added `make request` action, which lets playbooks call any Jira REST API endpoint directly. Pass the path after the base device URL (e.g. `rest/api/3/issue/PROJ-1`), optional headers, query parameters, request body, and HTTP method. The full response body and HTTP status code are returned as action output.
* Fixed `on poll`: attachment and comment artifacts now include an `is_on_prem` CEF field set to `true` or `false`. Playbooks that branch on `is_on_prem` will now receive the expected value.
* Fixed `on poll` for Jira Cloud: issue description fields returned in Atlassian Document Format (ADF) are now converted to plain text before being stored in container and artifact fields.
* Improved `on poll` performance: field metadata (used to resolve custom field display names) is now fetched once per poll run instead of once per project, reducing API calls for large ingestions.