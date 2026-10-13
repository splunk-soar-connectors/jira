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
"""Regression tests for behavior restored from the legacy Jira connector."""

import importlib
from types import SimpleNamespace

import pytest
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import OnPollParams

from src._asset import Asset
from src.client import JiraClient, validate_issue_id
from src.auth import resolve_jira_auth, resolve_jira_base_url
from src.actions.on_poll import on_poll
from src.actions.get_ticket import FieldsOutput
from src.helpers import apply_issue_updates
from src.actions._outputs import JiraPermissiveOutput


@pytest.fixture
def asset():
    return Asset(device_url="https://jira.example", username="user", password="token")


@pytest.mark.parametrize("value", ["SEC-1", "sec-1", "10001"])
def test_issue_policy_accepts_keys_and_positive_numeric_ids(value):
    assert validate_issue_id(value) == value


@pytest.mark.parametrize(
    "value",
    ["../project/SEC", "0", "-1", "SEC-0", "SEC-1?x=2", "https://jira.example/SEC-1"],
)
def test_issue_policy_rejects_non_issue_paths(value):
    with pytest.raises(ActionFailure, match="valid Jira issue"):
        validate_issue_id(value)


def test_client_rejects_invalid_issue_before_transport(monkeypatch, asset):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("transport must not run")

    monkeypatch.setattr("src.client._call_jira", fail_if_called)
    with pytest.raises(ActionFailure):
        JiraClient(asset).delete_issue("../project/SEC")


def test_mixed_update_payload_keeps_fields_operations_and_simple_fields():
    calls = []

    class Client:
        def update_issue(self, issue_id, *, fields=None, update=None):
            calls.append((issue_id, fields, update))

    apply_issue_updates(
        Client(),
        "SEC-1",
        {
            "fields": {"summary": "new"},
            "update": {"labels": [{"add": "x"}]},
            "description": "details",
        },
    )
    assert calls == [
        ("SEC-1", {"summary": "new"}, None),
        ("SEC-1", None, {"labels": [{"add": "x"}]}),
        ("SEC-1", {"description": "details"}, None),
    ]


def test_raw_user_vendor_fields_survive_output_serialization():
    output = JiraPermissiveOutput(id="1", vendorField={"enabled": True})
    assert output.model_dump()["vendorField"] == {"enabled": True}
    assert output.model_dump(by_alias=True)["vendorField"] == {"enabled": True}


def test_lookup_users_preserves_vendor_fields(monkeypatch, asset):
    module = importlib.import_module("src.actions.search_users")

    class Client:
        def search_users(self, **_kwargs):
            return [{"name": "jane", "active": True, "vendorField": "extra"}]

    monkeypatch.setattr(module, "JiraClient", lambda _: Client())
    result = module.lookup_users(
        module.LookupUsersParams(username="jane", max_results=1),
        SimpleNamespace(set_message=lambda *_: None, set_summary=lambda *_: None),
        asset,
    )
    assert result[0].model_dump(by_alias=True)["vendorField"] == "extra"


def test_partial_oauth_credentials_fail_clearly():
    partial = Asset(
        device_url="https://jira.example",
        username="user",
        password="token",
        client_id="id",
    )
    with pytest.raises(ActionFailure, match="both client_id and client_secret"):
        resolve_jira_auth(partial)


def test_existing_gateway_url_does_not_trigger_tenant_lookup(monkeypatch):
    gateway = "https://api.atlassian.com/ex/jira/existing-cloud-id"
    service_asset = Asset(
        device_url=gateway,
        username="bot@serviceaccount.atlassian.com",
        password="token",
    )
    monkeypatch.setattr(
        "src.auth.httpx.get",
        lambda *_a, **_k: pytest.fail("tenant lookup should not run"),
    )
    assert resolve_jira_base_url(service_asset) == gateway


def test_link_inward_alias_reverses_issues(monkeypatch, asset):
    module = importlib.import_module("src.actions.link_tickets")
    calls = []

    class Client:
        def issue_link_types(self):
            return [{"name": "Blocks", "inward": "is blocked by", "outward": "blocks"}]

        def create_issue_link(self, *args):
            calls.append(args)

    monkeypatch.setattr(module, "JiraClient", lambda _: Client())
    module.link_tickets(
        module.LinkTicketsParams(
            from_id="SEC-1", to_id="SEC-2", link_type="is blocked by"
        ),
        SimpleNamespace(set_message=lambda *_: None),
        asset,
    )
    assert calls[0][:3] == ("Blocks", "SEC-2", "SEC-1")


def test_list_tickets_accepts_limit_over_one_thousand(monkeypatch, asset):
    module = importlib.import_module("src.actions.list_tickets")
    requested = []

    class Client:
        def search_issues(self, _jql, **kwargs):
            requested.append(kwargs["max_results"])
            return {"issues": [], "isLast": True}

    monkeypatch.setattr(module, "JiraClient", lambda _: Client())
    monkeypatch.setattr(module, "get_custom_field_map", lambda *_: {})

    class MultiPageClient:
        def search_issues(self, _jql, **kwargs):
            requested.append(kwargs["max_results"])
            start = (len(requested) - 1) * 100
            issues = [
                {"id": str(index), "key": f"SEC-{index}", "fields": {}}
                for index in range(start, min(start + 100, 1500))
            ]
            result = {"issues": issues, "isLast": start + len(issues) >= 1500}
            if not result["isLast"]:
                result["nextPageToken"] = f"page-{len(requested)}"
            return result

    monkeypatch.setattr(module, "JiraClient", lambda _: MultiPageClient())
    outputs = module.list_tickets(
        module.ListTicketsParams(project_key="SEC", max_results=1500),
        SimpleNamespace(set_summary=lambda *_: None),
        asset,
    )
    assert len(outputs) == 1500
    assert sum(requested) >= 1500


def test_poll_rejects_explicit_zero_container_count(monkeypatch, asset):
    with pytest.raises(ActionFailure, match="container_count"):
        next(on_poll(OnPollParams(container_count=0), SimpleNamespace(), asset))


def test_issue_output_manifest_keeps_legacy_paths_and_types():
    specs = list(FieldsOutput._to_json_schema("action_result.data.*.fields"))
    paths = {spec["data_path"]: spec["data_type"] for spec in specs}
    assert paths["action_result.data.*.fields.labels"] == "string"
    assert paths["action_result.data.*.fields.assignee"] == "string"
    assert paths["action_result.data.*.fields.resolution"] == "string"
    assert paths["action_result.data.*.fields.timeestimate"] == "string"
