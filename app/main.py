import os

from fastmcp import FastMCP

mcp = FastMCP("Trilium MCP Server")


@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "6969"))
    mcp.run(transport="http", host=host, port=port)
