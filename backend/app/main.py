"""
WHY THIS FILE EXISTS:
The FastAPI application entry point. It wires together middleware, the
Prometheus instrumentator, and all route modules.
Schema creation is intentionally NOT done here — Alembic manages migrations
so the database is never silently out of sync with the codebase.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import check_db_connection
from app.routes.appointments import router as appointments_router

app = FastAPI(
    title="project-clinq",
    description="Clinic Appointment Booking API",
    version=settings.app_version,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus metrics ────────────────────────────────────────────────────────
# Probes are excluded so Grafana shows real user traffic, not noise from k8s.
Instrumentator(
    excluded_handlers=["/metrics", "/health", "/ready"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(appointments_router)


# ── System endpoints ──────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "project-clinq",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["ops"])
def health():
    """Liveness probe — returns 200 as long as the process is alive."""
    return {"status": "ok"}


@app.get("/ready", tags=["ops"])
def ready():
    """
    Readiness probe — runs SELECT 1 to confirm the database is reachable.
    Returns 503 when the DB is down so Kubernetes stops routing traffic here.
    """
    from fastapi import Response

    if check_db_connection():
        return {"status": "READY"}
    return Response(
        content='{"status":"NOT_READY"}',
        status_code=503,
        media_type="application/json",
    )
