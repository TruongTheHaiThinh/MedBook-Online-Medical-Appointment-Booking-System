"""
AuthService – Service Layer for Authentication & Account Management.
All business logic for registration, login, email verification,
and password reset lives here. Routers only call this service.
"""
from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.doctor import Doctor
from app.schemas.user import (
    UserRegister, AdminCreateUser, UserLogin,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_verification_token, decode_token,
)
from app.core.email import send_verify_email, send_reset_password_email
from app.config import settings


class AuthService:
    """Stateless service – every method receives `db` session explicitly."""

    # ── Registration (Patient / Doctor self-signup) ──

    @staticmethod
    async def register(data: UserRegister, db: AsyncSession, background_tasks: BackgroundTasks) -> User:
        # Check phone unique
        result_p = await db.execute(select(User).where(User.phone == data.phone))
        if result_p.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng")

        # Check email unique
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
            is_verified=False,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_type=data.blood_type,
        )
        db.add(user)
        await db.flush()

        # If doctor role, create doctor profile (requires HR admin approval)
        if data.role == "doctor":
            doctor = Doctor(user_id=user.id, is_approved=False)
            db.add(doctor)

        await db.commit()
        await db.refresh(user)

        # Send verification email in background
        if data.email:
            token = create_verification_token(str(user.id), purpose="verify_email")
            background_tasks.add_task(send_verify_email, data.email, data.full_name, token)

        return user

    # ── Admin creates Doctor / Cashier accounts ──

    @staticmethod
    async def admin_create_user(data: AdminCreateUser, db: AsyncSession, background_tasks: BackgroundTasks) -> User:
        # Check email unique
        result_e = await db.execute(select(User).where(User.email == data.email))
        if result_e.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

        # Check phone unique
        result_p = await db.execute(select(User).where(User.phone == data.phone))
        if result_p.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
            role=data.role,
            is_verified=True,  # Admin-created accounts are pre-verified
        )
        db.add(user)
        await db.flush()

        # If doctor role, create doctor profile (pre-approved by admin)
        if data.role == "doctor":
            doctor = Doctor(user_id=user.id, is_approved=True)
            db.add(doctor)

        await db.commit()
        await db.refresh(user)
        return user

    # ── Login ──

    @staticmethod
    async def login(data: UserLogin, db: AsyncSession) -> dict:
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
                detail="Số điện thoại/Email hoặc mật khẩu không đúng",
            )

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {"access_token": access_token, "token_type": "bearer", "user": user}

    # ── Email Verification ──

    @staticmethod
    async def verify_email(token: str, db: AsyncSession) -> dict:
        payload = decode_token(token)
        purpose = payload.get("purpose")
        user_id = payload.get("sub")

        if purpose != "verify_email" or not user_id:
            raise HTTPException(status_code=400, detail="Token xác thực không hợp lệ")

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        if user.is_verified:
            return {"message": "Tài khoản đã được xác thực trước đó"}

        user.is_verified = True
        await db.commit()
        return {"message": "Xác thực email thành công! Bạn có thể đăng nhập ngay bây giờ."}

    # ── Forgot Password ──

    @staticmethod
    async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession, background_tasks: BackgroundTasks) -> dict:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        # Always return success to prevent email enumeration
        if not user:
            return {"message": "Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu."}

        token = create_verification_token(str(user.id), purpose="reset_password")
        background_tasks.add_task(send_reset_password_email, user.email, user.full_name, token)

        return {"message": "Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu."}

    # ── Reset Password ──

    @staticmethod
    async def reset_password(data: ResetPasswordRequest, db: AsyncSession) -> dict:
        payload = decode_token(data.token)
        purpose = payload.get("purpose")
        user_id = payload.get("sub")

        if purpose != "reset_password" or not user_id:
            raise HTTPException(status_code=400, detail="Token đặt lại mật khẩu không hợp lệ")

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        user.password_hash = hash_password(data.new_password)
        await db.commit()
        return {"message": "Đặt lại mật khẩu thành công! Bạn có thể đăng nhập với mật khẩu mới."}

    # ── Resend Verification Email ──

    @staticmethod
    async def resend_verification(user: User, background_tasks: BackgroundTasks) -> dict:
        if user.is_verified:
            return {"message": "Tài khoản đã được xác thực"}

        if not user.email:
            raise HTTPException(status_code=400, detail="Tài khoản chưa có email để xác thực")

        token = create_verification_token(str(user.id), purpose="verify_email")
        background_tasks.add_task(send_verify_email, user.email, user.full_name, token)
        return {"message": "Email xác thực đã được gửi lại thành công."}
