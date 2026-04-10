import json
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


@pytest.fixture
def clipped_note_response(note_response: dict[str, object]) -> dict[str, object]:
    return {
        **note_response,
        "noteId": "clipped123",
        "title": "Extracted Title",
        "parentNoteIds": ["parent1234"],
        "parentBranchIds": ["branch123"],
    }


@pytest.fixture
def moved_note_response(note_response: dict[str, object]) -> dict[str, object]:
    return {
        **note_response,
        "noteId": "clipped123",
        "title": "Extracted Title",
        "parentNoteIds": ["dayNote123", "parent1234"],
        "parentBranchIds": ["branch123", "branch456"],
    }


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
    clipped_note_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page", lambda html, url: extracted_page
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html><body>ignored</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    clipper_route = respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123").mock(
        return_value=httpx.Response(200, json=clipped_note_response)
    )
    branch_route = respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    attribute_route = respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(
        return_value=httpx.Response(200)
    )

    result = await clip_url(
        url="https://example.com/article",
        parent_note_id="parent1234",
    )

    clipper_payload = json.loads(clipper_route.calls.last.request.content)
    assert clipper_payload["title"] == "Extracted Title"
    assert clipper_payload["clipType"] == "page"
    assert clipper_payload["pageUrl"] == "https://example.com/article"

    assert result.note_id == "clipped123"
    assert result.title == "Extracted Title"
    assert result.labels_created == 3
    assert result.warnings == []
    assert attribute_route.call_count == 3
    assert branch_route.called


@respx.mock
async def test_clip_url_uses_url_when_extracted_title_missing(
    monkeypatch: pytest.MonkeyPatch,
    extracted_page: ExtractedPage,
    clipped_note_response: dict[str, object],
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
    clipper_route = respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123").mock(
        return_value=httpx.Response(200, json=clipped_note_response)
    )
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(return_value=httpx.Response(200))

    result = await clip_url(
        url="https://example.com/article", parent_note_id="parent1234"
    )

    assert result.title == "https://example.com/article"
    assert b"https://example.com/article" in clipper_route.calls.last.request.content


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
    clipped_note_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page", lambda html, url: extracted_page
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html></html>",
            headers={"content-type": "text/html"},
        )
    )
    respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123").mock(
        return_value=httpx.Response(200, json=clipped_note_response)
    )
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    routes = respx.route(method="POST", url=f"{TRILIUM_URL}/etapi/attributes")
    routes.side_effect = [
        httpx.Response(200),
        RuntimeError("boom"),
        httpx.Response(200),
    ]

    result = await clip_url(
        url="https://example.com/article", parent_note_id="parent1234"
    )

    assert result.labels_created == 2
    assert len(result.warnings) == 1
    assert "siteName" in result.warnings[0]


@respx.mock
async def test_clip_url_embeds_images_in_native_clipper_payload(
    monkeypatch: pytest.MonkeyPatch,
    clipped_note_response: dict[str, object],
) -> None:
    extracted_page = ExtractedPage(
        title="Extracted Title",
        description="Summary",
        content_html=(
            '<article><img alt="cover" src="https://cdn.example.com/image.png"/></article>'
        ),
        canonical_url="https://example.com/article",
        site_name="Example Site",
        published_time="2024-01-02T03:04:05Z",
    )
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page", lambda html, url: extracted_page
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html><body>ignored</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    respx.get("https://cdn.example.com/image.png").mock(
        return_value=httpx.Response(
            200,
            content=b"png-bytes",
            headers={"content-type": "image/png"},
        )
    )
    clipper_route = respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123").mock(
        return_value=httpx.Response(200, json=clipped_note_response)
    )
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(return_value=httpx.Response(200))

    result = await clip_url(
        url="https://example.com/article",
        parent_note_id="parent1234",
    )

    clipper_payload = json.loads(clipper_route.calls.last.request.content)
    assert clipper_payload["pageUrl"] == "https://example.com/article"
    assert len(clipper_payload["images"]) == 1
    assert clipper_payload["images"][0]["src"] == "https://cdn.example.com/image.png"
    assert clipper_payload["images"][0]["dataUrl"].startswith("data:image/png;base64,")
    assert "https://cdn.example.com/image.png" not in clipper_payload["content"]
    assert result.warnings == []


@respx.mock
async def test_clip_url_warns_and_keeps_note_when_image_localization_fails(
    monkeypatch: pytest.MonkeyPatch,
    clipped_note_response: dict[str, object],
) -> None:
    extracted_page = ExtractedPage(
        title="Extracted Title",
        description="Summary",
        content_html='<article><img src="https://cdn.example.com/missing.png"/></article>',
        canonical_url="https://example.com/article",
        site_name="Example Site",
        published_time="2024-01-02T03:04:05Z",
    )
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page", lambda html, url: extracted_page
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html><body>ignored</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    respx.get("https://cdn.example.com/missing.png").mock(
        return_value=httpx.Response(404)
    )
    clipper_route = respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123").mock(
        return_value=httpx.Response(200, json=clipped_note_response)
    )
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(return_value=httpx.Response(200))

    result = await clip_url(
        url="https://example.com/article",
        parent_note_id="parent1234",
    )

    clipper_payload = json.loads(clipper_route.calls.last.request.content)
    assert clipper_payload["images"] == []
    assert "https://cdn.example.com/missing.png" in clipper_payload["content"]
    assert len(result.warnings) == 1
    assert "Failed to localize image" in result.warnings[0]


@respx.mock
async def test_clip_url_moves_native_clipper_note_to_requested_parent(
    monkeypatch: pytest.MonkeyPatch,
    extracted_page: ExtractedPage,
    note_response: dict[str, object],
    moved_note_response: dict[str, object],
) -> None:
    monkeypatch.setattr("app.clipper.tools.validate_url_for_fetch", lambda url: url)
    monkeypatch.setattr(
        "app.clipper.tools.extract_page", lambda html, url: extracted_page
    )

    respx.get("https://example.com/article").mock(
        return_value=httpx.Response(
            200,
            text="<html><body>ignored</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
        )
    )
    respx.post(f"{TRILIUM_URL}/api/clipper/notes").mock(
        return_value=httpx.Response(200, json={"noteId": "clipped123"})
    )
    initial_note_response = {
        **note_response,
        "noteId": "clipped123",
        "title": "Extracted Title",
        "parentNoteIds": ["dayNote123"],
        "parentBranchIds": ["branch123"],
    }
    note_route = respx.get(f"{TRILIUM_URL}/etapi/notes/clipped123")
    note_route.side_effect = [
        httpx.Response(200, json=initial_note_response),
        httpx.Response(200, json=moved_note_response),
    ]
    create_branch = respx.post(f"{TRILIUM_URL}/etapi/branches").mock(
        return_value=httpx.Response(
            201,
            json={
                "branchId": "branch456",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        )
    )
    branch_route = respx.route(
        method="GET", url__regex=rf"{TRILIUM_URL}/etapi/branches/.*"
    )
    branch_route.side_effect = [
        httpx.Response(
            200,
            json={
                "branchId": "branch123",
                "noteId": "clipped123",
                "parentNoteId": "dayNote123",
                "prefix": None,
                "notePosition": 10,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        ),
        httpx.Response(
            200,
            json={
                "branchId": "branch456",
                "noteId": "clipped123",
                "parentNoteId": "parent1234",
                "prefix": None,
                "notePosition": 20,
                "isExpanded": False,
                "utcDateModified": "2022-03-07T21:54:25.277Z",
            },
        ),
    ]
    delete_branch = respx.delete(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(204)
    )
    respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(return_value=httpx.Response(200))

    result = await clip_url(
        url="https://example.com/article",
        parent_note_id="parent1234",
    )

    create_branch_payload = json.loads(create_branch.calls.last.request.content)
    assert create_branch_payload == {
        "noteId": "clipped123",
        "parentNoteId": "parent1234",
    }
    assert delete_branch.called
    assert result.note_id == "clipped123"
