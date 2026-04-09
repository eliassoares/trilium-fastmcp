import importlib
from unittest.mock import patch

import pytest

from app.config import Settings


@pytest.fixture
def _clear_app_module() -> None:
    """Ensure app module is freshly imported each test."""
    import sys

    sys.modules.pop("app", None)


@pytest.mark.usefixtures("_clear_app_module")
class TestAuthSetup:
    def test_mcp_has_no_auth_when_credentials_missing(self) -> None:
        mock_settings = Settings(
            trilium_url="http://trilium:8080",
            trilium_token="test-token",
        )

        with patch("app.config.settings", mock_settings):
            import app as app_module

            importlib.reload(app_module)

            assert app_module.mcp.auth is None

    def test_mcp_has_auth_when_credentials_provided(self) -> None:
        mock_settings = Settings(
            trilium_url="http://trilium:8080",
            trilium_token="test-token",
            mcp_auth_token="my-secret-token",
            mcp_client_id="my-client",
        )

        with patch("app.config.settings", mock_settings):
            import app as app_module

            importlib.reload(app_module)

            assert app_module.mcp.auth is not None

    def test_mcp_has_no_auth_when_only_token_provided(self) -> None:
        mock_settings = Settings(
            trilium_url="http://trilium:8080",
            trilium_token="test-token",
            mcp_auth_token="my-secret-token",
        )

        with patch("app.config.settings", mock_settings):
            import app as app_module

            importlib.reload(app_module)

            assert app_module.mcp.auth is None

    def test_mcp_has_no_auth_when_only_client_id_provided(self) -> None:
        mock_settings = Settings(
            trilium_url="http://trilium:8080",
            trilium_token="test-token",
            mcp_client_id="my-client",
        )

        with patch("app.config.settings", mock_settings):
            import app as app_module

            importlib.reload(app_module)

            assert app_module.mcp.auth is None
