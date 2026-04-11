# Contributing to trilium-fastmcp

Thanks for your interest in contributing! This document explains how to set up the project locally, the conventions it follows, and how to submit changes.

## Development setup

Requirements:

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker (optional, for running the full stack with MCP Inspector)
- A running [Trilium](https://github.com/TriliumNext/Trilium) instance with ETAPI enabled

Clone and install:

```bash
git clone https://github.com/eliassoares/trilium-fastmcp.git
cd trilium-fastmcp
make install
```

`make install` runs `uv sync` and installs the `pre-commit` hooks. The hooks run ruff, mypy, and bandit on every commit.

Create a `.env` file with at least `TRILIUM_URL` and `TRILIUM_TOKEN` (see README for the full list of environment variables).

## Running the server

```bash
make run-local     # Run locally with uv
make run           # Run via docker-compose (server + MCP Inspector)
```

## Quality checks

Before opening a PR, run:

```bash
make check
```

This runs, in order:

- `ruff check` — linting
- `mypy` (strict) — type checking
- `bandit` — security scan
- `pip-audit` — dependency CVE check
- `pytest` — unit tests

All of these also run in CI on every pull request.

## Code style

- **Python**: 3.13+, use modern syntax (`match`, `type` unions with `|`, etc.)
- **Formatter/Linter**: ruff with line length 88
- **Type checking**: mypy strict — every function must have type annotations
- **Security**: bandit for code, pip-audit for dependencies
- Write all code and comments in English
- Prefer `async`/`await` for I/O operations
- Never hardcode credentials — use environment variables

## Architecture conventions

- Source lives in `app/`
- Each ETAPI resource group is its own module (e.g. `app/note/`, `app/branch/`) with `schemas.py` and `tools.py`
- Each module's `tools.py` must be imported in `app/main.py` so its tools get registered with the FastMCP instance
- Tool parameters use `Annotated[type, Field(description=...)]`; build a Pydantic model internally for serialization
- Serialize outgoing params with `model_dump(by_alias=True, exclude_none=True, mode="json")` for camelCase query strings
- Pydantic models use `alias_generator=to_camel` + `populate_by_name=True` to map camelCase API responses
- HTTP calls go through the `get_client()` async context manager in `app/client.py`
- Tools that modify state must be tagged `{"update"}` or `{"delete"}` so they can be disabled via `UPDATING_DISABLED` / `DELETING_DISABLED`

## Tests

Unit tests live in `tests/unit/`. Run them with:

```bash
make test
```

New tools should ship with tests that mock the HTTP client. Look at existing tests for the pattern.

## Submitting changes

1. Fork the repository and create a branch from `main`
2. Make your changes, keeping commits focused and descriptive
3. Run `make check` and make sure everything passes
4. Open a pull request against `main` with a clear description of the change and why

For larger changes, please open an issue first so we can discuss the approach.

## Reporting bugs and requesting features

Please use the issue templates in the repository to report bugs or request features. For security issues, see [SECURITY.md](SECURITY.md) — do **not** open a public issue.

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
