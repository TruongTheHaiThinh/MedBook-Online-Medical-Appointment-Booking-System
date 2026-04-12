import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id", ondelete="SET NULL"), nullable=True)
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    specialty = relationship("Specialty", back_populates="doctors")
    schedules = relationship("Schedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship(
        "Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id"
    )
    leave_requests = relationship("LeaveRequest", back_populates="doctor", cascade="all, delete-orphan")
