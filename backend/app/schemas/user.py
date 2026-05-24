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
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
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

    @validator("date_of_birth")
    def make_dob_naive(cls, v):
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class AdminCreateUser(BaseModel):
    """HR Admin creates doctor or cashier accounts."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=3, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    role: str  # doctor, cashier_admin
    
    # Optional Doctor fields
    specialty_id: Optional[UUID] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    room_number: Optional[str] = None

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
        if v not in ["doctor", "cashier_admin"]:
            raise ValueError("HR Admin chỉ có thể tạo tài khoản 'doctor' hoặc 'cashier_admin'")
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
    patient_code: Optional[str] = None
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    blood_type: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None

    @validator("date_of_birth")
    def make_dob_naive(cls, v):
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Email Verification & Password Reset ──

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường")
        if not re.search(r"[0-9]", v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ số")
        return v


class VerifyEmailRequest(BaseModel):
    token: str


class MessageResponse(BaseModel):
    message: str
