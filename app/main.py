import app.general.tools
import app.notes.tools
from app import mcp
from app.config import settings

if __name__ == "__main__":
    mcp.run(transport="http", host=settings.host, port=settings.port)
