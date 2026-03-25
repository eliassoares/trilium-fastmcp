import pytest

from app.client import _build_client


def test_raises_when_trilium_url_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRILIUM_URL", raising=False)

    with pytest.raises(RuntimeError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_url_ends_with_slash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TRILIUM_URL", "http://trilium:8080/")

    with pytest.raises(ValueError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_url_ends_with_etapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TRILIUM_URL", "http://trilium:8080/etapi")

    with pytest.raises(ValueError, match="TRILIUM_URL"):
        _build_client()


def test_raises_when_trilium_token_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRILIUM_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TRILIUM_TOKEN"):
        _build_client()
