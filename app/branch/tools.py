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
            examples=["BiLlVTUX4Fzk_KMa5HXFDUW3J"],
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


@mcp.tool(
    name="update_branch",
    description=(
        "Patch a branch identified by the branchId with changes in the body. "
        "Only prefix and notePosition can be updated. If you want to update "
        "other properties, you need to delete the old branch and create a new one."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
)
async def update_branch(
    branch_id: Annotated[
        str,
        Field(
            ...,
            description="Identifies the branch",
            examples=["BiLlVTUX4Fzk_KMa5HXFDUW3J"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    prefix: Annotated[
        str | None,
        Field(
            description=(
                "Location-specific prefix shown before the note title. "
                "Pass null to clear an existing prefix."
            ),
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
        "prefix": prefix,
    }
    if note_position is not None:
        payload["notePosition"] = note_position
    if is_expanded is not None:
        payload["isExpanded"] = is_expanded

    async with get_client() as client:
        response = await client.patch(
            f"/etapi/branches/{branch_id}",
            json=payload,
        )
        response.raise_for_status()

        return Branch.model_validate(response.json())


@mcp.tool(
    name="refresh_note_order",
    description=(
        "Trigger a re-ordering push for all clients connected to the given parent note."
        " notePosition changes made via ETAPI are not automatically synced to connected"
        " clients (e.g. the Trilium web UI). Call this after updating notePosition on"
        " branches under the same parent to make the new order visible immediately."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def refresh_note_order(
    parent_note_id: Annotated[
        str,
        Field(
            ...,
            description="Identifies the parent note",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> None:
    async with get_client() as client:
        response = await client.post(f"/etapi/refresh-note-ordering/{parent_note_id}")
        response.raise_for_status()
