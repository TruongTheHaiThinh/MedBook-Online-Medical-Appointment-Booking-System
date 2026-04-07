import uuid
from typing import Optional
from pydantic import BaseModel


class SpecialtyCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SpecialtyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SpecialtyResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]

    model_config = {"from_attributes": True}
