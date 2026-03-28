import httpx
import pytest
import respx

from app.notes.tools import get_note, get_note_content, search_notes
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
