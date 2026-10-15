"""
WHY THIS FILE EXISTS:
All CRUD endpoints for the Appointment resource live here.
The router is mounted at /api/appointments in main.py.
Note: /stats is declared BEFORE /{id} — if it came after, FastAPI would try
to parse the string "stats" as an integer and return a 422 error.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment
from app.schemas import AppointmentCreate, AppointmentRead, AppointmentUpdate, Stats

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

STATUS_VALUES = ["scheduled", "completed", "cancelled"]


@router.get("/stats", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    """Aggregate counts — used by the dashboard KPI cards."""
    total = db.scalar(select(func.count()).select_from(Appointment)) or 0

    # Count per status, ensuring every status appears (even with zero)
    rows = db.execute(
        select(Appointment.status, func.count()).group_by(Appointment.status)
    ).all()
    by_status = {s: 0 for s in STATUS_VALUES}
    for s, cnt in rows:
        by_status[s] = cnt

    upcoming_count = by_status.get("scheduled", 0)

    return Stats(total=total, by_status=by_status, upcoming_count=upcoming_count)


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search patient name or doctor"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List appointments, newest first. Supports status filter and text search."""
    stmt = select(Appointment).order_by(Appointment.created_at.desc())
    if status:
        stmt = stmt.where(Appointment.status == status)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            Appointment.patient_name.ilike(pattern) | Appointment.doctor.ilike(pattern)
        )
    stmt = stmt.offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(body: AppointmentCreate, db: Session = Depends(get_db)):
    appt = Appointment(**body.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.put("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int, body: AppointmentUpdate, db: Session = Depends(get_db)
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return appt


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()
