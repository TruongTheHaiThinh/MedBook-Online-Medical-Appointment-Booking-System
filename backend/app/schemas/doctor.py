from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


class SpecialtyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class SpecialtyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


class SpecialtyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class DoctorProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    specialty_id: Optional[UUID]
    bio: Optional[str]
    experience_years: int
    avatar_url: Optional[str] = None
    is_approved: bool
    full_name: str
    email: str
    specialty_name: Optional[str] = None

    class Config:
        from_attributes = True


class DoctorProfileUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    experience_years: Optional[int] = Field(None, ge=0)
    specialty_id: Optional[UUID] = None


class LeaveRequestCreate(BaseModel):
    leave_date: date
    reason: Optional[str] = Field(None, max_length=500)


class LeaveRequestResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    leave_date: date
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
