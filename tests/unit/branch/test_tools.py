import httpx
import pytest
import respx

from app.branch.tools import get_branch
from tests.unit.conftest import TRILIUM_URL


@pytest.fixture
def branch_response() -> dict[str, object]:
    return {
        "branchId": "branch123",
        "noteId": "evnnmvHTCgIn",
        "parentNoteId": "parent123",
        "prefix": None,
        "notePosition": 10,
        "isExpanded": False,
        "utcDateModified": "2022-03-07T21:54:25.277Z",
    }


@respx.mock
async def test_get_branch_returns_branch(
    branch_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    result = await get_branch(branch_id="branch123")

    assert result.branch_id == "branch123"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.parent_note_id == "parent123"


@respx.mock
async def test_get_branch_raises_on_not_found() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/branches/missing").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_branch(branch_id="missing")

