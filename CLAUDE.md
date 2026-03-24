# CLAUDE.md

## Project Overview

MCP (Model Context Protocol) server for Trilium Notes, exposing the ETAPI as MCP tools via FastMCP. Python 3.13+.

## Project Structure

```
app/
├── __init__.py
└── main.py        # FastMCP server entrypoint
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
- Use `httpx` for async HTTP calls to Trilium
- Each ETAPI resource group (notes, branches, attributes, attachments, etc.) should be its own module under `app/`

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

## Conventions

- Write all code in English
- Keep functions small and focused
- Prefer `async`/`await` for I/O operations
- Never hardcode credentials — use environment variables
- All new code must pass ruff, mypy strict, and bandit before commit
