# WHY THIS FILE EXISTS:
# Packages the FastAPI backend as a minimal, non-root Docker image.
# - python:3.12-slim keeps the attack surface small (fewer OS packages = fewer CVEs).
# - We copy requirements.txt first so pip runs only when dependencies change,
#   not on every source-code edit (Docker layer caching).
# - A dedicated non-root user (UID 10001) means a compromised process cannot
#   write to system directories or escalate privileges in the container.
# - start.sh runs Alembic migrations before Uvicorn so the schema is always
#   up to date without a separate migration job.

FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered stdout/stderr for clean logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Dependencies (cached layer) ───────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application source ────────────────────────────────────────────────────────
# Note: alembic/ must be copied separately so Docker preserves it as a
# subdirectory at /app/alembic/. Mixing it with other sources in one COPY
# causes Docker to flatten its contents directly into /app/.
COPY alembic.ini start.sh ./
COPY alembic/ ./alembic/
COPY app/ ./app/

# Build-time version label (CI passes the git SHA)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# OCI source label — links the image back to the repository on GHCR
LABEL org.opencontainers.image.source="https://github.com/sergiocipher/project-clinq"

# ── Non-root user (numeric UID required for Kubernetes runAsNonRoot) ──────────
RUN groupadd -g 10001 app && \
    useradd -u 10001 -g app -M -s /usr/sbin/nologin app && \
    chmod +x /app/start.sh

USER 10001

EXPOSE 8000

CMD ["sh", "/app/start.sh"]
