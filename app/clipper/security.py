import ipaddress
import socket
from urllib.parse import urlparse

_ALLOWED_SCHEMES = frozenset({"http", "https"})

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


class SSRFError(ValueError):
    """Raised when a URL is blocked by SSRF protection."""


def validate_url_for_fetch(url: str) -> str:
    """Validate that a URL is safe to fetch externally.

    Returns the URL if valid, raises SSRFError otherwise.
    """
    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise SSRFError(f"Scheme '{parsed.scheme}' is not allowed")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL has no hostname")

    try:
        resolved = ipaddress.ip_address(
            socket.gethostbyname(hostname)  # nosec B314
        )
    except (socket.gaierror, ValueError) as e:
        raise SSRFError(f"Cannot resolve hostname '{hostname}': {e}") from e

    for network in _PRIVATE_NETWORKS:
        if resolved in network:
            raise SSRFError(f"URL resolves to private/loopback address {resolved}")

    return url
