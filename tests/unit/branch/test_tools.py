import json

import httpx
import pytest
import respx

from app.branch.tools import (
    create_branch,
    get_branch,
    refresh_note_order,
    update_branch,
)
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


@respx.mock
async def test_create_branch_allows_omitting_optional_fields(
    branch_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/branches").mock(
        return_value=httpx.Response(201, json=branch_response)
    )

    result = await create_branch(
        note_id="evnnmvHTCgIn",
        parent_note_id="parent123",
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload == {
        "noteId": "evnnmvHTCgIn",
        "parentNoteId": "parent123",
        "prefix": None,
    }
    assert result.branch_id == "branch123"


@respx.mock
async def test_create_branch_preserves_null_prefix_when_clearing_existing_value(
    branch_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/branches").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await create_branch(
        note_id="evnnmvHTCgIn",
        parent_note_id="parent123",
        prefix=None,
        note_position=20,
        is_expanded=False,
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload["prefix"] is None
    assert payload["notePosition"] == 20
    assert payload["isExpanded"] is False


@respx.mock
async def test_create_branch_sends_explicit_prefix(
    branch_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/branches").mock(
        return_value=httpx.Response(201, json=branch_response)
    )

    await create_branch(
        note_id="evnnmvHTCgIn",
        parent_note_id="parent123",
        prefix="Archive",
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload["prefix"] == "Archive"


@respx.mock
async def test_create_branch_returns_branch_on_200_update(
    branch_response: dict[str, object],
) -> None:
    """200 means ETAPI updated an existing branch instead of creating a new one."""
    respx.post(f"{TRILIUM_URL}/etapi/branches").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    result = await create_branch(
        note_id="evnnmvHTCgIn",
        parent_note_id="parent123",
    )

    assert result.branch_id == "branch123"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.parent_note_id == "parent123"
    assert result.note_position == 10
    assert result.is_expanded is False


@respx.mock
async def test_create_branch_raises_on_error() -> None:
    respx.post(f"{TRILIUM_URL}/etapi/branches").mock(return_value=httpx.Response(422))

    with pytest.raises(httpx.HTTPStatusError):
        await create_branch(note_id="evnnmvHTCgIn", parent_note_id="parent123")


@respx.mock
async def test_get_branch_returns_all_fields(
    branch_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    result = await get_branch(branch_id="branch123")

    assert result.branch_id == "branch123"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.parent_note_id == "parent123"
    assert result.prefix is None
    assert result.note_position == 10
    assert result.is_expanded is False
    assert result.utc_date_modified is not None


@respx.mock
async def test_update_branch_sends_only_prefix_by_default(
    branch_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await update_branch(branch_id="branch123")

    payload = json.loads(request.calls.last.request.content)
    assert payload == {"prefix": None}


@respx.mock
async def test_update_branch_sends_explicit_prefix(
    branch_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await update_branch(branch_id="branch123", prefix="Archive")

    payload = json.loads(request.calls.last.request.content)
    assert payload["prefix"] == "Archive"


@respx.mock
async def test_update_branch_sends_null_prefix_to_clear(
    branch_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await update_branch(branch_id="branch123", prefix=None)

    payload = json.loads(request.calls.last.request.content)
    assert payload["prefix"] is None


@respx.mock
async def test_update_branch_sends_note_position_and_is_expanded(
    branch_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await update_branch(
        branch_id="branch123",
        note_position=30,
        is_expanded=True,
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload["notePosition"] == 30
    assert payload["isExpanded"] is True
    assert "note_position" not in payload


@respx.mock
async def test_update_branch_omits_none_optional_fields(
    branch_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    await update_branch(branch_id="branch123", prefix="X")

    payload = json.loads(request.calls.last.request.content)
    assert "notePosition" not in payload
    assert "isExpanded" not in payload


@respx.mock
async def test_update_branch_returns_branch(
    branch_response: dict[str, object],
) -> None:
    respx.patch(f"{TRILIUM_URL}/etapi/branches/branch123").mock(
        return_value=httpx.Response(200, json=branch_response)
    )

    result = await update_branch(branch_id="branch123", prefix="Archive")

    assert result.branch_id == "branch123"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.parent_note_id == "parent123"
    assert result.note_position == 10
    assert result.is_expanded is False


@respx.mock
async def test_update_branch_raises_on_not_found() -> None:
    respx.patch(f"{TRILIUM_URL}/etapi/branches/missing").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await update_branch(branch_id="missing")


@respx.mock
async def test_refresh_note_order_calls_correct_endpoint() -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/refresh-note-ordering/parent123").mock(
        return_value=httpx.Response(204)
    )

    await refresh_note_order(parent_note_id="parent123")

    assert request.called


@respx.mock
async def test_refresh_note_order_raises_on_error() -> None:
    respx.post(f"{TRILIUM_URL}/etapi/refresh-note-ordering/parent123").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await refresh_note_order(parent_note_id="parent123")
