.PHONY: install lint fix format typecheck security audit check run build clean

install: ## Install dependencies and pre-commit hooks
	uv sync
	uv run pre-commit install

lint: ## Run linter
	uv run ruff check .

lint-fix: ## Run linter with auto-fix
	uv run ruff check . --fix

format: ## Run formatter
	uv run ruff format .

typecheck: ## Run type checker (strict)
	uv run mypy .

security: ## Run security scan (bandit)
	uv run bandit -r . -c pyproject.toml

audit: ## Run dependency vulnerability check
	uv run pip-audit

check: lint typecheck security audit ## Run all checks

build: ## Build Docker image
	docker compose build

run: ## Run the MCP server via docker-compose
	docker compose up

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
