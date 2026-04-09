FROM python:3.13-alpine3.23 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

COPY . .

RUN uv sync --locked --no-dev

FROM python:3.13-alpine3.23 AS production

RUN adduser -D app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

USER app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

CMD ["python", "app/main.py"]
