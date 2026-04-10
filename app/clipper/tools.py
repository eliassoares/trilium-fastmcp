import base64
import logging
import mimetypes
import secrets
from datetime import UTC, datetime
from typing import Annotated
from urllib.parse import unquote, urlparse

import httpx
from bs4 import BeautifulSoup
from mcp.types import ToolAnnotations
from pydantic import Field

from app import mcp
from app.client import get_client, get_web_client
from app.clipper.extractor import extract_page
from app.clipper.schemas import ClipResult
from app.clipper.security import SSRFError, validate_url_for_fetch
from app.note.schemas import (
    CreateNoteParams,
    Note,
    NoteType,
    NoteWithBranch,
    SearchNotesParams,
    SearchNotesResponse,
)

logger = logging.getLogger(__name__)

_MAX_RESPONSE_SIZE = 10_000_000  # 10 MB
_MAX_IMAGE_SIZE = 10_000_000  # 10 MB
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
        params=params.model_dump(by_alias=True, exclude_none=True, mode="json"),
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
        json=create_params.model_dump(by_alias=True, exclude_none=True, mode="json"),
    )
    create_response.raise_for_status()
    created = NoteWithBranch.model_validate(create_response.json())
    logger.info("Created 'Web Clipper' note: %s", created.note.note_id)
    return created.note.note_id


def _guess_attachment_title(url: str, content_type: str) -> str:
    parsed = urlparse(url)
    filename = unquote(parsed.path.rsplit("/", 1)[-1]) if parsed.path else ""
    if filename:
        return filename

    extension = mimetypes.guess_extension(content_type) or ""
    return f"image{extension}"


async def _build_clipper_payload(
    *,
    note_html: str,
    title: str,
    page_url: str,
    labels: dict[str, str],
    web_client: httpx.AsyncClient,
) -> tuple[dict[str, object], list[str]]:
    soup = BeautifulSoup(note_html, "html.parser")
    warnings: list[str] = []
    images: list[dict[str, str]] = []
    localized_sources: dict[str, str] = {}

    for img in soup.find_all("img"):
        src = img.get("src")
        if not isinstance(src, str) or not src:
            continue

        for attr in (
            "data-src",
            "data-lazy-src",
            "data-original",
            "data-lazy",
            "srcset",
            "data-srcset",
        ):
            img.attrs.pop(attr, None)

        if src.startswith("data:image/"):
            image_id = f"inline.{src[11:14]}"
            images.append(
                {
                    "imageId": image_id,
                    "src": image_id,
                    "dataUrl": src,
                }
            )
            img["src"] = image_id
            continue

        if src in localized_sources:
            img["src"] = localized_sources[src]
        else:
            try:
                validate_url_for_fetch(src)
                response = await web_client.get(src)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                mime = content_type.split(";", 1)[0].strip().lower()
                if not mime.startswith("image/"):
                    raise ValueError(f"URL returns non-image content: {content_type}")
                if len(response.content) > _MAX_IMAGE_SIZE:
                    raise ValueError(
                        f"Image too large: {len(response.content)} bytes "
                        f"(max {_MAX_IMAGE_SIZE})"
                    )

                image_id = secrets.token_urlsafe(15)[:20]
                data_url = (
                    f"data:{mime};base64,"
                    f"{base64.b64encode(response.content).decode('ascii')}"
                )
                images.append(
                    {
                        "imageId": image_id,
                        "src": src,
                        "dataUrl": data_url,
                        "title": _guess_attachment_title(src, mime),
                    }
                )
                localized_sources[src] = image_id
                img["src"] = image_id
            except Exception as e:
                warnings.append(f"Failed to localize image '{src}': {e}")
                continue

    payload: dict[str, object] = {
        "title": title,
        "content": str(soup),
        "images": images,
        "pageUrl": page_url,
        "clipType": "page",
        "labels": labels,
    }

    return payload, warnings


async def _get_note(client: httpx.AsyncClient, note_id: str) -> Note:
    response = await client.get(f"/etapi/notes/{note_id}")
    response.raise_for_status()
    return Note.model_validate(response.json())


async def _move_clipped_note(
    *,
    client: httpx.AsyncClient,
    note_id: str,
    resolved_parent: str,
) -> list[str]:
    warnings: list[str] = []
    note = await _get_note(client, note_id)

    if resolved_parent not in note.parent_note_ids:
        create_response = await client.post(
            "/etapi/branches",
            json={
                "noteId": note_id,
                "parentNoteId": resolved_parent,
            },
        )
        create_response.raise_for_status()
        note = await _get_note(client, note_id)

    non_target_branch_ids: list[str] = []
    for branch_id in note.parent_branch_ids:
        branch_response = await client.get(f"/etapi/branches/{branch_id}")
        branch_response.raise_for_status()
        branch = branch_response.json()
        if branch["parentNoteId"] != resolved_parent:
            non_target_branch_ids.append(branch_id)

    if len(non_target_branch_ids) == 1:
        delete_response = await client.delete(
            f"/etapi/branches/{non_target_branch_ids[0]}"
        )
        delete_response.raise_for_status()
    elif len(non_target_branch_ids) > 1:
        warnings.append(
            "Clipped note has multiple non-target parent branches; "
            "left the original clipper branch in place."
        )

    return warnings


async def _create_note_via_native_clipper(
    *,
    client: httpx.AsyncClient,
    payload: dict[str, object],
) -> str:
    response = await client.post("/api/clipper/notes", json=payload)
    response.raise_for_status()
    note_id = response.json().get("noteId")
    if not isinstance(note_id, str) or not note_id:
        raise ValueError("Clipper API did not return a noteId")
    return note_id


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
            raise ValueError(f"URL returns non-HTML content: {content_type}")

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
        clipper_labels: dict[str, str] = {}
        if page.published_time:
            clipper_labels["publishedDate"] = page.published_time

        async with get_client() as client:
            resolved_parent = parent_note_id or await _resolve_parent_note_id(client)
            clipper_payload, image_warnings = await _build_clipper_payload(
                note_html=note_html,
                title=final_title,
                page_url=url,
                labels=clipper_labels,
                web_client=web_client,
            )
            warnings: list[str] = []
            warnings.extend(image_warnings)
            note_id = await _create_note_via_native_clipper(
                client=client,
                payload=clipper_payload,
            )
            warnings.extend(
                await _move_clipped_note(
                    client=client,
                    note_id=note_id,
                    resolved_parent=resolved_parent,
                )
            )

            labels = [
                ("iconClass", "bx bx-globe"),
                ("siteName", page.site_name),
                ("clipDate", datetime.now(tz=UTC).strftime("%Y-%m-%d")),
            ]
            labels_created = 0

            for label_name, label_value in labels:
                if not label_value:
                    continue
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
                    warnings.append(f"Failed to create label '{label_name}': {e}")

    return ClipResult(
        note_id=note_id,
        title=final_title,
        url=url,
        labels_created=labels_created,
        warnings=warnings,
    )
