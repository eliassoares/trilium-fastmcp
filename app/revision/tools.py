from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client
from app.revision.schemas import Revision


@mcp.tool(
    name="get_revision",
    description="Returns a revision identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def get_revision(
    revision_id: Annotated[
        str,
        Field(
            description="The revision id to get it",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        )
    ]
) -> Revision:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/revisions/{revision_id}"
        )
        response.raise_for_status()
        return Revision.model_validate(response.json())


@mcp.tool(
    name="get_revision_content",
    description="Returns revision content identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def get_revision_content(
    revision_id: Annotated[
        str,
        Field(
            description="The revision id to get its content",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        )
    ]
) -> str:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/revisions/{revision_id}/content"
        )
        response.raise_for_status()
        return response.text
