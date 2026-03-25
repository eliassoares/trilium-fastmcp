import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx


def _build_client() -> httpx.AsyncClient:
    trilium_url = os.getenv("TRILIUM_URL")
    trilium_token = os.getenv("TRILIUM_TOKEN")

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
