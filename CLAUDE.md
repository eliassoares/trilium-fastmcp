# CLAUDE.md

## Project Overview

MCP (Model Context Protocol) server for Trilium Notes, exposing the ETAPI as MCP tools via FastMCP. Python 3.13+.

## Project Structure

```
app/
├── __init__.py      # FastMCP instance (mcp)
├── main.py          # Server entrypoint — side-effect imports tool modules + runs mcp
├── config.py        # Env vars (HOST, PORT, TRILIUM_URL, TRILIUM_TOKEN)
├── client.py        # httpx AsyncClient with get_client() context manager
├── general/
│   ├── schemas.py   # AppInfoResponse
│   └── tools.py     # get_application_information
└── notes/
    ├── schemas.py   # Note, Attribute, Branch, NoteWithBranch, SearchNotesParams, SearchNotesResponse, enums
    └── tools.py     # search_notes, get_note, get_note_content
```

## Commands

```bash
make install       # Install dependencies + pre-commit hooks
make lint          # Lint with ruff
make fix           # Lint with auto-fix
make format        # Format with ruff
make typecheck     # Type check with mypy (strict)
make security      # Security scan with bandit
make audit         # Dependency CVE check with pip-audit
make check         # Run all checks
make build         # Build Docker image (docker compose build)
make run           # Run via docker-compose (server + mcp-inspector)
make down          # Stop and remove docker-compose containers
make run-local     # Run locally with uv
make clean         # Remove caches and build artifacts
```

## Code Style

- **Formatter/Linter**: ruff (line-length 88)
- **Type checking**: mypy strict — all functions must have type annotations
- **Imports**: sorted by isort via ruff, `trilium_fastmcp` is first-party
- **Security**: bandit for code, pip-audit for dependencies
- **Python**: 3.13+, use modern syntax (match, type unions with `|`, etc.)

## Architecture

- Source code lives in `app/`
- This project wraps Trilium's ETAPI (`/etapi/...`) endpoints as MCP tools
- See README.md for the full list of ETAPI endpoints to implement
- Use `httpx` for async HTTP calls to Trilium via `get_client()` context manager
- Each ETAPI resource group gets its own module under `app/` with `schemas.py` and `tools.py`
- Each module's `tools.py` must be imported in `main.py` as a side-effect to register tools with `mcp`
- Tool parameters use `Annotated[type, Field(description=...)]`; construct a Pydantic params model internally
- Serialize params with `model_dump(by_alias=True, exclude_none=True, mode="json")` for camelCase query strings

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TRILIUM_URL` | — | Base URL of your Trilium instance |
| `TRILIUM_TOKEN` | — | ETAPI authentication token |
| `HOST` | `127.0.0.1` | Server bind address (`0.0.0.0` in Docker) |
| `PORT` | `6969` | Server port |

## mypy Notes

- `fastmcp.*` is configured with `disallow_untyped_decorators = false` in `pyproject.toml` — no need for `# type: ignore` on `@mcp.tool` decorators
- mypy pre-commit hook runs via `uv run mypy` (local hook) so it has access to the project `.venv` and installed packages

## Known Issues / Workarounds

- `pygments 2.19.2` has CVE-2026-4539 (no fix yet) — ignored via `pip-audit --ignore-vuln CVE-2026-4539`
- MCP Inspector: use `http://trilium-fastmcp:6969/mcp` as server URL (not `127.0.0.1`)
- Docker needs `PYTHONPATH=/app` to resolve `app.*` imports when running `python app/main.py`

## Dependencies

- Runtime: `fastmcp==3.1.1`, `httpx>=0.28.1`, `pydantic==2.12.5`
- Dev: `ruff`, `mypy`, `bandit`, `pip-audit`, `pre-commit`

## Conventions

- Write all code in English
- Keep functions small and focused
- Prefer `async`/`await` for I/O operations
- Never hardcode credentials — use environment variables
- All new code must pass ruff, mypy strict, and bandit before commit
- Pydantic models use `alias_generator=to_camel` + `populate_by_name=True` to map camelCase API responses
