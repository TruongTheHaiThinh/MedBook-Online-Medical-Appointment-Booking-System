import asyncio
import os
import sys
import csv
from datetime import date, time

# Thiết lập đường dẫn để có thể import từ app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.specialty import Specialty
from app.models.doctor import Doctor
from app.models.schedule import Schedule
from app.models.medicine import Medicine
from app.core.security import hash_password
from sqlalchemy import select

async def init_db():
    print("--- Khởi tạo Database và các bảng ---")
    async with engine.begin() as conn:
        # Tạo tất cả các bảng nếu chưa tồn tại
        await conn.run_sync(Base.metadata.create_all)
    print("Database đã được khởi tạo thành công.")

async def seed_data():
    print("--- Đang đổ dữ liệu mẫu ---")
    async with AsyncSessionLocal() as db:
        # 1. Tạo các Chuyên khoa
        specs_data = [
            {"name": "Viện Chấn thương Chỉnh hình", "desc": "Chuyên khoa mũi nhọn điều trị cơ xương khớp."},
            {"name": "Ngoại Thần kinh", "desc": "Phẫu thuật bệnh lý não bộ và cột sống."},
            {"name": "Nội Tiêu hóa", "desc": "Điều trị bệnh lý đường tiêu hóa kỹ thuật cao."},
            {"name": "Tim mạch - Khớp - Nội tiết", "desc": "Chăm sóc sức khỏe nội tiết và tim mạch."},
            {"name": "Phụ sản", "desc": "Dịch vụ sản nhi toàn diện."},
            {"name": "Khoa Nhi", "desc": "Chăm sóc sức khỏe trẻ em."},
            {"name": "Khoa Mắt", "desc": "Điều trị khúc xạ và bệnh lý về mắt."}
        ]
        
        specs = {}
        for s in specs_data:
            stmt = select(Specialty).where(Specialty.name == s["name"])
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                new_spec = Specialty(name=s["name"], description=s["desc"])
                db.add(new_spec)
                await db.flush()
                specs[s["name"]] = new_spec
                print(f"Đã tạo chuyên khoa: {s['name']}")
            else:
                specs[s["name"]] = existing
                print(f"Chuyên khoa đã tồn tại: {s['name']}")

        # 2. Tạo ROLE: HR ADMIN (Quản lý)
        hr_email = "admin@medbook.vn"
        if not (await db.execute(select(User).where(User.email == hr_email))).first():
            db.add(User(
                email=hr_email,
                password_hash=hash_password("Admin@123"),
                full_name="Trần Thế Hải (HR Manager)",
                phone="0901234567",
                role="hr_admin"
            ))
            print(f"Đã tạo Admin: {hr_email}")

        # 3. Tạo ROLE: CASHIER ADMIN (Thu ngân)
        cash_email = "cashier@medbook.vn"
        if not (await db.execute(select(User).where(User.email == cash_email))).first():
            db.add(User(
                email=cash_email,
                password_hash=hash_password("Cashier@123"),
                full_name="Nguyễn Thu Ngân",
                phone="0907654321",
                role="cashier_admin"
            ))
            print(f"Đã tạo Thu ngân: {cash_email}")

        # 4. Tạo DOCTORS (Mỗi bác sĩ 1 tài khoản)
        doctors_list = [
            {"name": "Bác sĩ Nguyễn Việt Nam", "email": "vietnam.175@medbook.vn", "spec": "Viện Chấn thương Chỉnh hình", "exp": 25},
            {"name": "Bác sĩ Trần Quốc Anh", "email": "quocanh.175@medbook.vn", "spec": "Ngoại Thần kinh", "exp": 20},
            {"name": "Bác sĩ Lê Thị Mai", "email": "lemai.175@medbook.vn", "spec": "Phụ sản", "exp": 15},
            {"name": "Bác sĩ Hoàng Thanh Tùng", "email": "thanhtung@medbook.vn", "spec": "Khoa Nhi", "exp": 12},
            {"name": "Bác sĩ Ngô Mỹ Linh", "email": "mylinh@medbook.vn", "spec": "Khoa Mắt", "exp": 10},
        ]

        for d in doctors_list:
            if (await db.execute(select(User).where(User.email == d["email"]))).first(): 
                print(f"Bác sĩ đã tồn tại: {d['email']}")
                continue

            u = User(
                email=d["email"],
                password_hash=hash_password("Doctor@123"),
                full_name=d["name"],
                phone="0917500" + str(doctors_list.index(d)),
                role="doctor",
                is_active=True
            )
            db.add(u)
            await db.flush()

            doc = Doctor(
                user_id=u.id,
                specialty_id=specs[d["spec"]].id,
                bio=f"Bác sĩ chuyên khoa tại Bệnh viện Medbook. Kinh nghiệm {d['exp']} năm.",
                experience_years=d["exp"],
                is_approved=True
            )
            db.add(doc)
            await db.flush()

            # Lịch 07:30 - 16:30 (T2-T7) - Cập nhật giờ chuẩn BV
            for day in range(0, 6):
                db.add(Schedule(
                    doctor_id=doc.id,
                    day_of_week=day,
                    start_time=time(7, 30),
                    end_time=time(16, 30),
                    slot_duration_min=30,
                    max_slots=20
                ))
            print(f"Đã tạo bác sĩ và lịch: {d['name']}")

        # 5. Tạo PATIENTS (Bệnh nhân mẫu)
        patients = [
            {"name": "Nguyễn Văn Bệnh", "email": "patient1@medbook.vn"},
            {"name": "Trần Thị Khám", "email": "patient2@medbook.vn"}
        ]
        for p in patients:
            if (await db.execute(select(User).where(User.email == p["email"]))).first(): continue
            db.add(User(
                email=p["email"],
                password_hash=hash_password("Patient@123"),
                full_name=p["name"],
                phone="0922000" + str(patients.index(p)),
                role="patient"
            ))
            print(f"Đã tạo bệnh nhân mẫu: {p['name']}")

        # 6. Nhập dữ liệu Thuốc từ CSV
        csv_path = os.path.join(os.path.dirname(__file__), "medicine_dataset.csv")
        if os.path.exists(csv_path):
            print("Đang nhập dữ liệu thuốc từ CSV...")
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Kiểm tra xem thuốc đã tồn tại chưa
                    stmt = select(Medicine).where(Medicine.name == row['name'])
                    existing = (await db.execute(stmt)).scalar_one_or_none()
                    if not existing:
                        db.add(Medicine(
                            name=row['name'],
                            unit=row['unit'],
                            price=float(row['price']),
                            description=row.get('description', '')
                        ))
                        count += 1
                        if count % 100 == 0: await db.flush()
            print(f"Đã nhập {count} loại thuốc.")

        await db.commit()
        print("--- Hoàn tất đổ dữ liệu mẫu ---")

async def main():
    await init_db()
    await seed_data()

if __name__ == "__main__":
    asyncio.run(main())
