import logging
from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.attributes.schemas import CreateAttributeParams, UpdateAttributeParams
from app.client import get_client
from app.note.schemas import Attribute, AttributeType

logger = logging.getLogger(__name__)


@mcp.tool(
    name="get_attribute",
    description="Returns an attribute identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
    output_schema=Attribute.model_json_schema(),
)
async def get_attribute(
    attribute_id: Annotated[
        str,
        Field(
            description="The attribute ID to retrieve",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> Attribute:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/attributes/{attribute_id}",
        )
        response.raise_for_status()
        return Attribute.model_validate(response.json())


@mcp.tool(
    name="create_attribute",
    description=(
        "Create an attribute (label or relation) for a note. "
        "Labels are key-value pairs, relations link to other notes."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
    output_schema=Attribute.model_json_schema(),
)
async def create_attribute(
    note_id: Annotated[
        str,
        Field(
            description="ID of the note to attach the attribute to",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    type: Annotated[
        AttributeType,
        Field(
            description=(
                "Attribute type: 'label' for key-value pairs, "
                "'relation' for links to other notes"
            ),
            examples=["label"],
        ),
    ],
    name: Annotated[
        str,
        Field(
            description="Attribute name",
            examples=["pageUrl", "iconClass", "shareCss"],
        ),
    ],
    value: Annotated[
        str,
        Field(
            description=(
                "Value of the label, or ID of the related note for relations. "
                "Can be empty for flag-like labels."
            ),
            examples=["https://example.com"],
        ),
    ] = "",
    is_inheritable: Annotated[
        bool,
        Field(description="Whether child notes inherit this attribute"),
    ] = False,
    attribute_id: Annotated[
        str | None,
        Field(
            description=(
                "Attribute ID. DON'T specify unless you "
                "want to force a specific attributeId"
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ] = None,
) -> Attribute:
    params = CreateAttributeParams(
        note_id=note_id,
        type=type,
        name=name,
        value=value,
        is_inheritable=is_inheritable,
        attribute_id=attribute_id,
    )
    async with get_client() as client:
        response = await client.post(
            "/etapi/attributes",
            json=params.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()
        return Attribute.model_validate(response.json())


@mcp.tool(
    name="update_attribute",
    description="Update an attribute identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
    output_schema=Attribute.model_json_schema(),
)
async def update_attribute(
    attribute_id: Annotated[
        str,
        Field(
            description="The attribute ID to update",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    note_id: Annotated[
        str | None,
        Field(
            description="ID of the note this attribute belongs to",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ] = None,
    type: Annotated[
        AttributeType | None,
        Field(
            description="Attribute type: 'label' or 'relation'",
            examples=["label"],
        ),
    ] = None,
    name: Annotated[
        str | None,
        Field(
            description="Attribute name",
            examples=["pageUrl"],
        ),
    ] = None,
    value: Annotated[
        str | None,
        Field(
            description="Attribute value",
            examples=["https://example.com"],
        ),
    ] = None,
    is_inheritable: Annotated[
        bool | None,
        Field(description="Whether child notes inherit this attribute"),
    ] = None,
) -> Attribute:
    params = UpdateAttributeParams(
        note_id=note_id,
        type=type,
        name=name,
        value=value,
        is_inheritable=is_inheritable,
    )
    async with get_client() as client:
        response = await client.patch(
            f"/etapi/attributes/{attribute_id}",
            json=params.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()
        return Attribute.model_validate(response.json())


@mcp.tool(
    name="delete_attribute",
    description="Delete an attribute identified by its ID",
    annotations=ToolAnnotations(destructiveHint=True),
    tags={"delete"},
)
async def delete_attribute(
    attribute_id: Annotated[
        str,
        Field(
            description="The attribute ID to delete",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> str:
    async with get_client() as client:
        response = await client.delete(
            f"/etapi/attributes/{attribute_id}",
        )
        response.raise_for_status()
    return "Attribute deleted successfully"
