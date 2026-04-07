import uuid
from sqlalchemy import Integer, Time, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import datetime


class Schedule(Base):
    """
    Weekly recurring schedule pattern for a doctor.
    day_of_week: 0=Monday ... 6=Sunday
    """
    __tablename__ = "schedules"
    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="chk_day_of_week"),
        CheckConstraint("start_time < end_time", name="chk_schedule_time_order"),
        CheckConstraint("slot_duration_min > 0", name="chk_slot_duration_positive"),
        CheckConstraint("max_slots >= 1", name="chk_max_slots_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    slot_duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    max_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=8)

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
