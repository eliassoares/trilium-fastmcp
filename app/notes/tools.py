import logging
from datetime import datetime
from typing import Annotated

from fastmcp.utilities.types import File
from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client
from app.notes.schemas import (
    CreateNoteParams,
    Note,
    NoteAttachment,
    NoteExportType,
    NoteOrderBy,
    NoteOrderDirection,
    NoteRecentChange,
    NoteType,
    NoteWithBranch,
    SearchNotesParams,
    SearchNotesResponse,
    UpdateNoteParams
)

from app.revision.schemas import Revision

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
        Field(
            description="Maximum number of results to return",
            examples=[10],
            gt=0
        ),
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
            params=params.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            ),
        )
        response.raise_for_status()
        return SearchNotesResponse.model_validate(response.json())


@mcp.tool(
    name="get_note",
    description="Returns a note identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
    output_schema=Note.model_json_schema(),
)
async def get_note(
    note_id: Annotated[
        str,
        Field(
            description="A note id to retrieve the note",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> Note:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/notes/{note_id}",
        )
        response.raise_for_status()
        return Note.model_validate(response.json())


@mcp.tool(
    name="get_note_content",
    description="Returns note content identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_note_content(
    note_id: Annotated[
        str,
        Field(
            description="A note id to retrieve the note content",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> bytes:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/notes/{note_id}/content",
        )
        response.raise_for_status()
        return response.content


@mcp.tool(
    name="export_note",
    description=(
        "Exports ZIP file export of a given note subtree. "
        "To export whole document, use 'root' for noteId"
    ),
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def export_note(
    note_id: Annotated[
        str,
        Field(
            description="A note id to export the note",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    export_format: Annotated[
        NoteExportType,
        Field(
            description="The exporting format. Default: markdown",
            examples=[NoteExportType.markdown.value],
        ),
    ] = NoteExportType.markdown,
) -> File:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/notes/{note_id}/export",
            params={"format": export_format.value},
        )
        response.raise_for_status()
        return File(
            data=response.content,
            format="zip",
            name=f"{note_id}_export.zip",
        )


@mcp.tool(
    name="get_note_attachments",
    description="Returns all attachments for a note identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_note_attachments(
    note_id: Annotated[
        str,
        Field(
            description="A note id to retrieve the attachments",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
) -> list[NoteAttachment]:
    async with get_client() as client:
        response = await client.get(
            f"/etapi/notes/{note_id}/attachments",
        )
        response.raise_for_status()
        return [NoteAttachment.model_validate(item) for item in response.json()]


@mcp.tool(
    name="get_note_history",
    description=(
        "Returns recent changes including note creations, modifications, and deletions"
    ),
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def get_note_history(
    ancestor_note_id: Annotated[
        str,
        Field(
            description=(
                "Limit changes to a subtree identified by this note ID. "
                "Defaults to 'root' (all notes)."
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ] = "root",
) -> list[NoteRecentChange]:
    async with get_client() as client:
        response = await client.get(
            "/etapi/notes/history",
            params={"ancestorNoteId": ancestor_note_id}
        )
        response.raise_for_status()
        return [NoteRecentChange.model_validate(item) for item in response.json()]


@mcp.tool(
    name="get_note_revisions",
    description="Returns all revisions for a note identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def get_note_revisions(
    note_id: Annotated[
        str,
        Field(
            description="A note id to retrieve the revisions",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ]
) -> list[Revision]:
    async with get_client() as client:
        response = await client.get(f"/etapi/notes/{note_id}/revisions")
        response.raise_for_status()
        return [Revision.model_validate(item) for item in response.json()]


@mcp.tool(
    name="create_note",
    description=(
        "Create a note and place it into the note tree"
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_note(
    parent_note_id: Annotated[
        str,
        Field(
            description="Note ID of the parent note in the tree",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}"
        ),
    ],
    title: Annotated[
        str,
        Field(description="Note title",
              examples=["Cruzeiro, maior de Minas Gerais"]
              ),
    ],
    note_type: Annotated[
        NoteType,
        Field(
            description="Note type",
            examples=["text", "file"]
        ),
    ],
    content: Annotated[
        str,
        Field(
            description="Note content",
            examples=["CRU 6 x ATL 1"]
        ),
    ],
    mime: Annotated[
        str | None,
        Field(
            description=(
                "Note mime. This needs to be specified "
                "only for note types 'code', 'file', 'image'."
            ),
            examples=["application/json"]
        ),
    ] = None,
    note_position: Annotated[
        int | None,
        Field(
            description=(
                "Position of the note in the parent. Normal ordering is 10, 20, 30 ... "
                "So if you want to create a note on the first position, "
                "use e.g. 5, for second position 15, "
                "for last e.g. 1000000"
            ),
            examples=[10, 20]
        ),
    ] = None,
    prefix: Annotated[
        str | None,
        Field(
            description=(
                "Prefix is branch (placement) specific title prefix for the note. "
                "Let's say you have your note placed into two "
                "different places in the tree, "
                "but you want to change the title a bit in one of the placements. "
                "For this you can use prefix."
            ),
            examples=["Cruzei"]
        ),
    ] = None,
    is_expanded: Annotated[
        bool,
        Field(
            description=(
                "A bool that says: true if this note "
                "(as a folder) should appear expanded"
            ),
            examples=[True]
        ),
    ] = False,
    note_id: Annotated[
        str | None,
        Field(
            description=(
                "Note ID. DON'T specify unless you "
                "want to force a specific noteId"
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}"
        ),
    ] = None,
    branch_id: Annotated[
        str | None,
        Field(
            description=(
                "Branch ID. DON'T specify unless you "
                "want to force a specific branchId"
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}"
        ),
    ] = None,
    date_created:  Annotated[
        datetime | None,
        Field(
            description=(
                "Local timestamp of the note creation. "
                "Specify only if you want to override "
                "the default (current datetime in the "
                "current timezone/offset)."
            ),
            examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
        ),
    ] = None,
    utc_date_created:  Annotated[
        datetime | None,
        Field(
            description=(
                "UTC timestamp of the note creation. Specify only if you want "
                "to override the default (current datetime)."
            ),
            examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
        ),
    ] = None,
) -> NoteWithBranch:
    params = CreateNoteParams(
        parent_note_id=parent_note_id,
        title=title,
        type=note_type,
        content=content,
        mime=mime,
        note_position=note_position,
        prefix=prefix,
        is_expanded=is_expanded,
        note_id=note_id,
        branch_id=branch_id,
        date_created=date_created,
        utc_date_created=utc_date_created,
    )
    async with get_client() as client:
        response = await client.post(
            "/etapi/create-note",
            json=params.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            ),
        )
        response.raise_for_status()
        return NoteWithBranch.model_validate(response.json())


@mcp.tool(
    name="update_note_metadata",
    description="Update a note identified by the noteId with changes in the body",
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"}
)
async def update_note_metadata(
    note_id: Annotated[
        str,
        Field(
            description="The note id to patch the metadata",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    title: Annotated[
        str | None,
        Field(
            description=(
                "The note title"
            ),
            examples=["Cruzeiro maior de Minas"],
        ),
    ] = None,
    note_type: Annotated[
        NoteType | None,
        Field(
            description="Note type",
            examples=["text", "file"]
        ),
    ] = None,
    mime: Annotated[
        str | None,
        Field(
            description=(
                "Note mime. This needs to be specified "
                "only for note types 'code', 'file', 'image'."
            ),
            examples=["application/json"]
        ),
    ] = None,
    date_created:  Annotated[
        datetime | None,
        Field(
            description=(
                "Local timestamp of the note creation. "
                "Specify only if you want to override "
                "the default (current datetime in the "
                "current timezone/offset)."
            ),
            examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
        ),
    ] = None,
    utc_date_created:  Annotated[
        datetime | None,
        Field(
            description=(
                "UTC timestamp of the note creation. Specify only if you want "
                "to override the default (current datetime)."
            ),
            examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
        ),
    ] = None,
) -> Note:
    async with get_client() as client:
        params = UpdateNoteParams(
            title=title,
            type=note_type,
            mime=mime,
            date_created=date_created,
            utc_date_created=utc_date_created,
        )
        response = await client.patch(
            f"/etapi/notes/{note_id}",
            json=params.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            )
        )
        response.raise_for_status()
        return Note.model_validate(response.json())


@mcp.tool(
    name="update_note_content",
    description="Updates note content identified by its ID",
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
)
async def update_note_content(
    note_id: Annotated[
        str,
        Field(
            description="The note id to update the note content",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    content: Annotated[
        str,
        Field(
            description="Note content (HTML)",
            examples=["<p>CRU 6 x 1 ATL</p>"],
        ),
    ],
) -> None:
    async with get_client() as client:
        response = await client.put(
            f"/etapi/notes/{note_id}/content",
            content=content.encode(),
            headers={"Content-Type": "text/plain"},
        )
        response.raise_for_status()


@mcp.tool(
    name="create_note_revision",
    description="Create a note revision for the given note",
    annotations=ToolAnnotations(readOnlyHint=False),
    tags={"update"},
)
async def create_note_revision(
    note_id: Annotated[
        str,
        Field(
            description="The note id to create the revision",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ],
    revision_format: Annotated[
        NoteExportType,
        Field(
            description="The note revision format. Default: html",
            examples=[NoteExportType.html.value],
        ),
    ] = NoteExportType.html,
) -> str:
    async with get_client() as client:
        response = await client.post(
            f"/etapi/notes/{note_id}/revision",
            params={"format": revision_format.value},
        )
        response.raise_for_status()
        return "Revision created successfully"


@mcp.tool(
    name="delete_note",
    description="Deletes a single note based on the noteId supplied",
    annotations=ToolAnnotations(destructiveHint=True),
    tags={"delete"}
)
async def delete_note(
        note_id: Annotated[
        str,
        Field(
            description="The note id to delete it",
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
        ],
) -> str:
    async with get_client() as client:
        response = await client.delete(
            f"/etapi/notes/{note_id}"
        )
        response.raise_for_status()
    return "Note deleted successfully"
