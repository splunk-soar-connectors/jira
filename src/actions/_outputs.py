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
from pydantic import ValidationError

from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.logging import getLogger

_logger = getLogger()


class JiraPermissiveOutput(PermissiveActionOutput):
    """Permissive output whose ``__init__`` tolerates a ``self`` data key.

    The SDK's ``PermissiveActionOutput.__init__(self, **data)`` names its
    instance parameter ``self``. Nearly every Jira REST object carries a
    ``"self"`` key (its own API URL), so ``Model(**jira_obj)`` collides with
    ``TypeError: got multiple values for argument 'self'``. We make ``self``
    positional-only and route to ``ActionOutput.__init__`` (plain pydantic,
    which handles a ``self`` *field* fine) while keeping the permissive
    warn-instead-of-raise behavior and the raw-data passthrough.
    """

    def __init__(self, /, **data: object) -> None:
        try:
            ActionOutput.__init__(self, **data)
        except ValidationError as exc:
            _logger.warning(f"Ignoring validation error:\n {exc.with_traceback(None)}")
        self._permissive_raw = data


class AvatarurlsOutput(JiraPermissiveOutput):
    n16x16: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500"
        ],
        alias="16x16",
    )
    n24x24: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/useravatar?size=small&ownerId=admin&avatarId=10500"
        ],
        alias="24x24",
    )
    n32x32: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/useravatar?size=medium&ownerId=admin&avatarId=10500"
        ],
        alias="32x32",
    )
    n48x48: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/useravatar?ownerId=admin&avatarId=10500"
        ],
        alias="48x48",
    )


class AssigneeOutput(JiraPermissiveOutput):
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=[
            "5d2ef6ab52a8370c567f27bb"  # pragma: allowlist secret
        ],
    )
    accountType: str = OutputField(example_values=["atlassian"])
    active: bool = OutputField(example_values=[False, True])
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Name"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["abc@domain.com"]
    )
    key: str | None = OutputField(example_values=["test"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["test"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/useravatar?size=xsmall&ownerId=admin&avatarId=10500"
        ],
    )
    timeZone: str | None


class AuthorOutput(JiraPermissiveOutput):
    active: bool
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["notifications@domain.us"]
    )
    key: str | None = OutputField(example_values=["admin"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["admin"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=admin"],
    )
    timeZone: str | None = OutputField(example_values=["UTC"])


class UpdateauthorOutput(JiraPermissiveOutput):
    active: bool
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["notifications@domain.us"]
    )
    key: str | None = OutputField(example_values=["admin"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["admin"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=admin"],
    )
    timeZone: str | None = OutputField(example_values=["UTC"])


class AttachmentauthorOutput(JiraPermissiveOutput):
    accountId: str | None = OutputField(
        cef_types=["jira user account id"],
        example_values=["557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce"],
    )
    accountType: str | None = OutputField(example_values=["atlassian"])
    active: bool
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["notifications@domain.us"]
    )
    key: str | None = OutputField(example_values=["admin"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["admin"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=admin"],
    )
    timeZone: str | None = OutputField(example_values=["UTC"])


class AttachmentOutput(JiraPermissiveOutput):
    author: AttachmentauthorOutput
    content: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/attachment/10403/Add+Comment.png"
        ],
    )
    created: str = OutputField(example_values=["2018-09-19T18:15:01.060-0700"])
    filename: str = OutputField(example_values=["Add Comment.png"])
    id: str = OutputField(example_values=["10403"])
    mimeType: str = OutputField(example_values=["image/png"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/attachment/10403"],
    )
    size: float = OutputField(example_values=[97613])
    thumbnail: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/thumbnail/10403/_thumb_10403.png"
        ],
    )


class VisibilityOutput(JiraPermissiveOutput):
    type: str = OutputField(example_values=["group", "role"])
    value: str = OutputField(example_values=["jira-software-users"])


class CommentsOutput(JiraPermissiveOutput):
    author: AuthorOutput
    body: str = OutputField(
        example_values=["This is a sample testing body for the comment"]
    )
    created: str = OutputField(example_values=["2016-03-15T17:11:49.767-0700"])
    id: str = OutputField(example_values=["10004"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/10246/comment/10004"],
    )
    updateAuthor: UpdateauthorOutput
    updated: str = OutputField(example_values=["2016-03-15T17:11:49.767-0700"])
    visibility: VisibilityOutput | None


class CommentOutput(JiraPermissiveOutput):
    comments: list[CommentsOutput]
    maxResults: float = OutputField(example_values=[7])
    startAt: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[7])


class ComponentsOutput(JiraPermissiveOutput):
    id: str = OutputField(example_values=["10104"])
    name: str = OutputField(example_values=["comp_test1"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/component/10104"],
    )


class CreatorOutput(JiraPermissiveOutput):
    accountId: str = OutputField(
        cef_types=["jira user account id"],
        example_values=["557058:c4593bd2-4853-4a5e-a9ed-278ca5f17dce"],
    )
    accountType: str = OutputField(example_values=["atlassian"])
    active: bool = OutputField(example_values=[False, True])
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["notifications@domain.us"]
    )
    key: str | None = OutputField(example_values=["admin"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["admin"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=admin"],
    )
    timeZone: str | None = OutputField(example_values=["UTC"])


class FixversionsOutput(JiraPermissiveOutput):
    archived: bool
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["1.0"])
    released: bool
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/version/10000"],
    )


class IssuetypeOutput(JiraPermissiveOutput):
    avatarId: float = OutputField(example_values=[10303])
    description: str = OutputField(
        example_values=[
            "A problem which impairs or prevents the functions of the product"
        ]
    )
    iconUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "http://jira.instance.ip/secure/viewavatar?size=xsmall&avatarId=10303&avatarType=issuetype"
        ],
    )
    id: str = OutputField(example_values=["1"])
    name: str = OutputField(cef_types=["jira issue type"], example_values=["Defect"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issuetype/1"],
    )
    subtask: bool = OutputField(example_values=[False, True])


class PriorityOutput(JiraPermissiveOutput):
    iconUrl: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/images/icons/priorities/medium.svg"],
    )
    id: str = OutputField(example_values=["3"])
    name: str = OutputField(
        cef_types=["jira ticket priority"], example_values=["Medium"]
    )
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/priority/3"],
    )


class AggregateprogressOutput(JiraPermissiveOutput):
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class ProgressOutput(JiraPermissiveOutput):
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class ProjectcategoryOutput(JiraPermissiveOutput):
    description: str = OutputField(example_values=["test"])
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["QA-Team"])
    self: str = OutputField(
        example_values=[
            "https://testlab.atlassian.net/rest/api/2/projectCategory/10000"
        ]
    )


class ProjectOutput(JiraPermissiveOutput):
    avatarUrls: AvatarurlsOutput
    id: str = OutputField(example_values=["10100"])
    key: str = OutputField(cef_types=["jira project key"], example_values=["MAN"])
    name: str = OutputField(example_values=["TestProject"])
    projectCategory: ProjectcategoryOutput | None
    projectTypeKey: str = OutputField(example_values=["software"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/project/10100"],
    )
    simplified: bool = OutputField(example_values=[False, True])


class ReporterOutput(JiraPermissiveOutput):
    accountType: str = OutputField(example_values=["atlassian"])
    active: bool = OutputField(example_values=[False, True])
    avatarUrls: AvatarurlsOutput | None
    displayName: str = OutputField(
        cef_types=["jira user display name"], example_values=["Test Admin"]
    )
    emailAddress: str | None = OutputField(
        cef_types=["email"], example_values=["notifications@domain.us"]
    )
    key: str | None = OutputField(example_values=["admin"])
    name: str | None = OutputField(cef_types=["user name"], example_values=["admin"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/user?username=admin"],
    )
    timeZone: str | None = OutputField(example_values=["UTC"])


class ResolutionOutput(JiraPermissiveOutput):
    description: str = OutputField(
        example_values=["Work has been completed on this issue"]
    )
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(
        cef_types=["jira ticket resolution"], example_values=["Done"]
    )
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/resolution/10000"],
    )


class StatuscategoryOutput(JiraPermissiveOutput):
    colorName: str = OutputField(example_values=["green"])
    id: float = OutputField(example_values=[3])
    key: str = OutputField(example_values=["done"])
    name: str = OutputField(example_values=["Done"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/statuscategory/3"],
    )


class StatusOutput(JiraPermissiveOutput):
    description: str = OutputField(
        example_values=["This is a sample testing description"]
    )
    iconUrl: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/images/icons/statuses/closed.png"],
    )
    id: str = OutputField(example_values=["10001"])
    name: str = OutputField(example_values=["Done"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/status/10001"],
    )
    statusCategory: StatuscategoryOutput


class TypeOutput(JiraPermissiveOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"],
    )


class VersionsOutput(JiraPermissiveOutput):
    archived: bool
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["1.0"])
    released: bool
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/version/10000"],
    )


class VotesOutput(JiraPermissiveOutput):
    hasVoted: bool = OutputField(example_values=[False, True])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/MAN-1/votes"],
    )
    votes: float = OutputField(example_values=[0])


class WatchesOutput(JiraPermissiveOutput):
    isWatching: bool = OutputField(example_values=[False, True])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers"],
    )
    watchCount: float = OutputField(example_values=[1])


class WorklogOutput(JiraPermissiveOutput):
    maxResults: float = OutputField(example_values=[20])
    startAt: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class TimetrackingOutput(JiraPermissiveOutput):
    remainingEstimate: str = OutputField(example_values=["0m"])
    remainingEstimateSeconds: float = OutputField(example_values=[0])
    timeSpent: str = OutputField(example_values=["2d 4h"])
    timeSpentSeconds: float = OutputField(example_values=[72000])


class WorklogsOutput(JiraPermissiveOutput):
    author: AuthorOutput | None
    comment: str | None
    created: str | None = OutputField(example_values=["2021-12-06T06:35:45.703+0000"])
    id: str | None = OutputField(example_values=["10200"])
    issueId: str | None = OutputField(example_values=["27216"])
    self: str | None = OutputField(
        example_values=["http://jira.instance.ip/rest/api/2/issue/27216/worklog/10200"]
    )
    started: str | None = OutputField(example_values=["2021-12-06T06:35:00.000+0000"])
    timeSpent: str | None = OutputField(example_values=["4h"])
    timeSpentSeconds: float | None = OutputField(example_values=[14400])
    updateAuthor: UpdateauthorOutput | None
    updated: str | None = OutputField(example_values=["2021-12-06T06:35:45.703+0000"])


class LinkedissuefieldsOutput(JiraPermissiveOutput):
    """Nested `fields` object on linked issues (inwardIssue / outwardIssue /
    parent / subtasks). Legacy exposes issuetype, priority, status and summary."""

    issuetype: IssuetypeOutput | None
    priority: PriorityOutput | None
    status: StatusOutput | None
    summary: str | None = OutputField(example_values=["Sample summary"])


__all__ = [
    "AggregateprogressOutput",
    "AssigneeOutput",
    "AttachmentOutput",
    "AttachmentauthorOutput",
    "AuthorOutput",
    "AvatarurlsOutput",
    "CommentOutput",
    "CommentsOutput",
    "ComponentsOutput",
    "CreatorOutput",
    "FixversionsOutput",
    "IssuetypeOutput",
    "JiraPermissiveOutput",
    "LinkedissuefieldsOutput",
    "PriorityOutput",
    "ProgressOutput",
    "ProjectOutput",
    "ProjectcategoryOutput",
    "ReporterOutput",
    "ResolutionOutput",
    "StatusOutput",
    "StatuscategoryOutput",
    "TimetrackingOutput",
    "TypeOutput",
    "UpdateauthorOutput",
    "VersionsOutput",
    "VisibilityOutput",
    "VotesOutput",
    "WatchesOutput",
    "WorklogOutput",
    "WorklogsOutput",
]
