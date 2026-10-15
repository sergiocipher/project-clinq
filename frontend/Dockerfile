# WHY THIS FILE EXISTS:
# Multi-stage build for the React frontend.
# Stage 1 (builder): installs Node dependencies and compiles the app to static
#   files in dist/. Build tools (node_modules, npm) never reach the final image.
# Stage 2 (runtime): uses nginx-unprivileged which runs as UID 101 (non-root)
#   and listens on port 8080 instead of 80. The Nginx template injects
#   BACKEND_URL at startup so the proxy target is configurable per environment.

# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first for layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Pass git SHA as build arg so the UI build badge shows the commit
ARG APP_VERSION=dev
ENV VITE_APP_VERSION=${APP_VERSION}

COPY . .
RUN npm run build

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM nginxinc/nginx-unprivileged:1.27-alpine

# BACKEND_URL is substituted into default.conf.template by the Nginx entrypoint
ENV BACKEND_URL=http://backend:8000

# OCI source label
LABEL org.opencontainers.image.source="https://github.com/sergiocipher/project-clinq"

# Copy compiled assets and Nginx config template
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080
