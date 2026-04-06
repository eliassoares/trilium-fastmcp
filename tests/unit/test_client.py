import pytest

from app.client import _build_client
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
