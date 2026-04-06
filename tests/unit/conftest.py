import pytest

from app.config import settings

TRILIUM_URL = "http://trilium:8080"
TRILIUM_TOKEN = "test-token"


@pytest.fixture(autouse=True)
def trilium_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "trilium_url", TRILIUM_URL)
    monkeypatch.setattr(settings, "trilium_token", TRILIUM_TOKEN)


@pytest.fixture
def note_response() -> dict[str, object]:
    return {
        "noteId": "evnnmvHTCgIn",
        "title": "My Note",
        "type": "text",
        "mime": "text/html",
        "isProtected": False,
        "blobId": "DecH36BK5cLX6dYDg5yx",
        "attributes": [],
        "parentNoteIds": [],
        "childNoteIds": [],
        "parentBranchIds": [],
        "childBranchIds": [],
        "dateCreated": "2022-02-09T22:52:36+01:00",
        "dateModified": "2022-02-09T22:52:36+01:00",
        "utcDateCreated": "2022-03-07T21:54:25.277Z",
        "utcDateModified": "2022-03-07T21:54:25.277Z",
    }


@pytest.fixture
def note_with_branch_response(note_response: dict[str, object]) -> dict[str, object]:
    return {
        "note": note_response,
        "branch": {
            "branchId": "evnnmvHTCgIn",
            "noteId": "evnnmvHTCgIn",
            "parentNoteId": "parentNoteId1",
            "prefix": None,
            "notePosition": 10,
            "isExpanded": False,
            "utcDateModified": "2022-03-07T21:54:25.277Z",
        },
    }


@pytest.fixture
def revision_response() -> dict[str, object]:
    return {
        "revisionId": "yujrHQa6XfFI",
        "noteId": "evnnmvHTCgIn",
        "type": "text",
        "mime": "text/html",
        "isProtected": False,
        "title": "My Note",
        "blobId": "DecH36BK5cLX6dYDg5yx",
        "dateLastEdited": "2022-02-09T22:52:36+01:00",
        "dateCreated": "2022-02-09T22:52:36+01:00",
        "utcDateLastEdited": "2022-03-07T21:54:25.277Z",
        "utcDateCreated": "2022-03-07T21:54:25.277Z",
        "utcDateModified": "2022-03-07T21:54:25.277Z",
        "contentLength": 584,
    }


@pytest.fixture
def app_info_response() -> dict[str, object]:
    return {
        "appVersion": "0.50.2",
        "dbVersion": 194,
        "syncVersion": 25,
        "buildDate": "2022-02-09T22:52:36+01:00",
        "buildRevision": "23daaa2387a0655685377f0a541d154aeec2aae8",
        "dataDirectory": "/home/user/data",
        "clipperProtocolVersion": "1.0",
        "utcDateTime": "2022-03-07T21:54:25.277Z",
    }
