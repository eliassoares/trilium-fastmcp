import asyncio

import app.main
from app import mcp


def test_main_registers_branch_tool() -> None:
    tools = asyncio.run(mcp.list_tools())

    assert any(tool.name == "get_branch" for tool in tools)
