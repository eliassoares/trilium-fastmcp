import json

import httpx
import pytest
import respx

from app.attributes.tools import (
    create_attribute,
    delete_attribute,
    get_attribute,
    update_attribute,
)
from app.notes.schemas import AttributeType
from tests.unit.conftest import TRILIUM_URL


@pytest.fixture
def attribute_response() -> dict[str, object]:
    return {
        "attributeId": "attr1234",
        "noteId": "evnnmvHTCgIn",
        "type": "label",
        "name": "pageUrl",
        "value": "https://example.com/article",
        "position": 10,
        "isInheritable": False,
        "utcDateModified": "2022-03-07T21:54:25.277Z",
    }


@respx.mock
async def test_get_attribute_returns_attribute(
    attribute_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/attributes/attr1234").mock(
        return_value=httpx.Response(200, json=attribute_response)
    )

    result = await get_attribute(attribute_id="attr1234")

    assert result.attribute_id == "attr1234"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.type is AttributeType.label


@respx.mock
async def test_create_attribute_serializes_payload(
    attribute_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/attributes").mock(
        return_value=httpx.Response(200, json=attribute_response)
    )

    await create_attribute(
        note_id="evnnmvHTCgIn",
        type=AttributeType.label,
        name="pageUrl",
        value="https://example.com/article",
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload == {
        "noteId": "evnnmvHTCgIn",
        "type": "label",
        "name": "pageUrl",
        "value": "https://example.com/article",
        "isInheritable": False,
    }


@respx.mock
async def test_update_attribute_omits_none_fields(
    attribute_response: dict[str, object],
) -> None:
    request = respx.patch(f"{TRILIUM_URL}/etapi/attributes/attr1234").mock(
        return_value=httpx.Response(200, json=attribute_response)
    )

    await update_attribute(attribute_id="attr1234", value="updated")

    payload = json.loads(request.calls.last.request.content)
    assert payload == {"value": "updated"}


@respx.mock
async def test_delete_attribute_returns_success() -> None:
    respx.delete(f"{TRILIUM_URL}/etapi/attributes/attr1234").mock(
        return_value=httpx.Response(200)
    )

    result = await delete_attribute(attribute_id="attr1234")

    assert result == "Attribute deleted successfully"

