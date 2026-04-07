import uuid
from typing import Optional
from pydantic import BaseModel, field_validator
from app.schemas.specialty import SpecialtyResponse


class DoctorUpdateProfile(BaseModel):
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    specialty_id: Optional[uuid.UUID] = None

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 1000:
            raise ValueError("Bio must not exceed 1000 characters")
        return v

    @field_validator("experience_years")
    @classmethod
    def validate_experience(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Experience years must be a non-negative number")
        return v


class DoctorResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    specialty_id: Optional[uuid.UUID]
    bio: Optional[str]
    experience_years: int
    is_approved: bool
    specialty: Optional[SpecialtyResponse] = None
    full_name: Optional[str] = None  # Populated from joined user

    model_config = {"from_attributes": True}


class DoctorPublicResponse(BaseModel):
    """Public-facing doctor info (no sensitive data)."""
    id: uuid.UUID
    full_name: str
    specialty: Optional[SpecialtyResponse]
    experience_years: int
    bio: Optional[str]

    model_config = {"from_attributes": True}
