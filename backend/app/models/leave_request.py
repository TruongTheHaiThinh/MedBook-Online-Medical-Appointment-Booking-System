import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    leave_date = Column(Date, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="APPROVED") # Auto-approved for now based on user's suggestion of "tick X"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("Doctor", back_populates="leave_requests")
