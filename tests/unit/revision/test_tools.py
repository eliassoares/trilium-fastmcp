import httpx
import pytest
import respx

from app.notes.tools import get_note_revisions
from tests.unit.conftest import TRILIUM_URL


@respx.mock
async def test_get_note_revisions_returns_list(
    revision_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/revisions").mock(
        return_value=httpx.Response(200, json=[revision_response])
    )

    result = await get_note_revisions(note_id="evnnmvHTCgIn")

    assert len(result) == 1
    assert result[0].revision_id == "yujrHQa6XfFI"
    assert result[0].note_id == "evnnmvHTCgIn"
    assert result[0].title == "My Note"
    assert result[0].content_length == 584


@respx.mock
async def test_get_note_revisions_returns_empty_list() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/revisions").mock(
        return_value=httpx.Response(200, json=[])
    )

    result = await get_note_revisions(note_id="evnnmvHTCgIn")

    assert result == []


@respx.mock
async def test_get_note_revisions_calls_correct_endpoint(
    revision_response: dict[str, object],
) -> None:
    request = respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/revisions").mock(
        return_value=httpx.Response(200, json=[revision_response])
    )

    await get_note_revisions(note_id="evnnmvHTCgIn")

    assert request.called


@respx.mock
async def test_get_note_revisions_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/nonexistent/revisions").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_note_revisions(note_id="nonexistent")


@respx.mock
async def test_get_note_revisions_raises_on_unauthorized() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes/evnnmvHTCgIn/revisions").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_note_revisions(note_id="evnnmvHTCgIn")
