import asyncio
import os
import sys

sys.path.append(os.getcwd())

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.appointment import Appointment

async def get_test_qrs():
    async with AsyncSessionLocal() as db:
        stmt = select(Appointment).where(Appointment.qr_code != None).limit(10)
        result = await db.execute(stmt)
        appts = result.scalars().all()
        
        print("\n=== QR CODES IN DATABASE ===\n")
        if not appts:
            stmt2 = select(Appointment).where(Appointment.status == "CONFIRMED").limit(5)
            result2 = await db.execute(stmt2)
            appts2 = result2.scalars().all()
            if not appts2:
                print("No ready appointments. Please pay for an appointment.")
            else:
                print("Found CONFIRMED appointments without QR codes:")
                for a in appts2:
                    print(f"ID: {str(a.id)} | Status: {a.status}")
        else:
            for a in appts:
                print(f"ID: {str(a.id)[:8]} | QR: {a.qr_code} | Status: {a.status}")
        print("\n============================\n")

if __name__ == "__main__":
    asyncio.run(get_test_qrs())
