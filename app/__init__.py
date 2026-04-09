from fastmcp import FastMCP
from app.config import settings

if settings.mcp_auth_token and settings.mcp_client_id:
    from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

    verifier = StaticTokenVerifier(
        tokens={
            settings.mcp_auth_token: {
                "client_id": settings.mcp_client_id,
                "scopes": ["read", "write"]
            }
        }
    )

    mcp = FastMCP("Trilium MCP Server", auth=verifier)
else:
    mcp = FastMCP("Trilium MCP Server")
