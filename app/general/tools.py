from mcp.types import ToolAnnotations

from app import mcp
from app.client import get_client
from app.general.schemas import AppInfoResponse


@mcp.tool(
    name="get_application_information",
    description="Returns information about the running Trilium instance",
    annotations=ToolAnnotations(readOnlyHint=True),
    output_schema=AppInfoResponse.model_json_schema(),
)
async def get_application_information() -> AppInfoResponse:
    async with get_client() as client:
        response = await client.get("/etapi/app-info")
        response.raise_for_status()
        return AppInfoResponse.model_validate(response.json())
