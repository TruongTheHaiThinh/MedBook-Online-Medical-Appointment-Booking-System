import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    
    diagnosis = Column(Text, nullable=True)
    advice = Column(Text, nullable=True)
    
    # Clinical info entered by doctor
    patient_age = Column(Integer, nullable=True)
    patient_weight = Column(Float, nullable=True)
    patient_height = Column(Float, nullable=True)
    patient_address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointment = relationship("Appointment", backref="prescription")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    dosage = Column(String(255))  # e.g., "1 tablet"
    frequency = Column(String(255))  # e.g., "3 times a day"
    duration = Column(String(255))  # e.g., "7 days"
    morning = Column(Float, default=0)
    noon = Column(Float, default=0)
    afternoon = Column(Float, default=0)
    evening = Column(Float, default=0)
    total_quantity = Column(Integer, default=0)
    instructions = Column(Text)  # e.g., "Before meal"

    prescription = relationship("Prescription", back_populates="items")
