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
from soar_sdk.app import App

from ._asset import Asset
from .actions import register_actions
from .actions.test_connectivity import run_test_connectivity


def create_jira_app() -> App:
    """Build and fully configure the Jira SOAR app.

    Creates the App instance, wires the test_connectivity handler via its
    dedicated decorator (delegating to the plain run_test_connectivity
    function), and registers every other action through register_actions.
    """
    app = App(
        name="Jira",
        app_type="ticketing",
        logo="logo_atlassian.svg",
        logo_dark="logo_atlassian_dark.svg",
        product_vendor="Atlassian",
        product_name="Jira",
        publisher="Splunk",
        appid="1e1618e7-2f70-4fc0-916a-f96facc2d2e1",
        fips_compliant=True,
        asset_cls=Asset,
    )

    @app.test_connectivity()
    def test_connectivity(soar: SOARClient, asset: Asset) -> None:
        run_test_connectivity(soar, asset)

    return register_actions(app)


app: App = create_jira_app()


if __name__ == "__main__":
    app.cli()
