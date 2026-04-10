from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client


@mcp.tool(
    name="create_backup",
    description=(
        "Create a database backup under a given name. If the backupName "
        'is e.g. "now", then the backup will be written to "backup-now.db" file'
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_backup(
    backup_name: Annotated[
        str,
        Field(
            description="The backup name",
            examples=["2026-04-10"],
            pattern=r"[a-zA-Z0-9_-]{1,32}",
        ),
    ],
) -> str:
    async with get_client() as client:
        response = await client.put(f"/etapi/backup/{backup_name}")
        response.raise_for_status()

    return f"Backup backup-{backup_name}.db has been created"
