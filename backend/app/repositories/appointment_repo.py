import uuid
import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.appointment import Appointment, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .options(selectinload(Appointment.patient), selectinload(Appointment.doctor))
            .where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_booked_times_for_slot(
        self,
        doctor_id: uuid.UUID,
        scheduled_date: datetime.date,
        scheduled_time: datetime.time,
    ) -> list[Appointment]:
        """Used for race condition check — get all active appointments for a specific slot."""
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_date == scheduled_date,
                Appointment.scheduled_time == scheduled_time,
                Appointment.status.in_(
                    [AppointmentStatus.pending, AppointmentStatus.confirmed]
                ),
            )
        )
        return result.scalars().all()

    async def get_booked_times_for_doctor_date(
        self, doctor_id: uuid.UUID, scheduled_date: datetime.date
    ) -> list[datetime.time]:
        """Return all booked times for a doctor on a given date (for slot generation)."""
        result = await self.db.execute(
            select(Appointment.scheduled_time).where(
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_date == scheduled_date,
                Appointment.status.in_(
                    [AppointmentStatus.pending, AppointmentStatus.confirmed]
                ),
            )
        )
        return result.scalars().all()

    async def check_patient_conflict(
        self,
        patient_id: uuid.UUID,
        scheduled_date: datetime.date,
        scheduled_time: datetime.time,
    ) -> bool:
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.patient_id == patient_id,
                Appointment.scheduled_date == scheduled_date,
                Appointment.scheduled_time == scheduled_time,
                Appointment.status.in_(
                    [AppointmentStatus.pending, AppointmentStatus.confirmed]
                ),
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, **kwargs) -> Appointment:
        appointment = Appointment(**kwargs)
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def update(self, appointment: Appointment, **kwargs) -> Appointment:
        for key, value in kwargs.items():
            setattr(appointment, key, value)
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def list_for_patient(
        self, patient_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> tuple[list[Appointment], int]:
        query = (
            select(Appointment)
            .options(selectinload(Appointment.doctor))
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.scheduled_date.desc())
        )
        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())
        offset = (page - 1) * size
        paginated = await self.db.execute(query.offset(offset).limit(size))
        return paginated.scalars().all(), total

    async def list_for_doctor(
        self,
        doctor_id: uuid.UUID,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Appointment], int]:
        query = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .where(Appointment.doctor_id == doctor_id)
            .order_by(Appointment.scheduled_date.asc())
        )
        if status:
            query = query.where(Appointment.status == status)
        total_result = await self.db.execute(query)
        total = len(total_result.scalars().all())
        offset = (page - 1) * size
        paginated = await self.db.execute(query.offset(offset).limit(size))
        return paginated.scalars().all(), total

    async def get_pending_reminders(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> list[Appointment]:
        """Get confirmed appointments due in a time window that haven't been reminded yet."""
        from sqlalchemy import and_
        result = await self.db.execute(
            select(Appointment)
            .options(selectinload(Appointment.patient), selectinload(Appointment.doctor))
            .where(
                and_(
                    Appointment.status == AppointmentStatus.confirmed,
                    Appointment.reminder_sent == False,
                )
            )
        )
        return result.scalars().all()
