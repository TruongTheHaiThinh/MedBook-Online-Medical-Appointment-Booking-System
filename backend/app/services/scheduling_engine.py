import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schedule import Schedule
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.schemas.schedule import AvailableSlot


class SchedulingEngine:
    """
    Smart Scheduling Engine:
    Generates available slots on-demand from doctor's weekly schedule pattern,
    minus already-booked appointments. No pre-generated slots stored in DB.
    """

    def __init__(self, db: AsyncSession):
        self.schedule_repo = ScheduleRepository(db)
        self.appointment_repo = AppointmentRepository(db)

    async def get_available_slots(
        self, doctor_id, query_date: datetime.date
    ) -> list[AvailableSlot]:
        # 0=Monday ... 6=Sunday (Python's weekday())
        day_of_week = query_date.weekday()

        schedule = await self.schedule_repo.get_by_doctor_and_day(doctor_id, day_of_week)
        if not schedule:
            return []  # Doctor doesn't work on this day

        # Generate all possible slots from pattern
        all_slots = self._generate_slots(schedule, query_date)

        # Get already booked times
        booked_times = await self.appointment_repo.get_booked_times_for_doctor_date(
            doctor_id, query_date
        )
        booked_set = set(booked_times)

        # Filter out booked slots — also cap at max_slots
        available = [s for s in all_slots if s not in booked_set]

        # Build response
        return [
            AvailableSlot(
                time=slot,
                datetime_iso=datetime.datetime.combine(query_date, slot).isoformat(),
            )
            for slot in available
        ]

    def _generate_slots(
        self, schedule: Schedule, query_date: datetime.date
    ) -> list[datetime.time]:
        """Generate list of time slots from a schedule pattern."""
        slots = []
        current = datetime.datetime.combine(query_date, schedule.start_time)
        end = datetime.datetime.combine(query_date, schedule.end_time)
        delta = datetime.timedelta(minutes=schedule.slot_duration_min)

        while current + delta <= end and len(slots) < schedule.max_slots:
            slots.append(current.time())
            current += delta

        return slots
