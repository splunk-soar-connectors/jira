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
from soar_sdk.action_results import ActionOutput
from soar_sdk.params import Param, Params

from .._app_ref import app
from .._asset import Asset


class DeleteTicketParams(Params):
    id: str = Param(description="Issue ID", primary=True, cef_types=["jira ticket key"])


@app.action(description="Delete ticket (issue)", action_type="generic", read_only=False)
def delete_ticket(
    params: DeleteTicketParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import JIRA_SUCCESS_TICKET_DELETED
    from ..helpers import jira_request

    logger = getLogger()

    try:
        jira_request(asset, "GET", f"rest/api/2/issue/{params.id}")
    except ActionFailure as exc:
        raise ActionFailure(
            f"Unable to find ticket info. Please make sure the issue exists: {exc}"
        ) from exc

    jira_request(asset, "DELETE", f"rest/api/2/issue/{params.id}")

    logger.info(JIRA_SUCCESS_TICKET_DELETED)
    soar.set_message(JIRA_SUCCESS_TICKET_DELETED)
    return ActionOutput()
