from typing import Optional
from uuid import UUID
from datetime import date, time, datetime
from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    doctor_id: UUID
    scheduled_date: date
    scheduled_time: time
    reason: Optional[str] = Field(None, max_length=500)


class AppointmentConfirm(BaseModel):
    doctor_notes: Optional[str] = None


class AppointmentCancel(BaseModel):
    doctor_notes: str = Field(..., min_length=1, description="Lý do hủy lịch (bắt buộc)")


class AppointmentComplete(BaseModel):
    doctor_notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_date: date
    scheduled_time: time
    reason: Optional[str]
    status: str
    doctor_notes: Optional[str]
    reminder_sent: bool
    created_at: datetime
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    specialty_name: Optional[str] = None

    class Config:
        from_attributes = True
