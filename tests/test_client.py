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
from io import BytesIO

import httpx
import pytest

import src.client as client_module
from src._asset import Asset
from src.client import JiraClient
from soar_sdk.exceptions import ActionFailure


@pytest.fixture
def asset():
    return Asset(
        device_url="https://jira.example",
        username="user",
        password="token",  # pragma: allowlist secret
    )


def test_request_json_uses_central_transport(monkeypatch, asset):
    calls = []

    def fake_transport(method, endpoint, request_asset, **kwargs):
        calls.append((method, endpoint, request_asset, kwargs))
        return httpx.Response(200, json={"issues": []})

    monkeypatch.setattr(client_module, "_call_jira", fake_transport)

    result = JiraClient(asset).request_json(
        "GET", "rest/api/2/search/jql", params={"jql": "project=SEC"}
    )

    assert result == {"issues": []}
    assert calls[0][0:2] == ("GET", "rest/api/2/search/jql")
    assert calls[0][3]["params"] == {"jql": "project=SEC"}


def test_request_json_translates_api_errors(monkeypatch, asset):
    response = httpx.Response(
        400,
        json={"errorMessages": ["Invalid JQL"], "errors": {"jql": "bad query"}},
        headers={"content-type": "application/json"},
    )
    monkeypatch.setattr(client_module, "_call_jira", lambda *args, **kwargs: response)

    with pytest.raises(ActionFailure, match="Invalid JQL; jql: bad query"):
        JiraClient(asset).request_json("GET", "rest/api/2/search/jql")


def test_download_routes_absolute_url_through_streaming_transport(monkeypatch, asset):
    calls = []
    real_client = httpx.Client

    def transport(request):
        calls.append(request)
        return httpx.Response(200, content=b"attachment")

    monkeypatch.setattr(
        client_module.httpx,
        "Client",
        lambda **kwargs: real_client(
            transport=httpx.MockTransport(transport), **kwargs
        ),
    )
    content = JiraClient(asset).download("https://jira.example/secure/file.txt")
    assert content == b"attachment"
    assert str(calls[0].url) == "https://jira.example/secure/file.txt"
    assert calls[0].headers["Accept"] == "*/*"
    assert calls[0].headers["Authorization"].startswith("Basic ")


def test_request_rejects_absolute_endpoint_before_applying_auth(asset):
    with pytest.raises(ActionFailure, match="Invalid Jira endpoint"):
        JiraClient(asset).request("GET", "https://attacker.example/collect")


def test_download_rejects_attachment_url_outside_jira_origin(asset):
    with pytest.raises(ActionFailure, match="outside the configured Jira origin"):
        JiraClient(asset).download("https://attacker.example/file.txt")


def test_semantic_client_methods_all_use_rest_transport(monkeypatch, asset):
    calls = []

    def fake_transport(method, endpoint, request_asset, **kwargs):
        calls.append((method, endpoint, request_asset, kwargs))
        payload = {
            "rest/api/2/project": [{"id": "100"}],
            "rest/api/2/search/jql": {"issues": []},
            "rest/api/2/user/search": [],
            "rest/api/2/issue/SEC-1/watchers": {"watchers": []},
            "rest/api/2/issue": {"id": "100", "key": "SEC-1"},
            "rest/api/2/issueLinkType": {"issueLinkTypes": []},
            "rest/api/2/issue/SEC-1/transitions": {"transitions": []},
            "rest/api/2/resolution": [],
        }.get(endpoint, {"id": "100", "key": "SEC-1", "fields": {}})
        return httpx.Response(200, json=payload)

    monkeypatch.setattr(client_module, "_call_jira", fake_transport)
    client = JiraClient(asset)

    assert client.issue("SEC-1")["key"] == "SEC-1"
    assert client.projects() == [{"id": "100"}]
    assert client.search_issues("project=SEC") == {"issues": []}
    assert client.search_users(display_name="Analyst") == []
    assert client.watchers("SEC-1") == {"watchers": []}
    client.add_watcher("SEC-1", "account-id", account_id=True)
    client.remove_watcher("SEC-1", "account-id", account_id=True)
    assert client.create_issue({"summary": "Test"})["key"] == "SEC-1"
    client.update_issue("SEC-1", fields={"summary": "Updated"})
    client.delete_issue("SEC-1")
    client.add_comment("SEC-1", "Comment", internal=True)
    client.add_attachment("SEC-1", BytesIO(b"contents"), "test.txt")
    assert client.issue_link_types() == []
    client.create_issue_link("Blocks", "SEC-1", "SEC-2")
    client.assign_issue("SEC-1", "account-id", account_id=True)
    assert client.transitions("SEC-1") == []
    assert client.resolutions() == []
    client.add_worklog("SEC-1", "1h")
    client.transition_issue("SEC-1", "21")

    assert [(method, endpoint) for method, endpoint, _, _ in calls] == [
        ("GET", "rest/api/2/issue/SEC-1"),
        ("GET", "rest/api/2/project"),
        ("GET", "rest/api/2/search/jql"),
        ("GET", "rest/api/2/user/search"),
        ("GET", "rest/api/2/issue/SEC-1/watchers"),
        ("POST", "rest/api/2/issue/SEC-1/watchers"),
        ("DELETE", "rest/api/2/issue/SEC-1/watchers"),
        ("POST", "rest/api/2/issue"),
        ("PUT", "rest/api/2/issue/SEC-1"),
        ("DELETE", "rest/api/2/issue/SEC-1"),
        ("POST", "rest/api/2/issue/SEC-1/comment"),
        ("POST", "rest/api/2/issue/SEC-1/attachments"),
        ("GET", "rest/api/2/issueLinkType"),
        ("POST", "rest/api/2/issueLink"),
        ("PUT", "rest/api/2/issue/SEC-1/assignee"),
        ("GET", "rest/api/2/issue/SEC-1/transitions"),
        ("GET", "rest/api/2/resolution"),
        ("POST", "rest/api/2/issue/SEC-1/worklog"),
        ("POST", "rest/api/2/issue/SEC-1/transitions"),
    ]
    assert calls[2][3]["params"] == {
        "jql": "project=SEC",
        "maxResults": 100,
        "fields": "*all",
    }
