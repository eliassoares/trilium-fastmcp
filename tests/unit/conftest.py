import pytest

TRILIUM_URL = "http://trilium:8080"
TRILIUM_TOKEN = "test-token"


@pytest.fixture(autouse=True)
def trilium_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRILIUM_URL", TRILIUM_URL)
    monkeypatch.setenv("TRILIUM_TOKEN", TRILIUM_TOKEN)


@pytest.fixture
def app_info_response() -> dict[str, object]:
    return {
        "appVersion": "0.50.2",
        "dbVersion": 194,
        "syncVersion": 25,
        "buildDate": "2022-02-09T22:52:36+01:00",
        "buildRevision": "23daaa2387a0655685377f0a541d154aeec2aae8",
        "dataDirectory": "/home/user/data",
        "clipperProtocolVersion": "1.0",
        "utcDateTime": "2022-03-07T21:54:25.277Z",
    }
