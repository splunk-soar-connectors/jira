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
import json as _json
from typing import Any

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import MakeRequestParams


from .._asset import Asset
from ..client import JiraClient


def make_request(
    params: MakeRequestParams, soar: SOARClient, asset: Asset
) -> MakeRequestOutput:
    """Make a custom REST API call to Jira.

    Use this action to call any Jira REST API endpoint not covered by the other actions.
    The endpoint parameter is the path after the base device URL,
    e.g. rest/api/2/issue/PROJ-1 or rest/api/2/project.
    The full response body is returned as a string in response_body.
    """
    logger = getLogger()

    raw_body: str | None = None
    json_body: Any | None = None
    if params.body:
        content_type = "application/json"
        if params.headers:
            try:
                header_values = _json.loads(params.headers)
                if isinstance(header_values, dict):
                    content_type = next(
                        (
                            value
                            for key, value in header_values.items()
                            if isinstance(key, str) and key.lower() == "content-type"
                        ),
                        content_type,
                    )
            except (_json.JSONDecodeError, TypeError):
                pass
        if isinstance(content_type, str) and "json" in content_type.lower():
            try:
                json_body = _json.loads(params.body)
            except (_json.JSONDecodeError, TypeError) as exc:
                raise ActionFailure(f"Invalid JSON in 'body' parameter: {exc}") from exc
        else:
            raw_body = params.body

    query_dict: dict | None = None
    endpoint = params.endpoint
    if params.query_parameters:
        try:
            parsed_query = _json.loads(params.query_parameters)
        except (_json.JSONDecodeError, TypeError):
            query_string = params.query_parameters.removeprefix("?")
            separator = "&" if "?" in endpoint else "?"
            endpoint = f"{endpoint}{separator}{query_string}"
        else:
            if not isinstance(parsed_query, dict):
                raise ActionFailure("query_parameters JSON must be an object")
            query_dict = parsed_query

    timeout = float(params.timeout) if params.timeout else 60.0

    extra_headers: dict[str, str] = {}
    if params.headers:
        try:
            parsed_headers = _json.loads(params.headers)
        except (_json.JSONDecodeError, TypeError) as exc:
            raise ActionFailure(f"Invalid JSON in 'headers' parameter: {exc}") from exc
        if not isinstance(parsed_headers, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in parsed_headers.items()
        ):
            raise ActionFailure(
                "headers JSON must be an object with string keys and values"
            )
        extra_headers = parsed_headers

    logger.info(f"Making {params.http_method} request to {endpoint}")

    response = JiraClient(asset).request(
        params.http_method,
        endpoint,
        params=query_dict,
        json=json_body,
        data=raw_body,
        headers=extra_headers,
        timeout=timeout,
        verify_ssl=params.verify_ssl,
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
