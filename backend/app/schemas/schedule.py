import uuid
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ScheduleCreate(BaseModel):
    day_of_week: int  # 0=Mon ... 6=Sun
    start_time: datetime.time
    end_time: datetime.time
    slot_duration_min: int = 30
    max_slots: int = 8

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, v: int) -> int:
        if not (0 <= v <= 6):
            raise ValueError("day_of_week must be between 0 (Monday) and 6 (Sunday)")
        return v

    @field_validator("slot_duration_min")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("slot_duration_min must be positive")
        return v

    @field_validator("max_slots")
    @classmethod
    def validate_max_slots(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_slots must be at least 1")
        return v


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: datetime.time
    end_time: datetime.time
    slot_duration_min: int
    max_slots: int

    model_config = {"from_attributes": True}


class AvailableSlot(BaseModel):
    """A single available time slot returned from the scheduling engine."""
    time: datetime.time
    datetime_iso: str  # ISO string for easier frontend use
