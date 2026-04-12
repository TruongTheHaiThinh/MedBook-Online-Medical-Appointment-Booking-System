from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.schemas.user import UserRegister, UserLogin, UserResponse, UserUpdate, TokenResponse
from app.core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Đăng ký tài khoản mới (patient hoặc doctor)"""
    # Check phone unique (Required)
    result_p = await db.execute(select(User).where(User.phone == data.phone))
    if result_p.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng")

    # Check email unique (Optional)
    if data.email:
        result_e = await db.execute(select(User).where(User.email == data.email))
        if result_e.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        address=data.address,
        role=data.role,
    )
    db.add(user)
    await db.flush()

    # If doctor role, create doctor profile (requires admin approval)
    if data.role == "doctor":
        doctor = Doctor(user_id=user.id, is_approved=False)
        db.add(doctor)

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Đăng nhập và nhận JWT token"""
    # Login with phone or email
    login_id = data.identifier or data.email
    if not login_id:
        raise HTTPException(status_code=422, detail="Vui lòng nhập Email hoặc Số điện thoại")

    result = await db.execute(
        select(User).where((User.email == login_id) | (User.phone == login_id))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại/Email hoặc mật khẩu không đúng"
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin người dùng hiện tại"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật thông tin cá nhân"""
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.phone is not None:
        current_user.phone = data.phone
    await db.commit()
    await db.refresh(current_user)
    return current_user
