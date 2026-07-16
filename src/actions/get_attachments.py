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
import os
from pathlib import Path

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Param, Params

from .._asset import Asset


class GetAttachmentsParams(Params):
    id: str = Param(
        description="The key of the Jira issue",
        primary=True,
        cef_types=["jira ticket key"],
    )
    retrieve_all: bool | None = Param(
        description="If this is set to true all attachments will be retrieved from the issue (if the value is not provided, it will internally be treated as 'false')",
        default=False,
    )
    container_id: str = Param(description="The Container ID to associate the file with")
    extension_filter: str | None = Param(
        description="Comma-separated list of file extensions to be returned from the issue"
    )


class GetAttachmentsOutput(ActionOutput):
    vault_id: str = OutputField(
        cef_types=["vault id"],
        example_values=[
            "9c03244555e41685dc5f03ec7d9de1c6db26c318"  # pragma: allowlist secret
        ],
        column_name="Vault ID",
    )
    id: float = OutputField(example_values=[501], column_name="Attachment ID")
    size: float = OutputField(example_values=[231003], column_name="Size (bytes)")
    message: str = OutputField(example_values=["success"], column_name="Message")
    succeeded: bool = OutputField(column_name="Status")
    container: float = OutputField(example_values=[2446])
    hash: str = OutputField(
        cef_types=["md5"],
        example_values=[
            "9c03244555e41685dc5f03ec7d9de1c6db26c318"  # pragma: allowlist secret
        ],
    )


def _is_safe_path(basedir, path):
    return basedir == os.path.commonpath((basedir, os.path.realpath(path)))


def get_attachments(
    params: GetAttachmentsParams, soar: SOARClient, asset: Asset
) -> list[GetAttachmentsOutput]:
    import httpx

    from soar_sdk.exceptions import ActionFailure
    from soar_sdk.logging import getLogger

    from ..consts import JIRA_ERROR_INVALID_FILE_PATH
    from ..helpers import get_auth, jira_request

    logger = getLogger()

    retrieve_all = params.retrieve_all if params.retrieve_all is not None else False
    extension_filter = params.extension_filter or ""

    if not retrieve_all and not extension_filter.strip():
        raise ActionFailure(
            "Please select retrieve all or pass in a list of extensions"
        )

    allowed_extensions: list[str] = []
    if extension_filter.strip():
        allowed_extensions = [
            f".{ext.strip().lstrip('.')}"
            for ext in extension_filter.split(",")
            if ext.strip()
        ]

    ticket_key = params.id
    issue = jira_request(
        asset, "GET", f"rest/api/2/issue/{ticket_key}?fields=attachment"
    )

    attachments = (issue.get("fields") or {}).get("attachment") or []

    if not attachments:
        logger.info(f"No attachments found on issue {ticket_key}")
        return [
            GetAttachmentsOutput(
                container=float(params.container_id),
                hash="",
                id=0.0,
                message="This issue has no attachments",
                size=0.0,
                succeeded=True,
                vault_id="",
            )
        ]

    vault_tmp_dir = soar.vault.get_vault_tmp_dir()
    auth = get_auth(asset)
    verify = bool(asset.verify_server_cert)

    results: list[GetAttachmentsOutput] = []

    for attachment in attachments:
        filename = attachment.get("filename", "")
        content_url = attachment.get("content", "")
        attachment_id = float(attachment.get("id", 0))
        attachment_size = float(attachment.get("size", 0))

        filename = "".join(filename.split())

        if not filename:
            logger.warning("Skipping attachment with empty filename")
            continue

        if allowed_extensions:
            ext = Path(filename).suffix
            if ext.lower() not in [e.lower() for e in allowed_extensions]:
                logger.info(f"Skipping {filename}: extension not in filter")
                continue

        full_path = str(Path(vault_tmp_dir) / filename)
        if not _is_safe_path(vault_tmp_dir, full_path):
            logger.error(f"{JIRA_ERROR_INVALID_FILE_PATH}: {filename}")
            continue

        try:
            with httpx.Client(verify=verify, follow_redirects=True) as client:
                resp = client.get(
                    content_url, auth=auth, timeout=60.0, headers={"Accept": "*/*"}
                )
            if not resp.is_success:
                raise ActionFailure(
                    f"Failed to download attachment: {resp.status_code}"
                )
            content = resp.content
        except ActionFailure:
            raise
        except Exception as exc:
            raise ActionFailure(
                f"Failed to download attachment '{filename}': {exc}"
            ) from exc

        with open(full_path, "wb") as f:
            f.write(content)

        vault_id = soar.vault.add_attachment(
            container_id=int(params.container_id),
            file_location=full_path,
            file_name=filename,
        )

        results.append(
            GetAttachmentsOutput(
                container=float(params.container_id),
                hash=vault_id,
                id=attachment_id,
                message="success",
                size=attachment_size,
                succeeded=True,
                vault_id=vault_id,
            )
        )

    soar.set_message(f"Successfully retrieved {len(results)} attachment(s)")
    return results
