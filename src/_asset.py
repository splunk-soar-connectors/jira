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
from zoneinfo import ZoneInfo

from soar_sdk.asset import AssetField, BaseAsset


class Asset(BaseAsset):
    device_url: str = AssetField(
        description="Device URL including the port, e.g. https://myjira.enterprise.com:8080"
    )
    verify_server_cert: bool | None = AssetField(
        description="Verify server certificate", default=False
    )
    client_id: str | None = AssetField(
        description="OAuth 2.0 client ID for a service account. Takes priority over username/password."
    )
    client_secret: str | None = AssetField(
        description="OAuth 2.0 client secret, used with client_id.",
        sensitive=True,
    )
    username: str | None = AssetField(
        description="Jira email or on-prem username for Basic Auth. Not needed if using OAuth."
    )
    password: str | None = AssetField(
        description="Jira API token or on-prem password for Basic Auth. Not needed if using OAuth.",
        sensitive=True,
    )
    project_key: str | None = AssetField(
        description="Project key to ingest tickets (issues) from"
    )
    query: str | None = AssetField(
        description="Additional parameters to query for during ingestion in JQL"
    )
    first_run_max_tickets: float | None = AssetField(
        description="Maximum tickets (issues) to poll first time", default=1000.0
    )
    max_tickets: float | None = AssetField(
        description="Maximum tickets (issues) for scheduled polling", default=100.0
    )
    custom_fields: str | None = AssetField(
        description="JSON formatted list of names of custom fields (case-sensitive) to be ingested"
    )
    timezone: ZoneInfo | None = AssetField(
        description="Jira instance timezone (IANA, e.g. 'America/New_York'). Leave blank to auto-detect.",
        default=None,
    )
