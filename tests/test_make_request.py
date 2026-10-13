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
"""Tests for the Jira custom REST request action."""

import importlib

import httpx
import pytest

from src._asset import Asset
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams

make_request_module = importlib.import_module("src.actions.make_request")


class FakeJiraClient:
    def __init__(self):
        self.calls = []

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return httpx.Response(200, text="{}")


class FakeSOAR:
    pass


@pytest.fixture
def asset():
    return Asset(
        device_url="https://jira.example",
        username="user",
        password="token",  # pragma: allowlist secret
    )


def test_make_request_supports_raw_query_and_honors_verify_ssl(monkeypatch, asset):
    client = FakeJiraClient()
    monkeypatch.setattr(make_request_module, "JiraClient", lambda _: client)
    params = MakeRequestParams(
        http_method="POST",
        endpoint="rest/api/2/issue",
        query_parameters="?notifyUsers=false",
        headers='{"X-Test": "value"}',
        body='{"summary": "Test"}',
        verify_ssl=False,
    )

    make_request_module.make_request(params, FakeSOAR(), asset)

    args, kwargs = client.calls[0]
    assert args == ("POST", "rest/api/2/issue?notifyUsers=false")
    assert kwargs["headers"] == {"X-Test": "value"}
    assert kwargs["json"] == {"summary": "Test"}
    assert kwargs["verify_ssl"] is False


@pytest.mark.parametrize(
    ("headers", "body", "expected_json", "expected_data"),
    [
        (None, '"account-id"', "account-id", None),
        ('{"content-type": "text/plain"}', "plain text", None, "plain text"),
    ],
)
def test_make_request_supports_json_primitives_and_raw_text(
    monkeypatch, asset, headers, body, expected_json, expected_data
):
    client = FakeJiraClient()
    monkeypatch.setattr(make_request_module, "JiraClient", lambda _: client)
    param_values = {
        "http_method": "POST",
        "endpoint": "rest/api/2/issue/SEC-1/watchers",
        "body": body,
    }
    if headers is not None:
        param_values["headers"] = headers
    params = MakeRequestParams(**param_values)

    make_request_module.make_request(params, FakeSOAR(), asset)

    _, kwargs = client.calls[0]
    assert kwargs["json"] == expected_json
    assert kwargs["data"] == expected_data


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("query_parameters", "[]", "query_parameters JSON must be an object"),
        ("headers", "[]", "headers JSON must be an object"),
    ],
)
def test_make_request_rejects_non_object_json(field, value, message, asset):
    kwargs = {"http_method": "GET", "endpoint": "rest/api/2/project", field: value}

    with pytest.raises(ActionFailure, match=message):
        make_request_module.make_request(MakeRequestParams(**kwargs), FakeSOAR(), asset)
