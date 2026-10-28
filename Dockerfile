# ---- build: instala as dependências num venv ----
FROM python:3.12-slim AS builder
# uv fixado por digest: o Dependabot não acompanha o COPY --from.
COPY --from=ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
# --locked: falha se o uv.lock não bater com o pyproject.toml, em vez de resolver de novo.
RUN uv sync --locked --no-dev --no-install-project

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
