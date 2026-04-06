import logging
import app.general.tools
import app.notes.tools
from app import mcp
from app.config import settings


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if settings.updating_disabled:
        logger.warning("Update tools are disabled!")
        mcp.disable(tags={"update"})

    mcp.run(transport="http", host=settings.host, port=settings.port)
