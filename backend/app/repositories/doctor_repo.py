import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.doctor import Doctor


class DoctorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, doctor_id: uuid.UUID) -> Optional[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(selectinload(Doctor.user), selectinload(Doctor.specialty))
            .where(Doctor.id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(selectinload(Doctor.specialty))
            .where(Doctor.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID) -> Doctor:
        doctor = Doctor(user_id=user_id)
        self.db.add(doctor)
        await self.db.commit()
        await self.db.refresh(doctor)
        return doctor

    async def update(self, doctor: Doctor, **kwargs) -> Doctor:
        for key, value in kwargs.items():
            if value is not None:
                setattr(doctor, key, value)
        await self.db.commit()
        await self.db.refresh(doctor)
        return doctor

    async def list_approved(
        self, specialty_id: Optional[uuid.UUID] = None, page: int = 1, size: int = 20
    ) -> tuple[list[Doctor], int]:
        query = (
            select(Doctor)
            .options(selectinload(Doctor.user), selectinload(Doctor.specialty))
            .where(Doctor.is_approved == True)
        )
        if specialty_id:
            query = query.where(Doctor.specialty_id == specialty_id)

        all_result = await self.db.execute(query)
        all_doctors = all_result.scalars().all()
        total = len(all_doctors)

        offset = (page - 1) * size
        paginated = await self.db.execute(query.offset(offset).limit(size))
        return paginated.scalars().all(), total

    async def list_pending_approval(self) -> list[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(selectinload(Doctor.user), selectinload(Doctor.specialty))
            .where(Doctor.is_approved == False)
        )
        return result.scalars().all()
