import uuid
from sqlalchemy import Column, String, Text, Date, Time, Boolean, DateTime, ForeignKey, func, Numeric, Integer
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
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    # PENDING -> CONFIRMED -> IN_PROGRESS -> PRESCRIPTION_SENT -> COMPLETED
    # PENDING/CONFIRMED -> CANCELLED
    is_revisit = Column(Boolean, default=False, nullable=False)
    qr_code = Column(String(255), unique=True, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    queue_number = Column(Integer, nullable=True)
    room_number = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", back_populates="appointments_as_patient", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments", foreign_keys=[doctor_id])
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False, cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="appointment", uselist=False, cascade="all, delete-orphan")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    diagnosis = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    revisit_date = Column(Date, nullable=True)
    revisit_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointment = relationship("Appointment", back_populates="medical_record")
    prescriptions = relationship("PrescriptionItem", back_populates="medical_record", cascade="all, delete-orphan")
    doctor = relationship("Doctor", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    dosage = Column(String(255), nullable=True)
    frequency = Column(String(255), nullable=True)
    duration = Column(String(255), nullable=True)
    morning = Column(Numeric(5, 1), default=0)
    noon = Column(Numeric(5, 1), default=0)
    afternoon = Column(Numeric(5, 1), default=0)
    evening = Column(Numeric(5, 1), default=0)
    total_quantity = Column(Numeric(10, 1), default=0)
    instructions = Column(Text, nullable=True)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="prescriptions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True)
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False, default=0)
    payment_method = Column(String(50), nullable=True, default="cash")
    status = Column(String(20), nullable=False, default="PENDING")
    # PENDING, PAID
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    appointment = relationship("Appointment", back_populates="payment")
    cashier = relationship("User", back_populates="payments_as_cashier", foreign_keys=[cashier_id])
