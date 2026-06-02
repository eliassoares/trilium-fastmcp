import socket
from typing import Any
from unittest.mock import patch

import pytest

from app.clipper.security import SSRFError, validate_url_for_fetch


def _mock_resolve(ip: str) -> Any:
    return patch("app.clipper.security.socket.gethostbyname", return_value=ip)


def test_valid_public_url_is_returned() -> None:
    with _mock_resolve("93.184.216.34"):  # example.com
        result = validate_url_for_fetch("https://example.com/article")
    assert result == "https://example.com/article"


def test_http_scheme_is_allowed() -> None:
    with _mock_resolve("93.184.216.34"):
        result = validate_url_for_fetch("http://example.com/page")
    assert result == "http://example.com/page"


@pytest.mark.parametrize("scheme", ["ftp", "file", "javascript", "data", ""])
def test_disallowed_scheme_raises(scheme: str) -> None:
    with pytest.raises(SSRFError, match="not allowed"):
        validate_url_for_fetch(f"{scheme}://example.com/x")


def test_url_with_no_hostname_raises() -> None:
    with pytest.raises(SSRFError, match="no hostname"):
        validate_url_for_fetch("https://")


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "127.0.0.2",
        "10.0.0.1",
        "10.255.255.255",
        "172.16.0.1",
        "172.31.255.255",
        "192.168.0.1",
        "192.168.255.255",
        "169.254.1.1",  # link-local
    ],
)
def test_private_ip_raises(ip: str) -> None:
    with _mock_resolve(ip), pytest.raises(SSRFError, match="private/loopback"):
        validate_url_for_fetch("https://internal.example.com/secret")


def test_unresolvable_hostname_raises() -> None:
    with (
        patch(
            "app.clipper.security.socket.gethostbyname",
            side_effect=socket.gaierror("Name or service not known"),
        ),
        pytest.raises(SSRFError, match="Cannot resolve hostname"),
    ):
        validate_url_for_fetch("https://this-does-not-exist.invalid/x")
