

from typing import Annotated

from app import mcp
from mcp.types import ToolAnnotations
from pydantic import Field
from app.client import get_client
from app.branch.schemas import Branch


@mcp.tool(
    name="get_branch",
    description="Returns a branch identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def get_branch(
    branch_id: Annotated[
        str,
        Field(
            description="The branch id to retrieve the branch",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        )
    ]
) -> Branch:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/branches/{branch_id}",
        )
        response.raise_for_status()

        return Branch.model_validate(response.json())
