# ---- build: gera os arquivos estáticos ----
FROM node:26-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- runtime: nginx serve o build e faz proxy de /api para a API ----
FROM nginxinc/nginx-unprivileged:1.21-alpine
# CVE-2026-111497 (CRITICAL): a base ainda traz brotli-libs 1.2.0-r1; a correção é a 1.2.1-r0.
# Remover quando a base vier com ela. O apk precisa de root; depois volta ao uid 101 da base.
USER root
RUN apk upgrade --no-cache brotli-libs
USER 101
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 8080
