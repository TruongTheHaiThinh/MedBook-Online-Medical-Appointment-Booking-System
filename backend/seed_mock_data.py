import asyncio
import json
from uuid import uuid4
from datetime import date, time, timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal as async_session_maker
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from sqlalchemy import select

async def seed():
    async with async_session_maker() as session:
        # Find first doctor
        result = await session.execute(select(Doctor))
        doctor = result.scalars().first()
        
        # Find first patient (user where role == 'patient')
        result_pat = await session.execute(select(User).where(User.role == 'patient'))
        patient = result_pat.scalars().first()
        
        if not doctor or not patient:
            print("Vui lòng tạo ít nhất 1 bác sĩ và 1 bệnh nhân từ giao diện trước khi chạy mock data!")
            return
            
        print(f"Adding mock appointments for Pat: {patient.id} - Doc: {doctor.id}")

        # Add a COMPLETED appointment
        dt = datetime.now() - timedelta(days=1)
        notes = "Chẩn đoán:\nViêm Amidan hốc mủ, sốt nhẹ.\n\nĐơn thuốc:\n- Augmentin 1g (Sáng: 1, Trưa: 0, Chiều: 1) - Tổng: 10 viên\n- Paracetamol 500mg (Sáng: 0, Trưa: 1, Chiều: 0) - Tổng: 5 viên\n- Alpha Choay (Sáng: 2, Trưa: 0, Chiều: 2) - Tổng: 20 viên"
        app1 = Appointment(
            id=uuid4(),
            patient_id=patient.id,
            doctor_id=doctor.id,
            scheduled_date=dt.date(),
            scheduled_time=time(9, 30),
            reason="Đau họng, sốt từ 2 ngày trước.",
            status="COMPLETED",
            doctor_notes=notes,
            reminder_sent=True,
            created_at=datetime.now() - timedelta(days=2)
        )
        session.add(app1)
        
        # Add a PENDING appointment
        dt2 = datetime.now() + timedelta(days=2)
        app2 = Appointment(
            id=uuid4(),
            patient_id=patient.id,
            doctor_id=doctor.id,
            scheduled_date=dt2.date(),
            scheduled_time=time(14, 0),
            reason="Tái khám nội soi tai mũi họng.",
            status="PENDING",
            doctor_notes=None,
            reminder_sent=False,
            created_at=datetime.now()
        )
        session.add(app2)

        # Ensure Doctor has a profile if they don't
        doctor.experience_years = 10
        doctor.bio = "Bác sĩ chuyên khoa I, trưởng khoa Răng Hàm Mặt bệnh viện Chợ Rẫy."
        
        await session.commit()
        print("Mock data seeded successfully! Vui lòng làm mới trang (F5).")

if __name__ == "__main__":
    asyncio.run(seed())
