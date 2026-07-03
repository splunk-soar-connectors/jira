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
from soar_sdk.action_results import ActionOutput, OutputField


# Shared Output Classes


class AvatarurlsOutput(ActionOutput):
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


class AssigneeOutput(ActionOutput):
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


class AuthorOutput(ActionOutput):
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


class UpdateauthorOutput(ActionOutput):
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


class AttachmentauthorOutput(ActionOutput):
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


class AttachmentOutput(ActionOutput):
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


class VisibilityOutput(ActionOutput):
    type: str = OutputField(example_values=["group", "role"])
    value: str = OutputField(example_values=["jira-software-users"])


class CommentsOutput(ActionOutput):
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


class CommentOutput(ActionOutput):
    comments: list[CommentsOutput]
    maxResults: float = OutputField(example_values=[7])
    startAt: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[7])


class ComponentsOutput(ActionOutput):
    id: str = OutputField(example_values=["10104"])
    name: str = OutputField(example_values=["comp_test1"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/component/10104"],
    )


class CreatorOutput(ActionOutput):
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


class FixversionsOutput(ActionOutput):
    archived: bool
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["1.0"])
    released: bool
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/version/10000"],
    )


class IssuetypeOutput(ActionOutput):
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


class PriorityOutput(ActionOutput):
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


class AggregateprogressOutput(ActionOutput):
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class ProgressOutput(ActionOutput):
    progress: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class ProjectcategoryOutput(ActionOutput):
    description: str = OutputField(example_values=["test"])
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["QA-Team"])
    self: str = OutputField(
        example_values=[
            "https://testlab.atlassian.net/rest/api/2/projectCategory/10000"
        ]
    )


class ProjectOutput(ActionOutput):
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


class ReporterOutput(ActionOutput):
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


class ResolutionOutput(ActionOutput):
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


class StatuscategoryOutput(ActionOutput):
    colorName: str = OutputField(example_values=["green"])
    id: float = OutputField(example_values=[3])
    key: str = OutputField(example_values=["done"])
    name: str = OutputField(example_values=["Done"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/statuscategory/3"],
    )


class StatusOutput(ActionOutput):
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


class TypeOutput(ActionOutput):
    id: str = OutputField(example_values=["10000"])
    inward: str = OutputField(example_values=["is blocked by"])
    name: str = OutputField(example_values=["Blocks"])
    outward: str = OutputField(example_values=["blocks"])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issueLinkType/10000"],
    )


class VersionsOutput(ActionOutput):
    archived: bool
    id: str = OutputField(example_values=["10000"])
    name: str = OutputField(example_values=["1.0"])
    released: bool
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/version/10000"],
    )


class VotesOutput(ActionOutput):
    hasVoted: bool = OutputField(example_values=[False, True])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/MAN-1/votes"],
    )
    votes: float = OutputField(example_values=[0])


class WatchesOutput(ActionOutput):
    isWatching: bool = OutputField(example_values=[False, True])
    self: str = OutputField(
        cef_types=["url"],
        example_values=["http://jira.instance.ip/rest/api/2/issue/MAN-1/watchers"],
    )
    watchCount: float = OutputField(example_values=[1])


class WorklogOutput(ActionOutput):
    maxResults: float = OutputField(example_values=[20])
    startAt: float = OutputField(example_values=[0])
    total: float = OutputField(example_values=[0])


class TimetrackingOutput(ActionOutput):
    remainingEstimate: str = OutputField(example_values=["0m"])
    remainingEstimateSeconds: float = OutputField(example_values=[0])
    timeSpent: str = OutputField(example_values=["2d 4h"])
    timeSpentSeconds: float = OutputField(example_values=[72000])


class WorklogsOutput(ActionOutput):
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


class LinkedissuefieldsOutput(ActionOutput):
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
