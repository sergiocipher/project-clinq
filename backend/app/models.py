"""
WHY THIS FILE EXISTS:
Defines the SQLAlchemy ORM model for an Appointment.
Only portable column types are used (String, Integer, DateTime, Text)
so the same model works with both the production Postgres database and
the in-memory SQLite database used by the test suite.
Status and priority are stored as plain strings and validated in schemas.
"""

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Core fields
    patient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    doctor: Mapped[str] = mapped_column(String(200), nullable=False)
    scheduled_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status & priority — stored as plain strings, enforced by Pydantic
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="scheduled")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default="normal")

    # Audit timestamps
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_appointments_status", "status"),)
