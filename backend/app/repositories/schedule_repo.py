import uuid
import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schedule import Schedule


class ScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_doctor(self, doctor_id: uuid.UUID) -> list[Schedule]:
        result = await self.db.execute(
            select(Schedule).where(Schedule.doctor_id == doctor_id)
        )
        return result.scalars().all()

    async def get_by_doctor_and_day(
        self, doctor_id: uuid.UUID, day_of_week: int
    ) -> Optional[Schedule]:
        result = await self.db.execute(
            select(Schedule).where(
                Schedule.doctor_id == doctor_id,
                Schedule.day_of_week == day_of_week,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, doctor_id: uuid.UUID, **kwargs) -> Schedule:
        schedule = Schedule(doctor_id=doctor_id, **kwargs)
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def update(self, schedule: Schedule, **kwargs) -> Schedule:
        for key, value in kwargs.items():
            if value is not None:
                setattr(schedule, key, value)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def delete(self, schedule: Schedule) -> None:
        await self.db.delete(schedule)
        await self.db.commit()
