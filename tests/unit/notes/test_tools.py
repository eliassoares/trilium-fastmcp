import httpx
import pytest
import respx

from app.notes.tools import search_notes
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
