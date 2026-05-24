"""
MedBook Mega Seed v7.3 - Safe Edition
Final clean run without special characters for Windows terminal.
"""
import asyncio
from datetime import date, time
from sqlalchemy import select, delete, text

from app.database import engine, AsyncSessionLocal, Base
from app.models import User, Specialty, Doctor, Schedule, Appointment, MedicalRecord, PrescriptionItem, Payment
from app.core.security import hash_password

SPECIALTIES_LIST = [
    "Khoa Tim mach", "Khoa Tieu hoa", "Khoa Chan thuong chinh hinh", "Khoa Noi Than kinh",
    "Khoa Truyen nhiem", "Khoa San phu khoa", "Khoa Than - Loc mau", "Khoa Ung buou",
    "Khoa Rang Ham Mat", "Khoa Tai Mui Hong", "Khoa Mat", "Khoa Phuc hoi chuc nang",
    "Khoa Da lieu", "Khoa Cap cuu"
]

async def seed():
    async with engine.begin() as conn:
        print("[1/4] RESETTING SCHEMA...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("[2/4] SEEDING SYSTEM ACCOUNTS (@medbook.vn)...")
        # Admin & Cashier
        for email, pwd, name, role in [
            ("admin@medbook.vn", "123y", "Quan tri vien", "hr_admin"),
            ("cashier@medbook.vn", "Cashier@123", "Thu ngan chinh", "cashier_admin")
        ]:
            db.add(User(
                email=email,
                password_hash=hash_password(pwd),
                full_name=name,
                role=role,
                is_active=True,
                is_verified=True,
                phone=f"0988{email[0:2]}"
            ))

        # Patients
        for idx, (p_email, p_name, p_phone, p_dob, p_gender, p_blood) in enumerate([
            ("patient1@medbook.vn", "Trương Thế Hải Thịnh", "0912345678", date(1995, 5, 15), "Nam", "O+"), 
            ("patient2@medbook.vn", "Nguyễn Văn B", "0912345679", date(1998, 10, 20), "Nữ", "AB+")
        ], 1):
            db.add(User(
                email=p_email,
                password_hash=hash_password("Patient@123"),
                full_name=p_name,
                patient_code=f"MB-{idx:03d}",
                phone=p_phone,
                address="Ha Noi, Viet Nam",
                date_of_birth=p_dob,
                gender=p_gender,
                blood_type=p_blood,
                role="patient",
                is_active=True,
                is_verified=True
            ))
        await db.flush()

        print("[3/4] SEEDING SPECIALTIES & 28 DOCTORS...")
        for i, spec_name in enumerate(SPECIALTIES_LIST, 1):
            spec_obj = Specialty(name=spec_name, description=f"Kham chuyen sau tai {spec_name}")
            db.add(spec_obj)
            await db.flush()

            for suffix in ["", "b"]:
                dr_email = f"pk{i}{suffix}@medbook.com"
                dr_name = f"Bac si {spec_name.replace('Khoa ', '')} {('A' if suffix == '' else 'B')}"
                
                dr_user = User(
                    email=dr_email,
                    password_hash=hash_password("Doctor@123"),
                    full_name=dr_name,
                    phone=f"0777{i:02d}{'1' if suffix == '' else '2'}",
                    role="doctor",
                    is_active=True,
                    is_verified=True
                )
                db.add(dr_user)
                await db.flush()

                doc = Doctor(user_id=dr_user.id, specialty_id=spec_obj.id, bio=f"Chuyen gia {spec_name}.", experience_years=10, is_approved=True, room_number=f"Room {100+i}")
                db.add(doc)
                await db.flush()

                for dow in range(0, 7):
                    db.add(Schedule(
                        doctor_id=doc.id,
                        day_of_week=dow,
                        start_time=time(6, 30),
                        end_time=time(16, 30),
                        slot_duration_min=30,
                        max_slots=20
                    ))
            
            # Store first doctor for sample appointments
            if i == 1:
                sample_doctor_id = doc.id
                sample_patient1_id = (await db.execute(select(User.id).where(User.email == "patient1@medbook.vn"))).scalar()
        
        await db.flush()

        print("[4/4] SEEDING SAMPLE APPOINTMENTS...")
        if sample_doctor_id and sample_patient1_id:
            # 1. Upcoming Appointment
            db.add(Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date.today(),
                scheduled_time=time(14, 0),
                reason="Dau nguc trai, kho tho nhe.",
                status="CONFIRMED",
                queue_number=1,
                room_number="Room 101"
            ))

            # 2. Completed Appointment with Medical Record
            past_appt = Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date(2026, 4, 1),
                scheduled_time=time(9, 30),
                reason="Kham dinh ky tim mach.",
                status="COMPLETED"
            )
            db.add(past_appt)
            await db.flush()

            record = MedicalRecord(
                appointment_id=past_appt.id,
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                diagnosis="Huyet ap cao nhe, nhip tim on dinh.",
                notes="Han che an man, tap the duc deu dan.",
                revisit_required=True,
                revisit_date=date(2026, 5, 1)
            )
            db.add(record)
            await db.flush()

            db.add(PrescriptionItem(
                medical_record_id=record.id,
                medicine_name="Amlodipine 5mg",
                dosage="5mg",
                morning=1.0,
                total_quantity=30.0,
                instructions="Uong sau khi an sang."
            ))

            # 3. Appointment waiting for payment (PRESCRIPTION_SENT)
            pay_appt = Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date.today(),
                scheduled_time=time(10, 0),
                reason="Dau dau, hoa mat.",
                status="PRESCRIPTION_SENT",
                queue_number=2
            )
            db.add(pay_appt)
            await db.flush()

            pay_record = MedicalRecord(
                appointment_id=pay_appt.id,
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                diagnosis="Thieu mau nao nhe.",
                notes="Nghi ngoi nhieu hon, tranh thuc khuya."
            )
            db.add(pay_record)
            await db.flush()

            db.add(PrescriptionItem(
                medical_record_id=pay_record.id,
                medicine_name="Ginkgo Biloba",
                dosage="80mg",
                morning=1.0,
                evening=1.0,
                total_quantity=60.0,
                instructions="Uong trong khi an."
            ))

            db.add(Payment(
                appointment_id=pay_appt.id,
                amount=150000.0,
                status="PENDING"
            ))

        await db.commit()
        print("DATABASE INITIALIZED SUCCESSFULLY.")

if __name__ == "__main__":
    asyncio.run(seed())
