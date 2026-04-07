import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.specialty import Specialty


class SpecialtyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, specialty_id: uuid.UUID) -> Optional[Specialty]:
        result = await self.db.execute(select(Specialty).where(Specialty.id == specialty_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Specialty]:
        result = await self.db.execute(select(Specialty).where(Specialty.name == name))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Specialty]:
        result = await self.db.execute(select(Specialty))
        return result.scalars().all()

    async def create(self, name: str, description: Optional[str] = None) -> Specialty:
        specialty = Specialty(name=name, description=description)
        self.db.add(specialty)
        await self.db.commit()
        await self.db.refresh(specialty)
        return specialty

    async def update(self, specialty: Specialty, **kwargs) -> Specialty:
        for key, value in kwargs.items():
            if value is not None:
                setattr(specialty, key, value)
        await self.db.commit()
        await self.db.refresh(specialty)
        return specialty

    async def delete(self, specialty: Specialty) -> None:
        await self.db.delete(specialty)
        await self.db.commit()
