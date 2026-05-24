import asyncio
import os
import sys
from datetime import time

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.specialty import Specialty
from app.models.doctor import Doctor
from app.models.schedule import Schedule
from app.core.security import hash_password
from sqlalchemy import select

async def seed_core():
    print("--- Connecting and Seeding Core ---")
    sys.stdout.flush()
    async with AsyncSessionLocal() as db:
        # Create Specialty
        new_spec = Specialty(name="Tim mach Test", description="Test Specialty")
        db.add(new_spec)
        await db.flush()
        print("Specialty flushed.")
        
        # Create Admin
        new_user = User(
            email="test_admin@medbook.vn",
            password_hash=hash_password("Admin@123"),
            full_name="Test HR Admin",
            phone="0999999999",
            role="hr_admin",
            is_active=True
        )
        db.add(new_user)
        await db.flush()
        print("Admin user flushed.")
        
        await db.commit()
        print("Commit successful!")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(seed_core())
