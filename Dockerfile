# syntax=docker/dockerfile:1

# ---- build: instala as dependências num venv ----
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# ---- runtime: imagem enxuta, sem uv, usuário não-root ----
FROM python:3.12-slim
RUN useradd --create-home --uid 10001 edurag
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER edurag
EXPOSE 8000
# Aplica as migrations e sobe a API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
