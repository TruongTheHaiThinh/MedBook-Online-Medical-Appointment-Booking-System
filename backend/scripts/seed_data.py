from __future__ import annotations
import sys
from pathlib import Path

# Add backend directory to sys.path to allow importing app modules
sys.path.append(str(Path(__file__).parent.parent))

"""
Seed data script for Medbook System.
Before running this, make sure your PostgreSQL database is running 
and migrations have been applied (alembic upgrade head).
Run this via: python -m scripts.seed_data
"""
import asyncio
import uuid
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.specialty import Specialty
from app.models.schedule import Schedule
from app.models.appointment import Appointment, AppointmentStatus


async def seed():
    print("Bắt đầu tạo dữ liệu mẫu (Seed Data)...")
    async with AsyncSessionLocal() as db:
        # 1. Tạo Admin
        print("1. Tạo Admin...")
        admin = User(
            email="admin@medbook.com",
            password_hash=get_password_hash("Admin@123"),
            full_name="Quản Trị Viên",
            phone="0900000000",
            role=UserRole.admin,
            is_active=True
        )
        db.add(admin)

        # 2. Tạo Chuyên Khoa (Specialties)
        print("2. Tạo Chuyên khoa...")
        specs = [
            Specialty(name="Tim mạch", description="Khoa tim mạch và mạch máu"),
            Specialty(name="Nội tổng quát", description="Khám bệnh tổng quát"),
            Specialty(name="Da liễu", description="Các bệnh lý về da"),
            Specialty(name="Nhi khoa", description="Khám chữa bệnh cho trẻ em")
        ]
        db.add_all(specs)
        await db.commit()

        # Lấy lại các chuyên khoa vừa tạo
        for s in specs:
            await db.refresh(s)

        # 3. Tạo Bác Sĩ (Doctors)
        print("3. Tạo Bác sĩ...")
        doctor_users = [
            User(
                email="doctor.tim@medbook.com",
                password_hash=get_password_hash("Doctor@123"),
                full_name="BS. Nguyễn Văn Tim",
                phone="0911111111",
                role=UserRole.doctor
            ),
            User(
                email="doctor.da@medbook.com",
                password_hash=get_password_hash("Doctor@123"),
                full_name="BS. Trần Thị Da",
                phone="0922222222",
                role=UserRole.doctor
            )
        ]
        db.add_all(doctor_users)
        await db.commit()
        for d in doctor_users:
            await db.refresh(d)

        # Tạo thông tin hồ sơ bác sĩ (Doctor profiles)
        doc1 = Doctor(
            user_id=doctor_users[0].id,
            specialty_id=specs[0].id, # Tim mạch
            bio="Bác sĩ chuyên khoa Tim mạch với 15 năm kinh nghiệm từ BV Chợ Rẫy.",
            experience_years=15,
            is_approved=True
        )
        doc2 = Doctor(
            user_id=doctor_users[1].id,
            specialty_id=specs[2].id, # Da liễu
            bio="Bác sĩ chuyên khoa Da liễu, tu nghiệp tại Pháp.",
            experience_years=8,
            is_approved=True
        )
        db.add_all([doc1, doc2])
        await db.commit()
        await db.refresh(doc1)
        await db.refresh(doc2)

        # 4. Tạo Lịch Làm Việc Mẫu (Schedules)
        print("4. Tạo lịch làm việc cho bác sĩ...")
        schedules = [
            # BS Tim mạch: T2 (day 0), T4 (day 2), T6 (day 4), 08:00 - 12:00
            Schedule(
                doctor_id=doc1.id, day_of_week=0, start_time=datetime.time(8, 0),
                end_time=datetime.time(12, 0), slot_duration_min=30, max_slots=8
            ),
            Schedule(
                doctor_id=doc1.id, day_of_week=2, start_time=datetime.time(8, 0),
                end_time=datetime.time(12, 0), slot_duration_min=30, max_slots=8
            ),
            Schedule(
                doctor_id=doc1.id, day_of_week=4, start_time=datetime.time(8, 0),
                end_time=datetime.time(12, 0), slot_duration_min=30, max_slots=8
            ),
            # BS Da liễu: T3 (day 1), T5 (day 3), 13:00 - 17:00
            Schedule(
                doctor_id=doc2.id, day_of_week=1, start_time=datetime.time(13, 0),
                end_time=datetime.time(17, 0), slot_duration_min=30, max_slots=8
            ),
            Schedule(
                doctor_id=doc2.id, day_of_week=3, start_time=datetime.time(13, 0),
                end_time=datetime.time(17, 0), slot_duration_min=30, max_slots=8
            ),
        ]
        db.add_all(schedules)

        # 5. Tạo Bệnh Nhân (Patients)
        print("5. Tạo Bệnh nhân...")
        patients = [
            User(
                email="patient.an@medbook.com",
                password_hash=get_password_hash("Patient@123"),
                full_name="Lê Văn An",
                phone="0933333333",
                role=UserRole.patient
            ),
            User(
                email="patient.binh@medbook.com",
                password_hash=get_password_hash("Patient@123"),
                full_name="Phạm Thị Bình",
                phone="0944444444",
                role=UserRole.patient
            )
        ]
        db.add_all(patients)
        await db.commit()
        for p in patients:
            await db.refresh(p)

        # 6. Tạo 1-2 Cuộc hẹn mẫu (Appointments)
        print("6. Tạo Cuộc hẹn mẫu (Appointments)...")
        # Tìm một ngày T2 tiếp theo cho bác sĩ Tim mạch
        today = datetime.date.today()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0: # Target next Monday
            days_ahead += 7
        next_monday = today + datetime.timedelta(days_ahead)

        appts = [
            Appointment(
                patient_id=patients[0].id,
                doctor_id=doc1.id,
                scheduled_date=next_monday,
                scheduled_time=datetime.time(8, 0),
                reason="Đau thắt ngực khi vận động mạnh",
                status=AppointmentStatus.confirmed
            ),
            Appointment(
                patient_id=patients[1].id,
                doctor_id=doc1.id,
                scheduled_date=next_monday,
                scheduled_time=datetime.time(8, 30),
                reason="Kiểm tra tim mạch định kỳ",
                status=AppointmentStatus.pending
            )
        ]
        db.add_all(appts)
        await db.commit()

        print("🎉 Tạo dữ liệu Seed thành công!")
        print("-" * 50)
        print("Tài khoản (Password chung: Admin@123 / Doctor@123 / Patient@123):")
        print("- Admin: admin@medbook.com")
        print("- Doctor 1: doctor.tim@medbook.com")
        print("- Doctor 2: doctor.da@medbook.com")
        print("- Patient 1: patient.an@medbook.com")
        print("- Patient 2: patient.binh@medbook.com")


if __name__ == "__main__":
    asyncio.run(seed())
