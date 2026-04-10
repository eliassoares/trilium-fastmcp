import json

import httpx
import pytest
import respx

from app.attachment.tools import create_attachment
from tests.unit.conftest import TRILIUM_URL


@pytest.fixture
def attachment_response() -> dict[str, object]:
    return {
        "attachmentId": "att1234",
        "ownerId": "evnnmvHTCgIn",
        "role": "file",
        "mime": "text/plain",
        "title": "snippet.txt",
        "position": 10,
        "blobId": "blob1234",
        "dateModified": "2022-02-09T22:52:36+01:00",
        "utcDateModified": "2022-03-07T21:54:25.277Z",
        "utcDateScheduledForErasureSince": None,
        "contentLength": 12,
    }


@respx.mock
async def test_create_attachment_serializes_payload_in_camel_case(
    attachment_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/attachments").mock(
        return_value=httpx.Response(201, json=attachment_response)
    )

    result = await create_attachment(
        owner_id="evnnmvHTCgIn",
        role="file",
        mime="text/plain",
        title="snippet.txt",
        content="hello world",
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload == {
        "ownerId": "evnnmvHTCgIn",
        "role": "file",
        "mime": "text/plain",
        "title": "snippet.txt",
        "content": "hello world",
    }
    assert result.attachment_id == "att1234"


@respx.mock
async def test_create_attachment_includes_optional_position_when_provided(
    attachment_response: dict[str, object],
) -> None:
    request = respx.post(f"{TRILIUM_URL}/etapi/attachments").mock(
        return_value=httpx.Response(201, json=attachment_response)
    )

    await create_attachment(
        owner_id="evnnmvHTCgIn",
        role="file",
        mime="application/json",
        title="data.json",
        content='{"ok":true}',
        position=10,
    )

    payload = json.loads(request.calls.last.request.content)
    assert payload["position"] == 10


async def test_create_attachment_rejects_binary_mime_types() -> None:
    with pytest.raises(ValueError, match="only supports text-like attachments"):
        await create_attachment(
            owner_id="evnnmvHTCgIn",
            role="image",
            mime="image/png",
            title="image.png",
            content="ignored",
        )


@respx.mock
async def test_create_attachment_accepts_response_without_content_length(
    attachment_response: dict[str, object],
) -> None:
    response_without_content_length = {
        key: value
        for key, value in attachment_response.items()
        if key != "contentLength"
    }
    respx.post(f"{TRILIUM_URL}/etapi/attachments").mock(
        return_value=httpx.Response(201, json=response_without_content_length)
    )

    result = await create_attachment(
        owner_id="evnnmvHTCgIn",
        role="file",
        mime="text/plain",
        title="snippet.txt",
        content="hello world",
    )

    assert result.content_length is None
