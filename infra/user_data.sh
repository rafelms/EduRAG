#!/bin/bash
# Primeiro boot do EC2 do EduRAG (roda como root, uma vez só).
# Log: /var/log/cloud-init-output.log
set -euo pipefail

COMPOSE_VERSION="v5.7.1"
COMPOSE_SHA256="af426722a8af5de812fcee30cc1c39f0639f5f723cbadefb25e5d4db054064cf"
PLUGINS_DIR="/usr/local/lib/docker/cli-plugins"
COMPOSE_BIN="${PLUGINS_DIR}/docker-compose"

# 1. Docker do repositório do AL2023, ligado agora e em todo boot.
dnf install -y docker
systemctl enable --now docker

# 2. Pasta onde o Docker procura plugins para todos os usuários.
mkdir -p "${PLUGINS_DIR}"

# 3. Compose em versão fixa.
curl -fsSL -o "${COMPOSE_BIN}" \
  "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64"

# 4. Confere o hash ANTES de tornar executável. Se não bater, o set -e para aqui.
echo "${COMPOSE_SHA256}  ${COMPOSE_BIN}" | sha256sum -c -
chmod +x "${COMPOSE_BIN}"

docker --version
docker compose version
