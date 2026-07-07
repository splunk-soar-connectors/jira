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
from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.params import MakeRequestParams


from .._asset import Asset


def make_request(
    params: MakeRequestParams, soar: SOARClient, asset: Asset
) -> MakeRequestOutput:
    """Make a custom REST API call to Jira.

    Use this action to call any Jira REST API endpoint not covered by the other actions.
    The endpoint parameter is the path after the base device URL,
    e.g. rest/api/2/issue/PROJ-1 or rest/api/2/project.
    The full response body is returned as a string in response_body.
    """
    import json as _json

    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..client import call_jira

    logger = getLogger()

    body_dict = None
    if params.body:
        try:
            body_dict = _json.loads(params.body)
        except Exception as exc:
            raise ActionFailure(f"Invalid JSON in 'body' parameter: {exc}") from exc

    query_dict = None
    if params.query_parameters:
        try:
            query_dict = _json.loads(params.query_parameters)
        except Exception as exc:
            raise ActionFailure(
                f"Invalid JSON in 'query_parameters' parameter: {exc}"
            ) from exc

    timeout = float(params.timeout) if params.timeout else 60.0

    extra_headers: dict = {}
    if params.headers:
        try:
            extra_headers.update(_json.loads(params.headers))
        except Exception as exc:
            raise ActionFailure(f"Invalid JSON in 'headers' parameter: {exc}") from exc

    logger.info(f"Making {params.http_method} request to {params.endpoint}")

    response = call_jira(
        params.http_method,
        params.endpoint,
        asset,
        params=query_dict,
        json=body_dict,
        headers=extra_headers,
        timeout=timeout,
    )

    logger.info(f"Response: {response.status_code}")

    if not response.is_success:
        raise ActionFailure(
            f"Jira API error {response.status_code}: {response.text or 'no response body'}"
        )

    return MakeRequestOutput(
        response_body=response.text or "{}",
        status_code=float(response.status_code),
    )
