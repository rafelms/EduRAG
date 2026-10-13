#!/usr/bin/env bash
# Baixa os modelos no serviço ollama do compose. Rode depois do `docker compose up -d`.
set -euo pipefail

LLM_MODEL="${LLM_MODEL:-qwen2.5:3b}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"

for model in "$LLM_MODEL" "$EMBEDDING_MODEL"; do
  echo ">> baixando $model"
  docker compose exec ollama ollama pull "$model"
done
