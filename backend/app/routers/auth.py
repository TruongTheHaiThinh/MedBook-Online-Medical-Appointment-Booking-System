"""
Auth Router – Thin layer that delegates all logic to AuthService.
Endpoints: register, login, verify-email, forgot/reset password, me.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse, UserUpdate, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, MessageResponse,
)
from app.core.security import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Đăng ký tài khoản mới (patient hoặc doctor). Gửi email xác thực nếu có email."""
    return await AuthService.register(data, db, background_tasks)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Đăng nhập bằng email/SĐT và nhận JWT token."""
    return await AuthService.login(data, db)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    """Xác thực email qua token từ link trong email."""
    return await AuthService.verify_email(data.token, db)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Gửi link đặt lại mật khẩu qua email."""
    return await AuthService.forgot_password(data, db, background_tasks)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Đặt lại mật khẩu bằng token từ email."""
    return await AuthService.reset_password(data, db)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Gửi lại email xác thực (yêu cầu đã đăng nhập)."""
    return await AuthService.resend_verification(current_user, background_tasks)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin người dùng hiện tại."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cập nhật thông tin cá nhân."""
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.phone is not None:
        current_user.phone = data.phone
    if data.address is not None:
        current_user.address = data.address
    if data.date_of_birth is not None:
        current_user.date_of_birth = data.date_of_birth
    if data.gender is not None:
        current_user.gender = data.gender
    if data.blood_type is not None:
        current_user.blood_type = data.blood_type
        
    await db.commit()
    await db.refresh(current_user)
    return current_user
