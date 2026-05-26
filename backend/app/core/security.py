import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_verification_token(user_id: str, purpose: str = "verify_email") -> str:
    """Create a token for email verification or password reset."""
    if purpose == "verify_email":
        expire_delta = timedelta(hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS)
    elif purpose == "reset_password":
        expire_delta = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    else:
        expire_delta = timedelta(hours=1)

    data = {"sub": user_id, "purpose": purpose}
    return create_access_token(data, expires_delta=expire_delta)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_reset_token(token: str) -> dict:
    """Decode token dùng cho reset/verify email. Trả 400 thay vì 401
    để tránh frontend bị redirect về trang đăng nhập."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn (15 phút). Vui lòng yêu cầu lại.",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return user


# ── Class-based RBAC Dependency ──
class RoleChecker:
    """
    Usage:
        require_hr = RoleChecker(["hr_admin"])
        require_medical = RoleChecker(["doctor", "hr_admin"])

    In router:
        current_user = Depends(RoleChecker(["hr_admin", "cashier_admin"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user=Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền truy cập. Yêu cầu vai trò: {', '.join(self.allowed_roles)}"
            )
        return current_user


# ── Convenience shortcuts (backward-compatible) ──
require_patient = RoleChecker(["patient"])
require_doctor = RoleChecker(["doctor"])
require_hr_admin = RoleChecker(["hr_admin"])
require_cashier_admin = RoleChecker(["cashier_admin"])
require_any_admin = RoleChecker(["hr_admin", "cashier_admin"])
require_admin = RoleChecker(["hr_admin"])  # backward compat: old "admin" → hr_admin
