from os import getenv

HOST = getenv("HOST", "127.0.0.1")
PORT = int(getenv("PORT", "6969"))

TRILIUM_TOKEN = getenv("TRILIUM_TOKEN")
TRILIUM_URL = getenv("TRILIUM_URL")
