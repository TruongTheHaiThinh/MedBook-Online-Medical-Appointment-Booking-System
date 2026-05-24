"""
AuthService – Service Layer for Authentication & Account Management.
All business logic for registration, login, email verification,
and password reset lives here. Routers only call this service.
"""
from datetime import timedelta, datetime
from uuid import UUID

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.doctor import Doctor
from app.models.password_history import PasswordHistory
from app.schemas.user import (
    UserRegister, AdminCreateUser, UserLogin,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_verification_token, decode_token, decode_reset_token,
)
from app.core.email import send_verify_email, send_reset_password_email
from app.config import settings


async def _generate_next_patient_code(db: AsyncSession) -> str:
    # Query all patient codes that start with "MB-"
    result = await db.execute(
        select(User.patient_code).where(User.patient_code.like("MB-%"))
    )
    codes = result.scalars().all()
    max_num = 0
    for code in codes:
        if code:
            try:
                # Extract number from "MB-XXX" (e.g. MB-001 -> 1)
                parts = code.split("-")
                if len(parts) == 2:
                    num = int(parts[1])
                    if num > max_num:
                        max_num = num
            except ValueError:
                pass
    next_num = max_num + 1
    return f"MB-{next_num:03d}"


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

        p_code = None
        if data.role == "patient":
            p_code = await _generate_next_patient_code(db)

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
            patient_code=p_code,
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

        p_code = None
        if data.role == "patient":
            p_code = await _generate_next_patient_code(db)

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
            role=data.role,
            is_verified=True,  # Admin-created accounts are pre-verified
            patient_code=p_code,
        )
        db.add(user)
        await db.flush()

        # If doctor role, create doctor profile (pre-approved by admin)
        if data.role == "doctor":
            doctor = Doctor(
                user_id=user.id,
                is_approved=True,
                specialty_id=data.specialty_id,
                experience_years=data.experience_years,
                bio=data.bio,
                room_number=data.room_number,
            )
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

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy tài khoản",
            )

        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai mật khẩu, vui lòng thử lại",
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
        payload = decode_reset_token(token)  # dung 400 thay vi 401
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

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email không tồn tại trên hệ thống",
            )

        token = create_verification_token(str(user.id), purpose="reset_password")
        background_tasks.add_task(send_reset_password_email, user.email, user.full_name, token)

        return {"message": "Đã gửi link đặt lại mật khẩu thành công!"}

    # ── Reset Password ──

    @staticmethod
    async def reset_password(data: ResetPasswordRequest, db: AsyncSession) -> dict:
        payload = decode_reset_token(data.token)  # dung 400 thay vi 401, tranh redirect login
        purpose = payload.get("purpose")
        user_id = payload.get("sub")

        if purpose != "reset_password" or not user_id:
            raise HTTPException(status_code=400, detail="Token đặt lại mật khẩu không hợp lệ")

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        # ── Kiem tra lich su mat khau (3 thang gan nhat) ──
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        history_result = await db.execute(
            select(PasswordHistory)
            .where(
                PasswordHistory.user_id == user.id,
                PasswordHistory.created_at >= three_months_ago,
            )
            .order_by(PasswordHistory.created_at.desc())
        )
        recent_history = history_result.scalars().all()

        # Kiểm tra với mật khẩu hiện tại
        if verify_password(data.new_password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Mật khẩu mới không được trùng với mật khẩu hiện tại",
            )

        # Kiểm tra với lịch sử mật khẩu trong 3 tháng
        for record in recent_history:
            if verify_password(data.new_password, record.password_hash):
                raise HTTPException(
                    status_code=400,
                    detail="Mật khẩu mới không được trùng với mật khẩu đã dùng trong 3 tháng gần nhất",
                )

        # Luu mat khau cu vao lich su truoc khi cap nhat
        history_entry = PasswordHistory(
            user_id=user.id,
            password_hash=user.password_hash,  # luu hash mat khau hien tai
        )
        db.add(history_entry)

        # Cập nhật mật khẩu mới
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
