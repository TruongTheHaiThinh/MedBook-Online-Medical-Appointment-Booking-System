import asyncio
from app.database import AsyncSessionLocal
from app.models.appointment import Appointment
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Appointment))
        appts = result.scalars().all()
        print(f"Total appointments: {len(appts)}")
        for a in appts:
            print(f"ID: {a.id} | Status: {a.status}")

if __name__ == "__main__":
    asyncio.run(check())
