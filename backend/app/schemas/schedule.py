from typing import Optional, List
from uuid import UUID
from datetime import time, date
from pydantic import BaseModel, Field, validator, root_validator


class ScheduleCreate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=Sunday, 1=Monday,...,6=Saturday
    specific_date: Optional[date] = None  # YYYY-MM-DD
    start_time: time
    end_time: time
    slot_duration_min: int = Field(30, ge=10, le=120)
    max_slots: int = Field(8, ge=1)

    @root_validator(skip_on_failure=True)
    def check_schedule_data(cls, values):
        start = values.get("start_time")
        end = values.get("end_time")
        dow = values.get("day_of_week")
        spec = values.get("specific_date")

        if start and end and end <= start:
            raise ValueError("Giờ kết thúc phải sau giờ bắt đầu")
        
        if dow is None and spec is None:
            raise ValueError("Vui lòng cung cấp Thứ (day_of_week) hoặc Ngày cụ thể (specific_date)")
            
        return values


class ScheduleResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    day_of_week: Optional[int]
    specific_date: Optional[date]
    start_time: time
    end_time: time
    slot_duration_min: int
    max_slots: int

    class Config:
        from_attributes = True


class AvailableSlot(BaseModel):
    time: str
    is_available: bool


class AvailableSlotsResponse(BaseModel):
    doctor_id: UUID
    date: str
    slots: List[str]
