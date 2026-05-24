"""
PasswordHistory – lưu lịch sử mật khẩu đã dùng của mỗi user.
Dùng để kiểm tra không cho phép đặt lại mật khẩu đã dùng trong 3 tháng gần nhất.
"""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PasswordHistory(Base):
    __tablename__ = "password_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship back to user (optional, for convenience)
    user = relationship("User", back_populates="password_history")
