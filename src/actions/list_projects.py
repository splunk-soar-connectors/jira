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
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.params import Params

from .._asset import Asset
from ..consts import JIRA_ERROR_PROJECTS_INFO, JIRA_TOTAL_PROJECTS
from ..helpers import jira_request


class ListProjectsOutput(ActionOutput):
    project_key: str = OutputField(
        cef_types=["jira project key"],
        example_values=["AUA"],
        column_name="Project Key",
    )
    name: str = OutputField(example_values=["Access Uplift Alerts"], column_name="Name")
    id: str = OutputField(example_values=["10207"], column_name="ID")


class ListProjectsSummaryOutput(ActionOutput):
    total_projects: int = OutputField(example_values=[5])


def list_projects(
    params: Params, soar: SOARClient, asset: Asset
) -> list[ListProjectsOutput]:
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
