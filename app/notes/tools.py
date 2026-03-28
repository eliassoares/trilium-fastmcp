import logging
from typing import Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client
from app.notes.schemas import (
    NoteOrderBy,
    NoteOrderDirection,
    SearchNotesParams,
    SearchNotesResponse,
    Note
)

logger = logging.getLogger(__name__)


@mcp.tool(
    name="search_notes",
    description=(
        "Search notes using a query string as described in "
        "https://triliumnext.github.io/Docs/Wiki/search.html"
    ),
    annotations=ToolAnnotations(readOnlyHint=True),
    output_schema=SearchNotesResponse.model_json_schema(),
)
async def search_notes(
    search: Annotated[
        str,
        Field(
            description=(
                "Search query string as described in "
                "https://triliumnext.github.io/Docs/Wiki/search.html"
            ),
            examples=["#book #published"],
        ),
    ],
    fast_search: Annotated[
        bool,
        Field(
            description=(
                "Enable fast search — fulltext search does not look into note content"
            )
        ),
    ] = False,
    include_archived_notes: Annotated[
        bool,
        Field(
            description=(
                "By default archived notes are excluded. "
                "Set to true to include them in results."
            )
        ),
    ] = False,
    ancestor_note_id: Annotated[
        str | None,
        Field(
            description=(
                "Restrict search to a subtree identified by this note ID. "
                "By default the whole tree is searched."
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ] = None,
    ancestor_depth: Annotated[
        str | None,
        Field(
            description=(
                "Filter by depth in the tree relative to ancestor_note_id "
                "(e.g. 'eq1' for direct children, 'lt4' for depth less than 4)."
            ),
            examples=["eq1", "lt4", "gt2"],
        ),
    ] = None,
    order_by: Annotated[
        NoteOrderBy | None,
        Field(description="Property or label name to order search results by"),
    ] = None,
    order_direction: Annotated[
        NoteOrderDirection,
        Field(description="Sort direction for the results"),
    ] = NoteOrderDirection.asc,
    limit: Annotated[
        int | None,
        Field(description="Maximum number of results to return", examples=[10], gt=0),
    ] = None,
    debug: Annotated[
        bool,
        Field(
            description=(
                "Set to true to include query parsing debug info in the response"
            )
        ),
    ] = False,
) -> SearchNotesResponse:
    params = SearchNotesParams(
        search=search,
        fast_search=fast_search,
        include_archived_notes=include_archived_notes,
        ancestor_note_id=ancestor_note_id,
        ancestor_depth=ancestor_depth,
        order_by=order_by,
        order_direction=order_direction,
        limit=limit,
        debug=debug,
    )
    async with get_client() as client:
        logger.info("Calling search_notes with query: %s", search)
        response = await client.get(
            "/etapi/notes",
            params=params.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()
        return SearchNotesResponse.model_validate(response.json())


@mcp.tool(
        name="get_note",
        description="Returns a note identified by its ID",
        annotations=ToolAnnotations(readOnlyHint=True),
        output_schema=Note.model_json_schema()
)
async def get_note(
    note_id: Annotated[
        str, Field(
            description="A note id to retrieve",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        )
    ]
):
    async with get_client() as client:
        response = await client.get(
            f"/etapi/notes/{note_id}",
        )
        response.raise_for_status()
        return Note.model_validate(response.json())
