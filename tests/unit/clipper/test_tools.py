from dataclasses import replace

import httpx
import pytest
import respx

from app.clipper.extractor import ExtractedPage
from app.clipper.tools import _MAX_RESPONSE_SIZE, _resolve_parent_note_id, clip_url
from tests.unit.conftest import TRILIUM_URL


@pytest.fixture
def extracted_page() -> ExtractedPage:
    return ExtractedPage(
        title="Extracted Title",
        description="Summary",
        content_html="<article><p>Hello</p></article>",
        canonical_url="https://example.com/article",
        site_name="Example Site",
        published_time="2024-01-02T03:04:05Z",
    )


@respx.mock
async def test_resolve_parent_note_id_returns_existing_note() -> None:
    search = respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "noteId": "webClip123",
                        "title": "Web Clipper",
                        "type": "text",
                        "mime": "text/html",
                        "isProtected": False,
                        "blobId": "blob123",
                        "attributes": [],
                        "parentNoteIds": ["root"],
                        "childNoteIds": [],
                        "parentBranchIds": [],
                        "childBranchIds": [],
                        "dateCreated": "2022-02-09T22:52:36+01:00",
                        "dateModified": "2022-02-09T22:52:36+01:00",
                        "utcDateCreated": "2022-03-07T21:54:25.277Z",
                        "utcDateModified": "2022-03-07T21:54:25.277Z",
                    }
                ]
            },
        )
    )

    async with httpx.AsyncClient(base_url=TRILIUM_URL) as client:
        result = await _resolve_parent_note_id(client)

    assert result == "webClip123"
    params = search.calls.last.request.url.params
    assert params["search"] == 'note.title = "Web Clipper"'
    assert params["ancestorNoteId"] == "root"
    assert params["ancestorDepth"] == "eq1"


@respx.mock
async def test_resolve_parent_note_id_creates_container_when_missing(
    note_with_branch_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/notes").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    create = respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )

    async with httpx.AsyncClient(base_url=TRILIUM_URL) as client:
        result = await _resolve_parent_note_id(client)

    assert result == "evnnmvHTCgIn"
    assert create.calls.last.request.content


@respx.mock
async def test_clip_url_creates_note_and_labels(
    monkeypatch: pytest.MonkeyPatch,
    extracted_page: ExtractedPage,
    note_with_branch_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr("app.clipper.tools.extract_page", lambda html, url: extracted_page)

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html><body>ignored</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )
    attribute_route = respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(
        return_value=httpx.Response(200)
    )

    result = await clip_url(
        url="https://example.com/article",
        parent_note_id="parent1234",
    )

    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "Extracted Title"
    assert result.labels_created == 6
    assert result.warnings == []
    assert attribute_route.call_count == 6


@respx.mock
async def test_clip_url_uses_url_when_extracted_title_missing(
    monkeypatch: pytest.MonkeyPatch,
    extracted_page: ExtractedPage,
    note_with_branch_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page",
        lambda html, url: replace(extracted_page, title=""),
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html></html>",
            headers={"content-type": "text/html"},
        )
    )
    create = respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )
    respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(
        return_value=httpx.Response(200)
    )

    result = await clip_url(url="https://example.com/article", parent_note_id="parent1234")

    assert result.title == "https://example.com/article"
    assert b"https://example.com/article" in create.calls.last.request.content


@respx.mock
async def test_clip_url_rejects_non_html_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)

    respx.get("https://example.com/file.pdf").mock(
        return_value=httpx.Response(
            200,
            content=b"%PDF",
            headers={"content-type": "application/pdf"},
        )
    )

    with pytest.raises(ValueError, match="non-HTML content"):
        await clip_url(url="https://example.com/file.pdf", parent_note_id="parent1234")


@respx.mock
async def test_clip_url_rejects_large_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            content=b"x" * (_MAX_RESPONSE_SIZE + 1),
            headers={"content-type": "text/html"},
        )
    )

    with pytest.raises(ValueError, match="Page too large"):
        await clip_url(url="https://example.com/article", parent_note_id="parent1234")


@respx.mock
async def test_clip_url_collects_attribute_creation_warnings(
    monkeypatch: pytest.MonkeyPatch,
    extracted_page: ExtractedPage,
    note_with_branch_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr("app.clipper.tools.extract_page", lambda html, url: extracted_page)

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html></html>",
            headers={"content-type": "text/html"},
        )
    )
    respx.post(f"{TRILIUM_URL}/etapi/create-note").mock(
        return_value=httpx.Response(200, json=note_with_branch_response)
    )
    routes = respx.route(method="POST", url=f"{TRILIUM_URL}/etapi/attributes")
    routes.side_effect = [
        httpx.Response(200),
        RuntimeError("boom"),
        httpx.Response(200),
        httpx.Response(200),
        httpx.Response(200),
        httpx.Response(200),
    ]

    result = await clip_url(url="https://example.com/article", parent_note_id="parent1234")

    assert result.labels_created == 5
    assert len(result.warnings) == 1
    assert "pageUrl" in result.warnings[0]
