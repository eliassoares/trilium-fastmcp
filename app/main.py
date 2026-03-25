from app import mcp  # noqa: I001
from app.config import HOST, PORT
import app.tools  # noqa: F401 — side-effect: registers all tools with mcp


if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
