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


from .._app_ref import app
from .._asset import Asset


@app.make_request()
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

    import httpx

    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..helpers import get_auth

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

    base_url = asset.device_url.rstrip("/")
    full_url = f"{base_url}/{params.endpoint.lstrip('/')}"
    auth = get_auth(asset)
    verify = bool(asset.verify_server_cert)

    timeout = float(params.timeout) if params.timeout else 60.0

    headers: dict = {"Accept": "application/json", "Content-Type": "application/json"}
    if params.headers:
        try:
            headers.update(_json.loads(params.headers))
        except Exception as exc:
            raise ActionFailure(f"Invalid JSON in 'headers' parameter: {exc}") from exc

    logger.info(f"Making {params.http_method} request to {full_url}")

    with httpx.Client(verify=verify) as client:
        try:
            response = client.request(
                method=params.http_method.upper(),
                url=full_url,
                params=query_dict,
                json=body_dict,
                headers=headers,
                auth=auth,
                timeout=timeout,
            )
        except httpx.RequestError as exc:
            raise ActionFailure(f"Request to Jira failed: {exc}") from exc

    logger.info(f"Response: {response.status_code}")

    if not response.is_success:
        raise ActionFailure(
            f"Jira API error {response.status_code}: {response.text or 'no response body'}"
        )

    return MakeRequestOutput(
        response_body=response.text or "{}",
        status_code=float(response.status_code),
    )
