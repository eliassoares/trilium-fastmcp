import logging
from datetime import UTC, datetime
from typing import Annotated

import httpx
from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client, get_web_client
from app.clipper.extractor import extract_page
from app.clipper.schemas import ClipResult
from app.clipper.security import SSRFError, validate_url_for_fetch
from app.notes.schemas import (
    CreateNoteParams,
    NoteType,
    NoteWithBranch,
    SearchNotesParams,
    SearchNotesResponse,
)

logger = logging.getLogger(__name__)

_MAX_RESPONSE_SIZE = 10_000_000  # 10 MB
_WEB_CLIPPER_NOTE_TITLE = "Web Clipper"


async def _resolve_parent_note_id(
    client: httpx.AsyncClient,
) -> str:
    """Find or create the 'Web Clipper' note under root."""
    params = SearchNotesParams(
        search=f'note.title = "{_WEB_CLIPPER_NOTE_TITLE}"',
        ancestor_note_id="root",
        ancestor_depth="eq1",
    )
    search_response = await client.get(
        "/etapi/notes",
        params=params.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        ),
    )
    search_response.raise_for_status()
    results = SearchNotesResponse.model_validate(search_response.json())

    if results.results:
        return results.results[0].note_id

    create_params = CreateNoteParams(
        parent_note_id="root",
        title=_WEB_CLIPPER_NOTE_TITLE,
        type=NoteType.text,
        content="",
    )
    create_response = await client.post(
        "/etapi/create-note",
        json=create_params.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        ),
    )
    create_response.raise_for_status()
    created = NoteWithBranch.model_validate(create_response.json())
    logger.info("Created 'Web Clipper' note: %s", created.note.note_id)
    return created.note.note_id


@mcp.tool(
    name="clip_url",
    description=(
        "Clip a web page and save it as a Trilium note. "
        "Fetches the URL, extracts readable content, "
        "and creates a note with metadata labels "
        "(clipType, pageUrl, iconClass). "
        "By default, clips are saved under a 'Web Clipper' "
        "note in root (created automatically if missing)."
    ),
    annotations=ToolAnnotations(readOnlyHint=False),
    output_schema=ClipResult.model_json_schema(),
)
async def clip_url(
    url: Annotated[
        str,
        Field(
            description="The URL of the web page to clip",
            examples=["https://martinfowler.com/articles/gen-ai-patterns/"],
        ),
    ],
    parent_note_id: Annotated[
        str | None,
        Field(
            description=(
                "Note ID of the parent note where the clip will be saved. "
                "If not provided, the clip is saved under "
                "a 'Web Clipper' note in root."
            ),
            examples=["evnnmvHTCgIn"],
            pattern="[a-zA-Z0-9_]{4,32}",
        ),
    ] = None,
    title: Annotated[
        str | None,
        Field(
            description=(
                "Override the auto-detected page title. "
                "If not provided, the title is extracted from the page."
            ),
        ),
    ] = None,
) -> ClipResult:
    try:
        validate_url_for_fetch(url)
    except SSRFError as e:
        raise ValueError(str(e)) from e

    async with get_web_client() as web_client:
        response = await web_client.get(url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        raise ValueError(
            f"URL returns non-HTML content: {content_type}"
        )

    if len(response.content) > _MAX_RESPONSE_SIZE:
        raise ValueError(
            f"Page too large: {len(response.content)} bytes "
            f"(max {_MAX_RESPONSE_SIZE})"
        )

    page = extract_page(response.text, url)

    final_title = title or page.title or url

    note_html = (
        f'<p><em>Clipped from: <a href="{url}">{url}</a></em></p>'
        f"{page.content_html}"
    )

    async with get_client() as client:
        resolved_parent = parent_note_id or await _resolve_parent_note_id(
            client
        )

        params = CreateNoteParams(
            parent_note_id=resolved_parent,
            title=final_title,
            type=NoteType.text,
            content=note_html,
        )

        create_response = await client.post(
            "/etapi/create-note",
            json=params.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            ),
        )
        create_response.raise_for_status()
        created = NoteWithBranch.model_validate(create_response.json())

        note_id = created.note.note_id
        warnings: list[str] = []
        labels_created = 0

        labels = [
            ("clipType", "page", 10),
            ("pageUrl", url, 20),
            ("iconClass", "bx bx-globe", 30),
        ]

        if page.published_time:
            labels.append(("publishedDate", page.published_time, 40))

        if page.site_name:
            labels.append(("siteName", page.site_name, 50))

        clip_date = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        labels.append(("clipDate", clip_date, 60))

        for label_name, label_value, _position in labels:
            try:
                await client.post(
                    "/etapi/attributes",
                    json={
                        "noteId": note_id,
                        "type": "label",
                        "name": label_name,
                        "value": label_value,
                        "isInheritable": False,
                    },
                )
                labels_created += 1
            except Exception as e:
                warnings.append(
                    f"Failed to create label '{label_name}': {e}"
                )

    return ClipResult(
        note_id=note_id,
        title=final_title,
        url=url,
        labels_created=labels_created,
        warnings=warnings,
    )
