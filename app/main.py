import logging

import app.attributes.tools
import app.clipper.tools
import app.general.tools
import app.notes.tools
import app.revision.tools
from app import mcp
from app.config import settings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if settings.updating_disabled:
        logger.warning("Update tools are disabled!")
        mcp.disable(tags={"update"})

    if settings.deleting_disabled:
        logger.warning("Delete tools are disabled!")
        mcp.disable(tags={"delete"})

    mcp.run(transport="http", host=settings.host, port=settings.port)
