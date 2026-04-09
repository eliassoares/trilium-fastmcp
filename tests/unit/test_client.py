import pytest

from app.client import _build_client, get_web_client
from app.config import settings


def test_raises_when_trilium_url_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "trilium_url", None)

    with pytest.raises(RuntimeError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_url_ends_with_slash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "trilium_url", "http://trilium:8080/")

    with pytest.raises(ValueError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_url_ends_with_etapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "trilium_url", "http://trilium:8080/etapi")

    with pytest.raises(ValueError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_token_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "trilium_token", None)

    with pytest.raises(RuntimeError, match="TRILIUM_TOKEN"):
        _build_client()


async def test_get_web_client_uses_external_defaults() -> None:
    async with get_web_client() as client:
        assert "authorization" not in client.headers
        assert client.headers["user-agent"].startswith("Mozilla/5.0")
        assert client.headers["accept-language"] == "en-US,en;q=0.5"
        assert client.follow_redirects is True
        assert client.max_redirects == 5
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 30.0
