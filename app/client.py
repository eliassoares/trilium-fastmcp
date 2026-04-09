from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx

from app.config import settings


def _build_client() -> httpx.AsyncClient:
    trilium_url = settings.trilium_url
    trilium_token = settings.trilium_token

    if not trilium_url:
        raise RuntimeError("TRILIUM_URL environment variable is not set")
    if trilium_url.endswith("etapi") or trilium_url.endswith("/"):
        raise ValueError("TRILIUM_URL cannot finish with '/' or 'etapi'")
    if not trilium_token:
        raise RuntimeError("TRILIUM_TOKEN environment variable is not set")

    return httpx.AsyncClient(
        base_url=trilium_url,
        headers={"Authorization": f"Bearer {trilium_token}"},
        timeout=30.0,
    )


@asynccontextmanager
async def get_client() -> AsyncGenerator[httpx.AsyncClient]:
    async with _build_client() as client:
        yield client


@asynccontextmanager
async def get_web_client() -> AsyncGenerator[httpx.AsyncClient]:
    """HTTP client for fetching external URLs (no Trilium auth)."""
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; trilium-fastmcp/1.0; "
                "+https://github.com)"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
        },
        follow_redirects=True,
        max_redirects=5,
    ) as client:
        yield client
