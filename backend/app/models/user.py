import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    address = Column(String(255), nullable=True) # Will make required in schema
    role = Column(String(20), nullable=False, default="patient")  # patient, doctor, admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    appointments_as_patient = relationship(
        "Appointment", back_populates="patient", foreign_keys="Appointment.patient_id"
    )
