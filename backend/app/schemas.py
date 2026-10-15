"""
WHY THIS FILE EXISTS:
Pydantic schemas separate the API contract from the database model.
- AppointmentCreate: fields required to book a new appointment.
- AppointmentUpdate: every field optional so callers can PATCH a single field.
- AppointmentRead: what the API sends back; from_attributes lets Pydantic read
  values straight from SQLAlchemy ORM objects.
- Stats: aggregated counts returned by the /stats endpoint.
"""

from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

StatusValue = Literal["scheduled", "completed", "cancelled"]
PriorityValue = Literal["low", "normal", "urgent"]


class AppointmentCreate(BaseModel):
    patient_name: Annotated[str, Field(min_length=1, max_length=200)]
    doctor: Annotated[str, Field(min_length=1, max_length=200)]
    scheduled_at: datetime
    notes: Optional[str] = None
    status: StatusValue = "scheduled"
    priority: PriorityValue = "normal"


class AppointmentUpdate(BaseModel):
    """All fields optional — apply with exclude_unset=True for partial updates."""

    patient_name: Optional[Annotated[str, Field(min_length=1, max_length=200)]] = None
    doctor: Optional[Annotated[str, Field(min_length=1, max_length=200)]] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[StatusValue] = None
    priority: Optional[PriorityValue] = None


class AppointmentRead(BaseModel):
    id: int
    patient_name: str
    doctor: str
    scheduled_at: datetime
    notes: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Stats(BaseModel):
    total: int
    by_status: dict[str, int]
    upcoming_count: int  # domain-relevant extra: appointments still 'scheduled'
