import httpx
import pytest
import respx

from app.notes.tools import get_note_revisions
from app.revision.tools import get_revision, get_revision_content
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


@respx.mock
async def test_get_revision_returns_revision(
    revision_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/revisions/yujrHQa6XfFI").mock(
        return_value=httpx.Response(200, json=revision_response)
    )

    result = await get_revision(revision_id="yujrHQa6XfFI")

    assert result.revision_id == "yujrHQa6XfFI"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "My Note"


@respx.mock
async def test_get_revision_accepts_null_content_length(
    revision_response: dict[str, object],
) -> None:
    revision_response_without_content_length = {
        k: v for k, v in revision_response.items() if k != "contentLength"
    }
    respx.get(f"{TRILIUM_URL}/etapi/revisions/yujrHQa6XfFI").mock(
        return_value=httpx.Response(200, json=revision_response_without_content_length)
    )

    result = await get_revision(revision_id="yujrHQa6XfFI")

    assert result.content_length is None


@respx.mock
async def test_get_revision_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/revisions/nonexistent").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_revision(revision_id="nonexistent")


@respx.mock
async def test_get_revision_raises_on_unauthorized() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/revisions/yujrHQa6XfFI").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_revision(revision_id="yujrHQa6XfFI")


@respx.mock
async def test_get_revision_content_returns_text() -> None:
    html = "<p>Hello world</p>"
    respx.get(f"{TRILIUM_URL}/etapi/revisions/yujrHQa6XfFI/content").mock(
        return_value=httpx.Response(200, content=html.encode())
    )

    result = await get_revision_content(revision_id="yujrHQa6XfFI")

    assert result == html


@respx.mock
async def test_get_revision_content_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/revisions/nonexistent/content").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_revision_content(revision_id="nonexistent")


@respx.mock
async def test_get_revision_content_raises_on_unauthorized() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/revisions/yujrHQa6XfFI/content").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_revision_content(revision_id="yujrHQa6XfFI")
