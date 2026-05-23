from typing import Optional, List
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


class AppointmentStatsResponse(BaseModel):
    total_today: int
    pending_approval: int
    waiting_checkin: int
    waiting_payment: int
    completed_today: int
    revenue_today: float
    success_rate: float
    cancel_rate: float


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    scheduled_date: date
    scheduled_time: time
    reason: Optional[str]
    status: str
    is_revisit: bool
    qr_code: Optional[str]
    doctor_notes: Optional[str]
    reminder_sent: bool
    created_at: datetime
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_code: Optional[str] = None
    patient_address: Optional[str] = None
    patient_dob: Optional[date] = None
    patient_gender: Optional[str] = None
    patient_blood_type: Optional[str] = None
    doctor_name: Optional[str] = None
    specialty_name: Optional[str] = None
    queue_number: Optional[int] = None
    room_number: Optional[str] = None
    payment_amount: float = 0
    payment_status: str = "PENDING"

    class Config:
        from_attributes = True


# ── Medical Records ──

class MedicalRecordCreate(BaseModel):
    appointment_id: UUID
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    revisit_required: bool = False
    revisit_date: Optional[date] = None
    prescriptions: List["PrescriptionItemCreate"] = []
    is_final: bool = True


class MedicalRecordResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    diagnosis: Optional[str]
    notes: Optional[str]
    revisit_date: Optional[date]
    revisit_required: bool
    created_at: datetime
    doctor_name: Optional[str] = None
    prescriptions: List["PrescriptionItemResponse"] = []

    class Config:
        from_attributes = True


# ── Prescription Items ──

class PrescriptionItemCreate(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    morning: float = 0
    noon: float = 0
    afternoon: float = 0
    evening: float = 0
    total_quantity: float = 0
    instructions: Optional[str] = None


class PrescriptionItemResponse(PrescriptionItemCreate):
    id: UUID

    class Config:
        from_attributes = True


# ── Payments ──

class PaymentCreate(BaseModel):
    appointment_id: UUID
    amount: float
    payment_method: str = "cash"


class PaymentResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    cashier_id: Optional[UUID]
    amount: float
    payment_method: Optional[str]
    status: str
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


# Rebuild forward refs
MedicalRecordCreate.model_rebuild()
MedicalRecordResponse.model_rebuild()
