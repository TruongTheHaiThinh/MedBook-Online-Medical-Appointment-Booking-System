from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PrescriptionItemBase(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    morning: float = 0
    noon: float = 0
    afternoon: float = 0
    evening: float = 0
    total_quantity: int = 0
    instructions: Optional[str] = None

class PrescriptionItemCreate(PrescriptionItemBase):
    pass

class PrescriptionItemResponse(PrescriptionItemBase):
    id: UUID

class PrescriptionBase(BaseModel):
    diagnosis: Optional[str] = None
    advice: Optional[str] = None
    patient_age: Optional[int] = None
    patient_weight: Optional[float] = None
    patient_height: Optional[float] = None
    patient_address: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    appointment_id: UUID
    items: List[PrescriptionItemCreate]

class PrescriptionResponse(PrescriptionBase):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    created_at: datetime
    items: List[PrescriptionItemResponse]

    class Config:
        from_attributes = True

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
