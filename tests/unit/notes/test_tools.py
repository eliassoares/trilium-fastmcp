import json

import httpx
import pytest
import respx

from app.notes.schemas import NoteExportType, NoteType
from app.notes.tools import (
    create_note,
    export_note,
    get_note,
    get_note_content,
    search_notes,
    update_note_metadata,
)
from tests.unit.conftest import TRILIUM_URL


@respx.mock
async def test_search_notes_returns_results(
    note_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(200, json={"results": [note_response]})
    )

    result = await search_notes(search="#book")

    assert len(result.results) == 1
    assert result.results[0].note_id == "evnnmvHTCgIn"
    assert result.results[0].title == "My Note"


@respx.mock
async def test_search_notes_passes_search_query() -> None:
    request = respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    await search_notes(search="#book")

    assert request.called
    assert request.calls.last.request.url.params["search"] == "#book"


@respx.mock
async def test_search_notes_passes_optional_params() -> None:
    request = respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    await search_notes(search="#book", fast_search=True, limit=5)

    params = request.calls.last.request.url.params
    assert params["fastSearch"] == "true"
    assert params["limit"] == "5"


@respx.mock
async def test_search_notes_omits_none_params() -> None:
    request = respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    await search_notes(search="#book")

    params = request.calls.last.request.url.params
    assert "ancestorNoteId" not in params
    assert "orderBy" not in params


@respx.mock
async def test_search_notes_raises_on_error() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes").mock(return_value=httpx.Response(401))

    with pytest.raises(httpx.HTTPStatusError):
        await search_notes(search="#book")


@respx.mock
async def test_get_note_returns_note(
    note_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(200, json=note_response)
    )

    result = await get_note(note_id="evnnmvHTCgIn")

    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "My Note"
    assert result.type.value == "text"
    assert result.mime == "text/html"
    assert result.is_protected is False


@respx.mock
async def test_get_note_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/nonexistent").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_note(note_id="nonexistent")


@respx.mock
async def test_get_note_raises_on_unauthorized() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_note(note_id="evnnmvHTCgIn")


@respx.mock
async def test_get_note_content_returns_html() -> None:
    html = "<p>Hello world</p>"
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/content").mock(
        return_value=httpx.Response(200, content=html.encode())
    )

    result = await get_note_content(note_id="evnnmvHTCgIn")

    assert result == html.encode()


@respx.mock
async def test_get_note_content_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/nonexistent/content").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_note_content(note_id="nonexistent")


@respx.mock
async def test_export_note_returns_zip() -> None:
    zip_bytes = b"PK\x03\x04fake-zip-content"
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/export").mock(
        return_value=httpx.Response(200, content=zip_bytes)
    )

    result = await export_note(note_id="evnnmvHTCgIn")

    assert result.data == zip_bytes


@respx.mock
async def test_export_note_passes_format_param() -> None:
    request = respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/export").mock(
        return_value=httpx.Response(200, content=b"PK\x03\x04fake-zip-content")
    )

    await export_note(note_id="evnnmvHTCgIn", export_format=NoteExportType.html)

    assert request.calls.last.request.url.params["format"] == "html"


@respx.mock
async def test_export_note_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/nonexistent/export").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await export_note(note_id="nonexistent")


@respx.mock
async def test_create_note_returns_note_with_branch(
    note_with_branch_response: dict[str, object],
) -> None:
    respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )

    result = await create_note(
        parent_note_id="parentNoteId1",
        title="My Note",
        note_type=NoteType.text,
        content="hello",
    )

    assert result.note.note_id == "evnnmvHTCgIn"
    assert result.note.title == "My Note"
    assert result.branch.parent_note_id == "parentNoteId1"


@respx.mock
async def test_create_note_serializes_payload(
    note_with_branch_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )

    await create_note(
        parent_note_id="parentNoteId1",
        title="My Note",
        note_type=NoteType.text,
        content="hello",
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload["parentNoteId"] == "parentNoteId1"
    assert payload["type"] == "text"
    assert "mime" not in payload
    assert "notePosition" not in payload
    assert "prefix" not in payload


@respx.mock
async def test_create_note_raises_on_error() -> None:
    respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(400)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await create_note(
            parent_note_id="parentNoteId1",
            title="My Note",
            note_type=NoteType.text,
            content="hello",
        )


@respx.mock
async def test_update_note_metadata_returns_note(
    note_response: dict[str, object],
) -> None:
    respx.patch(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(200, json=note_response)
    )

    result = await update_note_metadata(note_id="evnnmvHTCgIn", title="New Title")

    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "My Note"


@respx.mock
async def test_update_note_metadata_serializes_payload(
    note_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(200, json=note_response)
    )

    await update_note_metadata(note_id="evnnmvHTCgIn", title="New Title", note_type=NoteType.text)

    payload = json.loads(request.calls.last.request.content)
    assert payload["title"] == "New Title"
    assert payload["type"] == "text"
    assert "noteId" not in payload
    assert "mime" not in payload


@respx.mock
async def test_update_note_metadata_omits_none_fields(
    note_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(200, json=note_response)
    )

    await update_note_metadata(note_id="evnnmvHTCgIn", title="New Title")

    payload = json.loads(request.calls.last.request.content)
    assert list(payload.keys()) == ["title"]


@respx.mock
async def test_update_note_metadata_raises_on_not_found() -> None:
    respx.patch(f"{TRILIUM_URL}/etapi/notes/nonexistent").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await update_note_metadata(note_id="nonexistent", title="New Title")


@respx.mock
async def test_update_note_metadata_raises_on_unauthorized() -> None:
    respx.patch(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await update_note_metadata(note_id="evnnmvHTCgIn", title="New Title")
