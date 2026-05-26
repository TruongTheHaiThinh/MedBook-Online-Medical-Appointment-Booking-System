import asyncio
import os
import sys
import csv
from datetime import date, time
import uuid

# Thiết lập đường dẫn để có thể import từ app
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Đảm bảo in được tiếng Việt trên Terminal Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import AsyncSessionLocal, engine, Base
from app.models import User, Specialty, Doctor, Schedule, Appointment, MedicalRecord, PrescriptionItem, Payment, Medicine
from app.core.security import hash_password
from sqlalchemy import select, insert, delete

SPECIALTIES_LIST = [
    "Khoa Tim mạch", "Khoa Tiêu hóa", "Khoa Chấn thương chỉnh hình", "Khoa Nội thần kinh",
    "Khoa Truyền nhiễm", "Khoa Sản phụ khoa", "Khoa Thận - Lọc máu", "Khoa Ung bướu",
    "Khoa Răng Hàm Mặt", "Khoa Tai Mũi Họng", "Khoa Mắt", "Khoa Phục hồi chức năng",
    "Khoa Da liễu", "Khoa Cấp cứu"
]

SPECIALTIES_DETAILS = {
    "Khoa Tim mạch": "Chẩn đoán và điều trị chuyên sâu các bệnh lý về tim mạch, huyết áp và mạch máu bằng công nghệ y khoa tiên tiến.",
    "Khoa Tiêu hóa": "Tầm soát, điều trị các bệnh lý đường tiêu hóa, gan mật, kết hợp phương pháp nội soi không đau hiện đại.",
    "Khoa Chấn thương chỉnh hình": "Phẫu thuật chấn thương cơ xương khớp, phục hồi vận động và tái tạo chức năng sau chấn thương.",
    "Khoa Nội thần kinh": "Điều trị các bệnh lý thần kinh, đau đầu, đột quỵ, rối loạn giấc ngủ và các hội chứng suy giảm trí nhớ.",
    "Khoa Truyền nhiễm": "Chẩn đoán, phòng ngừa và điều trị các bệnh truyền nhiễm nguy hiểm, dịch bệnh theo mùa và tiêm chủng bảo vệ cơ thể.",
    "Khoa Sản phụ khoa": "Chăm sóc sức khỏe thai kỳ toàn diện, điều trị phụ khoa và tư vấn kế hoạch hóa gia đình tận tâm.",
    "Khoa Thận - Lọc máu": "Điều trị suy thận cấp và mãn tính, lọc máu chu kỳ bằng hệ thống màng lọc thế hệ mới an toàn tuyệt đối.",
    "Khoa Ung bướu": "Tầm soát ung thư sớm, tư vấn phác đồ điều trị đa mô thức và đồng hành chăm sóc giảm nhẹ cho người bệnh.",
    "Khoa Răng Hàm Mặt": "Chăm sóc và điều trị các bệnh răng miệng, nha khoa thẩm mỹ chất lượng cao, phục hình răng sứ không đau.",
    "Khoa Tai Mũi Họng": "Điều trị hiệu quả các bệnh lý tai mũi họng cấp và mãn tính ở cả người lớn và trẻ em bằng kỹ thuật nội soi.",
    "Khoa Mắt": "Khám điều trị các tật khúc xạ, phẫu thuật đục thủy tinh thể và bảo vệ thị lực toàn diện.",
    "Khoa Phục hồi chức năng": "Thiết kế bài tập chuyên biệt giúp phục hồi khả năng vận động sau tai biến, phẫu thuật hoặc chấn thương cột sống.",
    "Khoa Da liễu": "Điều trị chuyên sâu các bệnh lý da liễu bẩm sinh, viêm da, mụn trứng cá và chăm sóc thẩm mỹ da an toàn.",
    "Khoa Cấp cứu": "Tiếp nhận và xử trí nhanh chóng, kịp thời các ca bệnh khẩn cấp 24/7 với trang thiết bị hồi sức hiện đại nhất."
}

async def init_db():
    print("--- RESETTING SCHEMA (DROP & CREATE TABLES) ---")
    async with engine.begin() as conn:
        # Tạo tất cả các bảng nếu chưa tồn tại
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema reset successfully.")

async def seed_data():
    print("--- Dang do du lieu mau Mega Seed ---")
    async with AsyncSessionLocal() as db:
        # 1. Tạo các Chuyên khoa
        print("[1/5] Seeding Chuyen khoa...")
        specs = {}
        for spec_name in SPECIALTIES_LIST:
            desc = SPECIALTIES_DETAILS.get(spec_name, f"Khám chuyên sâu tại {spec_name}")
            new_spec = Specialty(name=spec_name, description=desc)
            db.add(new_spec)
            await db.flush()
            specs[spec_name] = new_spec
            print(f"Da tao chuyen khoa: {spec_name}")

        # 2. Tạo ROLE: HR ADMIN & CASHIER ADMIN
        print("[2/5] Seeding he thong tai khoan quan ly...")
        for email, pwd, name, role in [
            ("admin@medbook.vn", "123y", "Quản trị viên Trần Quốc Bảo", "hr_admin"),
            ("cashier@medbook.vn", "Cashier@123", "Thu Ngân - Nguyễn Minh Khuê", "cashier_admin")
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
            print(f"Da tao tai khoan {role}: {email}")

        # 3. Tạo PATIENTS (Bệnh nhân mẫu)
        print("[3/5] Seeding Benh nhan...")
        patients_list = [
            ("patient1@medbook.vn", "Trương Thế Hải Thịnh", "0912345678", date(1995, 5, 15), "Nam", "O+"),
            ("patient2@medbook.vn", "Nguyễn Văn B", "0912345679", date(1998, 10, 20), "Nữ", "AB+")
        ]
        
        for idx, (p_email, p_name, p_phone, p_dob, p_gender, p_blood) in enumerate(patients_list, 1):
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
            print(f"Da tao benh nhan: {p_name} ({p_email}) - Ma: MB-{idx:03d}")
        await db.flush()

        # 4. Tạo DOCTORS (28 Bác sĩ thuộc 14 chuyên khoa)
        print("[4/5] Seeding 28 Bac si va lich lam viec...")
        DOCTOR_NAMES = [
            "Phạm Hoàng Nam", "Nguyễn Tấn Phát", "Lê Thị Mai", "Trần Minh Quân",
            "Hoàng Đức Hải", "Vũ Thanh Hằng", "Đỗ Quốc Bảo", "Nguyễn Mỹ Linh",
            "Phan Thanh Bình", "Trần Thị Hồng", "Lý Gia Kiệt", "Nguyễn Hữu Đạt",
            "Lê Huy Hoàng", "Nguyễn Bích Ngọc", "Bùi Anh Tuấn", "Phạm Minh Trí",
            "Trần Ngọc Lan", "Nguyễn Quang Huy", "Đặng Văn Lâm", "Lê Thu Thảo",
            "Vũ Hoàng Long", "Nguyễn Bảo Châu", "Hoàng Kim Oanh", "Trần Việt Anh",
            "Phạm Hùng Cường", "Đỗ Thu Trang", "Nguyễn Duy Mạnh", "Lê Công Vinh"
        ]
        for i, spec_name in enumerate(SPECIALTIES_LIST, 1):
            for suffix in ["", "b"]:
                dr_email = f"pk{i}{suffix}@medbook.com"
                idx = (i - 1) * 2 + (0 if suffix == "" else 1)
                dr_name = f"Bác sĩ {DOCTOR_NAMES[idx % len(DOCTOR_NAMES)]}"
                
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

                doc = Doctor(
                    user_id=dr_user.id,
                    specialty_id=specs[spec_name].id,
                    bio=f"Chuyên gia {spec_name}.",
                    experience_years=10,
                    is_approved=True,
                    room_number=f"Room {100+i}"
                )
                db.add(doc)
                await db.flush()

                # Tạo lịch làm việc từ Thứ 2 đến Chủ nhật (0 - 6)
                for dow in range(0, 7):
                    db.add(Schedule(
                        doctor_id=doc.id,
                        day_of_week=dow,
                        start_time=time(6, 30),
                        end_time=time(16, 30),
                        slot_duration_min=30,
                        max_slots=20
                    ))
            
            # Lưu bác sĩ và bệnh nhân đầu tiên để tạo các lịch hẹn mẫu
            if i == 1:
                sample_doctor_id = doc.id
                sample_patient1_id = (await db.execute(select(User.id).where(User.email == "patient1@medbook.vn"))).scalar()
        
        await db.flush()

        # 5. Tạo các LỊCH HẸN & BỆNH ÁN & GIAO DỊCH mẫu
        print("[5/5] Seeding Cac ca kham & Giao dich mau...")
        if sample_doctor_id and sample_patient1_id:
            # Ca 1: Sắp diễn ra (CONFIRMED)
            db.add(Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date.today(),
                scheduled_time=time(14, 0),
                reason="Đau ngực trái, khó thở nhẹ.",
                status="CONFIRMED",
                queue_number=1,
                room_number="Room 101"
            ))

            # Ca 2: Đã hoàn thành (COMPLETED) kèm Bệnh án & Đơn thuốc mẫu
            past_appt = Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date(2026, 4, 1),
                scheduled_time=time(9, 30),
                reason="Khám định kỳ tim mạch.",
                status="COMPLETED"
            )
            db.add(past_appt)
            await db.flush()

            record = MedicalRecord(
                appointment_id=past_appt.id,
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                diagnosis="Huyết áp cao nhẹ, nhịp tim ổn định.",
                notes="Hạn chế ăn mặn, tập thể dục đều đặn.",
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
                instructions="Uống sau khi ăn sáng."
            ))

            # Ca 3: Chờ thanh toán (PRESCRIPTION_SENT) kèm hóa đơn mẫu PENDING
            pay_appt = Appointment(
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                scheduled_date=date.today(),
                scheduled_time=time(10, 0),
                reason="Đau đầu, hoa mắt.",
                status="PRESCRIPTION_SENT",
                queue_number=2
            )
            db.add(pay_appt)
            await db.flush()

            pay_record = MedicalRecord(
                appointment_id=pay_appt.id,
                patient_id=sample_patient1_id,
                doctor_id=sample_doctor_id,
                diagnosis="Thiếu máu não nhẹ.",
                notes="Nghỉ ngơi nhiều hơn, tránh thức khuya."
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
                instructions="Uống trong khi ăn."
            ))

            db.add(Payment(
                appointment_id=pay_appt.id,
                amount=150000.0,
                status="PENDING"
            ))
            print("Da tao xong cac ca kham & Giao dich mau.")

        # 6. Nhập dữ liệu Thuốc từ CSV (khoảng 20,316 loại thuốc)
        print("[BONUS] Nhap du lieu Thuoc tu file CSV...")
        csv_path = os.path.join(os.path.dirname(__file__), "..", "medicine_dataset.csv")
        if os.path.exists(csv_path):
            print("Dang doc va loc du lieu thuoc tu CSV...")
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_rows = list(reader)
                
                # Lọc trùng lặp trong file CSV theo tất cả các trường
                unique_rows = []
                seen_full = set()
                for row in all_rows:
                    key = (
                        row.get('Name', '').strip(),
                        row.get('Category', '').strip(),
                        row.get('Dosage Form', '').strip(),
                        row.get('Strength', '').strip(),
                        row.get('Manufacturer', '').strip(),
                        row.get('Indication', '').strip(),
                        row.get('Classification', '').strip()
                    )
                    if key not in seen_full:
                        seen_full.add(key)
                        unique_rows.append(row)
                
                total_unique = len(unique_rows)
                print(f"Tong so thuoc duy nhat trong CSV: {total_unique}")
                
                # Lấy 20,000 thuốc đầu + 316 thuốc cuối
                selected_rows = []
                first_part_limit = min(20000, total_unique)
                first_part = unique_rows[:first_part_limit]
                
                last_part_start = max(0, total_unique - 316)
                last_part = unique_rows[last_part_start:]
                
                selected_rows = first_part + last_part
                
                # Chuyển thành batch list
                batch = []
                for row in selected_rows:
                    batch.append({
                        "id": uuid.uuid4(),
                        "name": row['Name'],
                        "category": row.get('Category'),
                        "dosage_form": row.get('Dosage Form'),
                        "strength": row.get('Strength'),
                        "manufacturer": row.get('Manufacturer'),
                        "indication": row.get('Indication'),
                        "classification": row.get('Classification')
                    })
                
                if batch:
                    # Tránh DDL locks bằng cách xóa dữ liệu cũ trước khi chèn
                    await db.execute(delete(Medicine))
                    await db.flush()
                    await db.execute(insert(Medicine), batch)
            print(f"Da nhap {len(batch)} loai thuoc moi (20000 dau + 316 cuoi) vao database.")
        else:
            print("WARNING: Khong tim thay medicine_dataset.csv")

        await db.commit()
        print("--- Mega Seed Hoan tat do du lieu mau ---")

async def main():
    await init_db()
    await seed_data()

if __name__ == "__main__":
    asyncio.run(main())
