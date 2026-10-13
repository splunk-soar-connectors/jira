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
"""Action-layer tests for the Jira REST connector."""

import importlib

import pytest

from src._asset import Asset

add_comment_module = importlib.import_module("src.actions.add_comment")
create_ticket_module = importlib.import_module("src.actions.create_ticket")
get_attachments_module = importlib.import_module("src.actions.get_attachments")
get_ticket_module = importlib.import_module("src.actions.get_ticket")
list_projects_module = importlib.import_module("src.actions.list_projects")
list_tickets_module = importlib.import_module("src.actions.list_tickets")
search_users_module = importlib.import_module("src.actions.search_users")
update_ticket_module = importlib.import_module("src.actions.update_ticket")


class FakeSOAR:
    def __init__(self):
        self.message = None
        self.summary = None

    def set_message(self, message):
        self.message = message

    def set_summary(self, summary):
        self.summary = summary


class FakeJiraClient:
    def __init__(self):
        self.comment_calls = []
        self.issue_calls = []
        self.search_calls = []

    def issue(self, issue_id, *args, **kwargs):
        self.issue_calls.append(issue_id)
        return {
            "id": "10001",
            "key": issue_id,
            "fields": {
                "summary": "Investigate alert",
                "description": "Ticket body",
                "project": {"key": "SEC"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "High"},
                "reporter": {"displayName": "Analyst"},
                "status": {"name": "Open"},
                "resolution": None,
            },
        }

    def add_comment(self, issue_id, comment, *, internal):
        self.comment_calls.append((issue_id, comment, internal))

    def projects(self):
        return [
            {"id": "1", "key": "SEC", "name": "Security"},
            {"id": "2", "key": "OPS", "name": "Operations"},
        ]

    def search_issues(self, jql, **kwargs):
        self.search_calls.append((jql, kwargs))
        return {
            "issues": [
                {
                    "id": "10001",
                    "key": "SEC-1",
                    "fields": {
                        "summary": "Investigate alert",
                        "description": "Ticket body",
                        "project": {"key": "SEC"},
                        "issuetype": {"name": "Task"},
                        "priority": {"name": "High"},
                        "reporter": {"displayName": "Analyst"},
                        "status": {"name": "Open"},
                        "resolution": None,
                    },
                }
            ]
        }

    def search_users(self, **kwargs):
        return [
            {
                "accountId": "abc123",
                "accountType": "atlassian",
                "active": True,
                "avatarUrls": {},
                "displayName": "Jane Analyst",
                "emailAddress": "jane@example.com",
                "key": "jane",
                "locale": "en_US",
                "name": "jane",
                "self": "https://jira.example/rest/api/2/user?username=jane",
                "timeZone": "UTC",
            }
        ]


@pytest.fixture
def asset():
    return Asset(
        device_url="https://jira.example", username="user", password="token"
    )  # pragma: allowlist secret


def test_get_ticket_uses_centralized_client(monkeypatch, asset):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(get_ticket_module, "JiraClient", lambda _: fake_client)
    monkeypatch.setattr(get_ticket_module, "get_custom_field_map", lambda *_: {})

    output = get_ticket_module.get_ticket(
        get_ticket_module.GetTicketParams(id="SEC-1"), FakeSOAR(), asset
    )

    assert output.id == "10001"
    assert output.name == "SEC-1"
    assert output.summary == "Investigate alert"
    assert output.resolution == "Unresolved"
    assert output.fields.summary == "Investigate alert"


def test_get_ticket_forwards_numeric_jira_issue_id(monkeypatch, asset):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(get_ticket_module, "JiraClient", lambda _: fake_client)
    monkeypatch.setattr(get_ticket_module, "get_custom_field_map", lambda *_: {})

    output = get_ticket_module.get_ticket(
        get_ticket_module.GetTicketParams(id="10001"), FakeSOAR(), asset
    )

    assert output.id == "10001"
    assert output.name == "10001"
    assert fake_client.issue_calls == ["10001"]


def test_legacy_boolean_defaults_are_preserved(monkeypatch, asset):
    comment_client = FakeJiraClient()
    monkeypatch.setattr(add_comment_module, "JiraClient", lambda _: comment_client)
    add_comment_module.add_comment(
        add_comment_module.AddCommentParams(id="SEC-1", comment="Note"),
        FakeSOAR(),
        asset,
    )
    assert comment_client.comment_calls == [("SEC-1", "Note", True)]

    attachments_client = FakeJiraClient()
    monkeypatch.setattr(
        get_attachments_module, "JiraClient", lambda _: attachments_client
    )
    outputs = get_attachments_module.get_attachments(
        get_attachments_module.GetAttachmentsParams(id="SEC-1", container_id="1"),
        FakeSOAR(),
        asset,
    )
    assert outputs == []


@pytest.mark.parametrize("fields", ["[]", '"not an object"'])
def test_create_ticket_rejects_non_object_fields(fields, asset):
    params = create_ticket_module.CreateTicketParams(
        project_key="SEC", summary="Investigate alert", issue_type="Task", fields=fields
    )

    with pytest.raises(
        create_ticket_module.ActionFailure, match="JSON formatted dictionary"
    ):
        create_ticket_module.create_ticket(params, FakeSOAR(), asset)


@pytest.mark.parametrize("update_fields", ["[]", '"not an object"', "{}"])
def test_update_ticket_rejects_invalid_or_empty_json_object(
    monkeypatch, update_fields, asset
):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(update_ticket_module, "JiraClient", lambda _: fake_client)
    params = update_ticket_module.UpdateTicketParams(
        id="SEC-1", update_fields=update_fields
    )

    with pytest.raises(update_ticket_module.ActionFailure):
        update_ticket_module.update_ticket(params, FakeSOAR(), asset)


def test_list_projects_uses_centralized_client(monkeypatch, asset):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(list_projects_module, "JiraClient", lambda _: fake_client)
    soar = FakeSOAR()

    outputs = list_projects_module.list_projects(None, soar, asset)

    assert [output.project_key for output in outputs] == ["SEC", "OPS"]
    assert soar.summary.total_projects == 2


def test_list_tickets_uses_centralized_rest_client_search(monkeypatch, asset):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(list_tickets_module, "JiraClient", lambda _: fake_client)
    monkeypatch.setattr(list_tickets_module, "get_custom_field_map", lambda *_: {})
    soar = FakeSOAR()

    outputs = list_tickets_module.list_tickets(
        list_tickets_module.ListTicketsParams(
            project_key="SEC", query=None, start_index=0, max_results=1
        ),
        soar,
        asset,
    )

    assert outputs[0].name == "SEC-1"
    assert fake_client.search_calls[0][0] == "project=SEC"
    assert fake_client.search_calls[0][1]["fields"] == "*all"
    assert soar.summary.total_issues == 1


def test_ticket_descriptions_are_not_classified_as_urls():
    fields_description = list_tickets_module.FieldsOutput.model_fields["description"]
    ticket_description = list_tickets_module.ListTicketsOutput.model_fields[
        "description"
    ]

    assert "cef_types" not in (fields_description.json_schema_extra or {})
    assert "cef_types" not in (ticket_description.json_schema_extra or {})


def test_list_tickets_uses_cloud_cursor_and_preserves_start_index(monkeypatch, asset):
    class FakeCloudJiraClient(FakeJiraClient):
        def search_issues(self, jql, **kwargs):
            self.search_calls.append((jql, kwargs))
            token = kwargs.get("next_page_token")
            pages = {
                None: {
                    "issues": [_issue("SEC-1"), _issue("SEC-2")],
                    "nextPageToken": "page-2",
                    "isLast": False,
                },
                "page-2": {
                    "issues": [_issue("SEC-3"), _issue("SEC-4")],
                    "nextPageToken": "page-3",
                    "isLast": False,
                },
                "page-3": {
                    "issues": [_issue("SEC-5")],
                    "isLast": True,
                },
            }
            return pages[token]

    fake_client = FakeCloudJiraClient()
    monkeypatch.setattr(list_tickets_module, "JiraClient", lambda _: fake_client)
    monkeypatch.setattr(list_tickets_module, "get_custom_field_map", lambda *_: {})

    outputs = list_tickets_module.list_tickets(
        list_tickets_module.ListTicketsParams(
            project_key="SEC", query=None, start_index=3, max_results=2
        ),
        FakeSOAR(),
        asset,
    )

    assert [output.name for output in outputs] == ["SEC-4", "SEC-5"]
    assert [call[1]["next_page_token"] for call in fake_client.search_calls] == [
        None,
        "page-2",
        "page-3",
    ]


def _issue(key):
    return {
        "id": key.removeprefix("SEC-"),
        "key": key,
        "fields": {
            "summary": key,
            "description": None,
            "project": {"key": "SEC"},
            "issuetype": {"name": "Task"},
            "priority": {"name": "Medium"},
            "reporter": {"displayName": "Analyst"},
            "status": {"name": "Open"},
            "resolution": None,
        },
    }


def test_lookup_users_uses_centralized_client(monkeypatch, asset):
    fake_client = FakeJiraClient()
    monkeypatch.setattr(search_users_module, "JiraClient", lambda _: fake_client)
    soar = FakeSOAR()

    outputs = search_users_module.lookup_users(
        search_users_module.LookupUsersParams(
            username="jane", display_name=None, max_results=1
        ),
        soar,
        asset,
    )

    assert outputs[0].name == "jane"
    assert outputs[0].accountId == "abc123"
    assert soar.summary.total_users == 1
