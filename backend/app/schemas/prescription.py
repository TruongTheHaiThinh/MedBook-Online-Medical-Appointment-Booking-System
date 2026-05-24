# ── DEPRECATED ──
# Prescription schemas have been moved to app/schemas/appointment.py
# This file is kept for backward compatibility.
from app.schemas.appointment import (
    PrescriptionItemCreate,
    PrescriptionItemResponse,
    MedicalRecordCreate,
    MedicalRecordResponse,
)

# Legacy aliases
PrescriptionItemBase = PrescriptionItemCreate

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MedicineResponse(BaseModel):
    id: UUID
    name: str
    category: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    indication: Optional[str] = None
    classification: Optional[str] = None

    class Config:
        from_attributes = True
