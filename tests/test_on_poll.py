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
"""Poll failure-handling tests."""

import importlib
from types import SimpleNamespace

import pytest

from soar_sdk.exceptions import ActionFailure
from soar_sdk.models.artifact import Artifact
from soar_sdk.params import OnPollParams

on_poll_module = importlib.import_module("src.actions.on_poll")


class _Response:
    is_success = True

    def __init__(self, data):
        self._data = data

    def json(self):
        return {"data": self._data}


class _SOAR:
    def __init__(self):
        self.vault = SimpleNamespace(create_attachment=self._fail_vault_upload)

    def get_asset_id(self):
        return "1"

    def get(self, endpoint, **_kwargs):
        if endpoint == "rest/container":
            return _Response([{"id": 10}])
        return _Response([])

    def post(self, *_args, **_kwargs):
        return _Response([])

    @staticmethod
    def _fail_vault_upload(**_kwargs):
        raise RuntimeError("vault unavailable")


def test_attachment_upload_failure_fails_poll(monkeypatch):
    issue = {
        "key": "SEC-1",
        "fields": {
            "updated": "2026-09-20T10:00:00+0000",
            "attachment": [
                {
                    "id": "10001",
                    "filename": "evidence.txt",
                    "content": "https://jira.example/secure/attachment/10001",
                }
            ],
        },
    }
    asset = SimpleNamespace(
        ingest_state={},
        custom_fields=None,
        first_run_max_tickets=1,
        max_tickets=1,
    )

    monkeypatch.setattr(on_poll_module, "_migrate_legacy_ingest_state", lambda _: None)
    monkeypatch.setattr(on_poll_module, "_build_jql", lambda *_args, **_kwargs: "")
    monkeypatch.setattr(on_poll_module, "_paginate_issues", lambda *_: [issue])
    monkeypatch.setattr(
        on_poll_module, "_build_fields_artifact", lambda *_: Artifact(name="fields")
    )
    monkeypatch.setattr(
        on_poll_module,
        "JiraClient",
        lambda _: SimpleNamespace(download=lambda *_args, **_kwargs: b"contents"),
    )

    with pytest.raises(ActionFailure, match=on_poll_module.JIRA_ERROR_FAILED):
        list(on_poll_module.on_poll(OnPollParams(container_count=1), _SOAR(), asset))


def test_comment_artifact_build_failure_fails_poll(monkeypatch):
    issue = {
        "key": "SEC-1",
        "fields": {
            "updated": "2026-09-20T10:00:00+0000",
            "comment": {"comments": [{"id": "20001"}], "total": 2},
        },
    }
    asset = SimpleNamespace(
        ingest_state={},
        custom_fields=None,
        first_run_max_tickets=1,
        max_tickets=1,
    )

    monkeypatch.setattr(on_poll_module, "_migrate_legacy_ingest_state", lambda _: None)
    monkeypatch.setattr(on_poll_module, "_build_jql", lambda *_args, **_kwargs: "")
    monkeypatch.setattr(on_poll_module, "_paginate_issues", lambda *_: [issue])
    monkeypatch.setattr(
        on_poll_module,
        "_build_comment_artifact",
        lambda *_: (_ for _ in ()).throw(RuntimeError("invalid Jira comment")),
    )
    monkeypatch.setattr(
        on_poll_module, "_build_fields_artifact", lambda *_: Artifact(name="fields")
    )
    monkeypatch.setattr(
        on_poll_module,
        "JiraClient",
        lambda _: SimpleNamespace(download=lambda *_args, **_kwargs: b"contents"),
    )

    with pytest.raises(ActionFailure, match=on_poll_module.JIRA_ERROR_FAILED):
        list(on_poll_module.on_poll(OnPollParams(container_count=1), _SOAR(), asset))
