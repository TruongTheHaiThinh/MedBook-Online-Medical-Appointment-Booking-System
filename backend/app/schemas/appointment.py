import uuid
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: uuid.UUID
    scheduled_date: datetime.date
    scheduled_time: datetime.time
    reason: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError("Reason must not exceed 500 characters")
        return v

    @field_validator("scheduled_date")
    @classmethod
    def validate_date_not_past(cls, v: datetime.date) -> datetime.date:
        if v < datetime.date.today():
            raise ValueError("Appointment date cannot be in the past")
        return v


class AppointmentConfirm(BaseModel):
    """Doctor confirms or rejects a pending appointment."""
    pass  # No extra body needed for CONFIRM


class AppointmentCancel(BaseModel):
    """Doctor cancels with mandatory notes; patient cancel has no required notes."""
    doctor_notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    scheduled_date: datetime.date
    scheduled_time: datetime.time
    reason: Optional[str]
    status: AppointmentStatus
    doctor_notes: Optional[str]
    reminder_sent: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class PaginatedAppointments(BaseModel):
    items: list[AppointmentResponse]
    total: int
    page: int
    size: int
    pages: int
