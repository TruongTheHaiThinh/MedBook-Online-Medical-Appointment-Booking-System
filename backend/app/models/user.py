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
    address = Column(String(255), nullable=True)
    
    # New patient profile fields
    patient_code = Column(String(50), unique=True, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_type = Column(String(10), nullable=True)

    role = Column(String(20), nullable=False, default="patient")
    # Roles: patient, doctor, hr_admin, cashier_admin
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    appointments_as_patient = relationship(
        "Appointment", back_populates="patient", foreign_keys="Appointment.patient_id"
    )
    payments_as_cashier = relationship(
        "Payment", back_populates="cashier", foreign_keys="Payment.cashier_id"
    )
    password_history = relationship(
        "PasswordHistory", back_populates="user", cascade="all, delete-orphan"
    )
