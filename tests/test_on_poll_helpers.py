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
from types import SimpleNamespace

from src.actions.on_poll_helpers import _migrate_legacy_ingest_state


class FakeState(dict):
    def __init__(self, legacy_state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = SimpleNamespace(load_state=lambda: legacy_state)


def test_legacy_ingest_state_migrates_falsey_checkpoint_values():
    state = FakeState({"first_run": False, "last_time": 0})
    asset = SimpleNamespace(ingest_state=state)

    _migrate_legacy_ingest_state(asset)

    assert state == {"first_run": False, "last_time": 0}


def test_existing_sdk_ingest_state_wins_over_legacy_state():
    state = FakeState(
        {"first_run": True, "last_time": 99},
        first_run=False,
        last_time=42,
    )
    asset = SimpleNamespace(ingest_state=state)

    _migrate_legacy_ingest_state(asset)

    assert state == {"first_run": False, "last_time": 42}
