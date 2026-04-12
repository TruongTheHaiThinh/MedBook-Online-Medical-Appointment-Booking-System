import uuid
from sqlalchemy import Column, String, Text, Date, Time, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    # PENDING -> CONFIRMED -> COMPLETED
    # PENDING/CONFIRMED -> CANCELLED
    doctor_notes = Column(Text, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", back_populates="appointments_as_patient", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments", foreign_keys=[doctor_id])
