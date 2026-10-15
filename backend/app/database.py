"""
WHY THIS FILE EXISTS:
Sets up the SQLAlchemy engine and session factory used by every route.
get_db() is a FastAPI dependency — it opens a session per request and
always closes it, even if the handler raises an exception.
Alembic (not SQLAlchemy's create_all) owns schema creation and migrations.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # re-test stale connections before using them
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields one DB session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Used by /ready to verify the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
