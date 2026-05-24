import asyncio
from app.database import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserRegister
from fastapi import BackgroundTasks

async def test_patient_code():
    bg = BackgroundTasks()
    import random
    rand = random.randint(1000, 9999)
    data = UserRegister(
        email=f"patient_test_{rand}@medbook.vn",
        password="Patient@123",
        full_name="Benh nhan Test",
        phone=f"091122{rand}",
        address="Hanoi, Vietnam",
        role="patient"
    )
    async with AsyncSessionLocal() as db:
        user = await AuthService.register(data, db, bg)
        print(f"SUCCESSFULLY REGISTERED!")
        print(f"Patient Code: {user.patient_code}")

if __name__ == "__main__":
    asyncio.run(test_patient_code())
