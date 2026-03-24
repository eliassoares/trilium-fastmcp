# CLAUDE.md

## Project Overview

MCP (Model Context Protocol) server for Trilium Notes, exposing the ETAPI as MCP tools via FastMCP. Python 3.13+.

## Commands

```bash
uv sync                          # Install dependencies
uv run ruff check .              # Lint
uv run ruff check . --fix        # Lint with auto-fix
uv run ruff format .             # Format
uv run mypy .                    # Type check (strict mode)
uv run bandit -r . -c pyproject.toml  # Security scan
uv run pip-audit                 # Dependency vulnerability check
uv run pre-commit run --all-files    # Run all pre-commit hooks
```

## Code Style

- **Formatter/Linter**: ruff (line-length 88)
- **Type checking**: mypy strict — all functions must have type annotations
- **Imports**: sorted by isort via ruff, `trilium_fastmcp` is first-party
- **Security**: bandit for code, pip-audit for dependencies
- **Python**: 3.13+, use modern syntax (match, type unions with `|`, etc.)

## Architecture

- This project wraps Trilium's ETAPI (`/etapi/...`) endpoints as MCP tools
- See README.md for the full list of ETAPI endpoints to implement
- Use `httpx` for async HTTP calls to Trilium
- Each ETAPI resource group (notes, branches, attributes, attachments, etc.) should be its own module

## Conventions

- Write all code in English
- Keep functions small and focused
- Prefer `async`/`await` for I/O operations
- Never hardcode credentials — use environment variables or config
- All new code must pass ruff, mypy strict, and bandit before commit
