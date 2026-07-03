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
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Params
from soar_sdk.views.view_parser import ViewContext

from .._app_ref import app
from .._asset import Asset


class ListProjectsOutput(ActionOutput):
    id: str = OutputField(example_values=["10207"])
    name: str = OutputField(example_values=["Access Uplift Alerts"])
    project_key: str = OutputField(
        cef_types=["jira project key"], example_values=["AUA"]
    )


class ListProjectsSummaryOutput(ActionOutput):
    total_projects: int = OutputField(example_values=[5])


@app.view_handler(template="jira_list_projects.html")
def _list_projects_view(
    context: ViewContext, results: list[ListProjectsOutput]
) -> dict:
    return {
        "results": [{"data": results, "param": getattr(context, "param", {})}],
    }


@app.action(
    description="List all projects",
    action_type="investigate",
    view_handler=_list_projects_view,
    summary_type=ListProjectsSummaryOutput,
)
def list_projects(
    params: Params, soar: SOARClient, asset: Asset
) -> list[ListProjectsOutput]:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import JIRA_ERROR_PROJECTS_INFO, JIRA_TOTAL_PROJECTS
    from ..helpers import jira_request

    logger = getLogger()

    try:
        projects = jira_request(asset, "GET", "rest/api/2/project")
    except ActionFailure as exc:
        raise ActionFailure(f"{JIRA_ERROR_PROJECTS_INFO}: {exc}") from exc

    if not projects:
        logger.info(f"{JIRA_TOTAL_PROJECTS}: 0")
        soar.set_summary(ListProjectsSummaryOutput(total_projects=0))
        return []

    results = [
        ListProjectsOutput(
            id=project.get("id", ""),
            name=project.get("name", ""),
            project_key=project.get("key", ""),
        )
        for project in projects
    ]

    logger.info(f"{JIRA_TOTAL_PROJECTS}: {len(results)}")
    soar.set_summary(ListProjectsSummaryOutput(total_projects=len(results)))
    return results
