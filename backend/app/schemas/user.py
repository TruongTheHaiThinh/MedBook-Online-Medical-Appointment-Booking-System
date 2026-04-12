import re
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, validator, Field


class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5, max_length=255)
    role: str = "patient"  # patient, doctor

    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường")
        if not re.search(r"[0-9]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ số")
        return v

    @validator("role")
    def role_must_be_valid(cls, v):
        if v not in ["patient", "doctor"]:
            raise ValueError("Role phải là 'patient' hoặc 'doctor'")
        return v


class UserLogin(BaseModel):
    identifier: Optional[str] = None
    email: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: Optional[str]
    full_name: str
    phone: str
    address: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
