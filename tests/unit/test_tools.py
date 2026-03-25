import httpx
import pytest
import respx

from app.tools import get_application_information
from tests.unit.conftest import TRILIUM_URL


@respx.mock
async def test_get_application_information(
    app_info_response: dict[str, object],
) -> None:
    respx.get(f"{TRILIUM_URL}/etapi/app-info").mock(
        return_value=httpx.Response(200, json=app_info_response)
    )

    result = await get_application_information()

    assert result.app_version == "0.50.2"
    assert result.db_version == 194


@respx.mock
async def test_get_application_information_raises_on_error() -> None:
    respx.get(f"{TRILIUM_URL}/etapi/app-info").mock(return_value=httpx.Response(401))

    with pytest.raises(httpx.HTTPStatusError):
        await get_application_information()
