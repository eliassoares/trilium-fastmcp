from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.branch.schemas import Branch
from app.client import get_client


@mcp.tool(
    name="get_branch",
    description="Returns a branch identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_branch(
    branch_id: Annotated[
        str,
        Field(
            description="The branch id to retrieve the branch",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> Branch:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/branches/{branch_id}",
        )
        response.raise_for_status()

        return Branch.model_validate(response.json())


@mcp.tool(
    name="create_branch",
    description=(
        "Create a branch (clone a note to a different location in the tree). "
        "In case there is a branch between parent note and child note already, "
        "then this will update the existing branch with prefix, "
        "notePosition and isExpanded."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_branch(
    note_id: Annotated[
        str,
        Field(
            ...,
            description="Identifies the note",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    parent_note_id: Annotated[
        str,
        Field(
            ...,
            description="Identifies the parent note",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    prefix: Annotated[
        str | None,
        Field(
            description="Location-specific prefix shown before the note title",
            examples=["Archive", None],
        ),
    ] = None,
    note_position: Annotated[
        int | None,
        Field(
            description=(
                "Position of the note in the parent. Normal ordering is 10, 20, 30"
            ),
            examples=[10],
        ),
    ] = None,
    is_expanded: Annotated[
        bool | None,
        Field(
            description="Whether this note appears expanded as a folder in the tree",
            examples=[False],
        ),
    ] = None,
) -> Branch:
    payload: dict[str, object | None] = {
        "noteId": note_id,
        "parentNoteId": parent_note_id,
        # Keep explicit null so callers can clear an existing prefix.
        "prefix": prefix,
    }
    if note_position is not None:
        payload["notePosition"] = note_position
    if is_expanded is not None:
        payload["isExpanded"] = is_expanded

    async with get_client() as client:
        response = await client.post(
            "/etapi/branches",
            json=payload,
        )
        response.raise_for_status()

        return Branch.model_validate(response.json())
