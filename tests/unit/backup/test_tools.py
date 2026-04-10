import httpx
import pytest
import respx

from app.backup.tools import create_backup
from tests.unit.conftest import TRILIUM_URL


@respx.mock
async def test_create_backup_returns_confirmation_message() -> None:
    respx.put(f"{TRILIUM_URL}/etapi/backup/now").mock(return_value=httpx.Response(204))

    result = await create_backup(backup_name="now")

    assert result == "Backup backup-now.db has been created"


@respx.mock
async def test_create_backup_sends_put_to_correct_endpoint() -> None:
    route = respx.put(f"{TRILIUM_URL}/etapi/backup/2026-04-10").mock(
        return_value=httpx.Response(204)
    )

    await create_backup(backup_name="2026-04-10")

    assert route.called


@respx.mock
async def test_create_backup_raises_on_http_error() -> None:
    respx.put(f"{TRILIUM_URL}/etapi/backup/now").mock(return_value=httpx.Response(500))

    with pytest.raises(httpx.HTTPStatusError):
        await create_backup(backup_name="now")
