from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.attachment.schemas import Attachment, CreateAttachment, UpdateAttachment
from app.client import get_client

_TEXT_ATTACHMENT_MIME_EXACT = {
    "application/javascript",
    "application/json",
    "application/xml",
    "image/svg+xml",
}


def _is_text_like_attachment(mime: str) -> bool:
    normalized = mime.strip().lower()
    return normalized.startswith("text/") or normalized in _TEXT_ATTACHMENT_MIME_EXACT


@mcp.tool(
    name="create_attachment",
    description=(
        "Create a text-like attachment. "
        "Binary attachments are not supported by this tool."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_attachment(
    owner_id: Annotated[
        str,
        Field(
            ...,
            description="ID of the owning entity — either a noteId or a revisionId",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    role: Annotated[
        str,
        Field(
            ...,
            description=(
                "Purpose of the attachment within its owner. "
                "Known values: 'image' (embedded image in a text note), "
                "'file' (generic file attachment)."
            ),
            examples=["image", "file"],
        ),
    ],
    mime: Annotated[
        str,
        Field(
            ...,
            description="MIME type of the attachment content",
            examples=["image/png", "application/pdf", "text/javascript"],
        ),
    ],
    title: Annotated[
        str,
        Field(
            ...,
            description="Display name of the attachment",
            examples=["screenshot.png", "report.pdf"],
        ),
    ],
    content: Annotated[
        str,
        Field(
            ...,
            description=(
                "Attachment content for text-like attachments. "
                "Binary attachment content is not supported by this tool."
            ),
        ),
    ],
    position: Annotated[
        int | None,
        Field(
            description=(
                "Ordering hint when a note has multiple attachments. "
                "Lower values sort first."
            ),
            examples=[10],
        ),
    ] = None,
) -> Attachment:
    if not _is_text_like_attachment(mime):
        raise ValueError(
            "create_attachment only supports text-like attachments. "
            "Use a text/*, application/json, application/javascript, "
            "application/xml, or image/svg+xml MIME type."
        )

    async with get_client() as client:
        response = await client.post(
            "/etapi/attachments",
            json=CreateAttachment(
                owner_id=owner_id,
                role=role,
                mime=mime,
                title=title,
                content=content,
                position=position,
            ).model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()
        return Attachment.model_validate(response.json())


@mcp.tool(
    name="update_attachment_metadata",
    description=(
        "Patch an attachment identified by the attachmentId with changes in the body. "
        "Only role, mime, title, and position are patchable"
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
)
async def update_attachment_metadata(
    attachment_id: Annotated[
        str,
        Field(
            ...,
            description="An attachment id to retrieve the attachment",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    role: Annotated[
        str | None,
        Field(
            description=(
                "Purpose of the attachment within its owner. "
                "Known values: 'image' (embedded image in a text note), "
                "'file' (generic file attachment)."
            ),
            examples=["image", "file"],
        ),
    ] = None,
    mime: Annotated[
        str | None,
        Field(
            description="MIME type of the attachment content",
            examples=["image/png", "application/pdf", "text/javascript"],
        ),
    ] = None,
    title: Annotated[
        str | None,
        Field(
            description="Display name of the attachment",
            examples=["screenshot.png", "report.pdf"],
        ),
    ] = None,
    position: Annotated[
        int | None,
        Field(
            description=(
                "Ordering hint when a note has multiple attachments. "
                "Lower values sort first."
            ),
            examples=[10],
        ),
    ] = None,
) -> Attachment:
    if all(value is None for value in (role, mime, title, position)):
        raise ValueError(
            "update_attachment_metadata requires at least one field to update."
        )

    async with get_client() as client:
        response = await client.patch(
            f"/etapi/attachments/{attachment_id}",
            json=UpdateAttachment(
                role=role, mime=mime, title=title, position=position
            ).model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()

        return Attachment.model_validate(response.json())


@mcp.tool(
    name="update_attachment_content",
    description="Updates attachment content identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
)
async def update_attachment_content(
    attachment_id: Annotated[
        str,
        Field(
            ...,
            description="An attachment id to retrieve the attachment",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    attachment_content: Annotated[
        str,
        Field(
            ...,
            description="The attachment content",
            examples=["{'data': 8888}"],
        ),
    ],
) -> None:
    async with get_client() as client:
        response = await client.put(
            f"/etapi/attachments/{attachment_id}/content",
            content=attachment_content.encode(),
            headers={"content-type": "text/plain"},
        )
        response.raise_for_status()


@mcp.tool(
    name="get_attachment",
    description="Returns an attachment identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_attachment(
    attachment_id: Annotated[
        str,
        Field(
            ...,
            description="An attachment id to retrieve the attachment",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> Attachment:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/attachments/{attachment_id}",
        )
        response.raise_for_status()

        return Attachment.model_validate(response.json())


@mcp.tool(
    name="get_attachment_content",
    description="Returns attachment content identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_attachment_content(
    attachment_id: Annotated[
        str,
        Field(
            ...,
            description="An attachment id to retrieve the attachment",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> bytes:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/attachments/{attachment_id}/content",
        )
        response.raise_for_status()

        return response.content
