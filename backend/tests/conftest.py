"""
WHY THIS FILE EXISTS:
Sets up an isolated in-memory SQLite database for every test.
The DATABASE_URL env var must be set BEFORE any app module is imported so
pydantic-settings reads it instead of requiring a real Postgres URL.
Each test gets a fresh, empty database (autouse fixture) so tests are
fully independent — no shared state, no ordering dependency.
"""

import os

# Set DATABASE_URL before importing anything from the app
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _fresh_db():
    """Drop and recreate all tables before each test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    """FastAPI test client with the DB dependency overridden to SQLite."""

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
