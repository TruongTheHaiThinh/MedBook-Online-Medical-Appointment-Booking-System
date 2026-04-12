import asyncio
from datetime import date, time

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.specialty import Specialty
from app.models.doctor import Doctor
from app.models.schedule import Schedule
from app.core.security import hash_password

async def seed():
    # Only run if you want to drop all tables and create fresh ones, 
    # instead of doing migration. Here we'll just populate.
    async with AsyncSessionLocal() as db:
        # Create Specialties
        cardiology = Specialty(name="Tim mạch", description="Khoa tim mạch và lồng ngực")
        internal_med = Specialty(name="Nội tổng quát", description="Khám chữa bệnh nội khoa chung")
        dermatology = Specialty(name="Da liễu", description="Chuyên khoa về da và điều trị da liễu")
        
        db.add_all([cardiology, internal_med, dermatology])
        await db.commit()
        await db.refresh(cardiology)
        await db.refresh(internal_med)
        await db.refresh(dermatology)

        print("Created specialties")

        # Create Admin
        admin = User(
            email="admin@medbook.com",
            password_hash=hash_password("Admin@123"),
            full_name="Quản trị viên",
            phone="0988000000",
            role="admin",
        )
        db.add(admin)

        # Create Patients
        patient1 = User(
            email="patient1@gmail.com",
            password_hash=hash_password("Patient@123"),
            full_name="Nguyễn Văn A",
            phone="0911000111",
            role="patient"
        )
        patient2 = User(
            email="patient2@gmail.com",
            password_hash=hash_password("Patient@123"),
            full_name="Trần Thị B",
            phone="0922000222",
            role="patient"
        )
        db.add_all([patient1, patient2])

        # Create Doctors
        doc_user1 = User(
            email="doctor1@medbook.com",
            password_hash=hash_password("Doctor@123"),
            full_name="BS. Lê Văn C",
            phone="0933000333",
            role="doctor"
        )
        doc_user2 = User(
            email="doctor2@medbook.com",
            password_hash=hash_password("Doctor@123"),
            full_name="BS. Phạm Thị D",
            phone="0944000444",
            role="doctor"
        )
        
        db.add_all([doc_user1, doc_user2])
        await db.commit()
        
        await db.refresh(doc_user1)
        await db.refresh(doc_user2)
        
        # Doctor profiles
        doc1 = Doctor(
            user_id=doc_user1.id,
            specialty_id=cardiology.id,
            bio="Bác sĩ có hơn 10 năm kinh nghiệm trong ngành tim mạch.",
            experience_years=10,
            is_approved=True
        )
        doc2 = Doctor(
            user_id=doc_user2.id,
            specialty_id=internal_med.id,
            bio="Chuyên gia khám Nội tổng quát, tu nghiệp từ Nhật Bản.",
            experience_years=8,
            is_approved=True
        )
        
        db.add_all([doc1, doc2])
        await db.commit()
        
        await db.refresh(doc1)
        await db.refresh(doc2)
        
        print("Created users and doctors")
        
        # Create schedules for Doctor 1 (e.g., Monday and Wednesday)
        sched1 = Schedule(
            doctor_id=doc1.id,
            day_of_week=1, # Monday
            start_time=time(8, 0),
            end_time=time(12, 0),
            slot_duration_min=30,
            max_slots=8
        )
        sched2 = Schedule(
            doctor_id=doc1.id,
            day_of_week=3, # Wednesday
            start_time=time(13, 0),
            end_time=time(17, 0),
            slot_duration_min=30,
            max_slots=8
        )
        
        db.add_all([sched1, sched2])
        await db.commit()
        
        print("Created schedules. Seed complete!")

if __name__ == "__main__":
    import sys
    import os
    # Ensure app directory is in PYTHONPATH
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    asyncio.run(seed())
