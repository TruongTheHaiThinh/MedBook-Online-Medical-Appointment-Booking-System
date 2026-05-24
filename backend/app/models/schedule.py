import uuid
from sqlalchemy import Column, Integer, Time, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=True)  # 0=Sunday, 1=Monday, ..., 6=Saturday
    specific_date = Column(Date, nullable=True)  # YYYY-MM-DD for one-off schedule
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_min = Column(Integer, nullable=False, default=30)
    max_slots = Column(Integer, nullable=False, default=8)

    doctor = relationship("Doctor", back_populates="schedules")
