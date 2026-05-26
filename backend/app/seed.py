"""
MedBook Mega Seed v7.3 - Safe Edition
Final clean run with special characters support for Windows terminal.
"""
import asyncio
import sys
import io
from datetime import date, time
from sqlalchemy import select, delete, text

# Setup UTF-8 encoding for Windows command prompt to support accents
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.database import engine, AsyncSessionLocal, Base
from app.models import User, Specialty, Doctor, Schedule, Appointment, MedicalRecord, PrescriptionItem, Payment
from app.core.security import hash_password

SPECIALTIES_LIST = [
    {"name": "Khoa Tim mạch", "desc": "Chẩn đoán và điều trị chuyên sâu các bệnh lý về tim mạch, huyết áp và mạch máu bằng công nghệ y khoa tiên tiến."},
    {"name": "Khoa Tiêu hóa", "desc": "Tầm soát, điều trị các bệnh lý đường tiêu hóa, gan mật, kết hợp phương pháp nội soi không đau hiện đại."},
    {"name": "Khoa Chấn thương chỉnh hình", "desc": "Phẫu thuật chấn thương cơ xương khớp, phục hồi vận động và tái tạo chức năng sau chấn thương."},
    {"name": "Khoa Nội thần kinh", "desc": "Điều trị các bệnh lý thần kinh, đau đầu, đột quỵ, rối loạn giấc ngủ và các hội chứng suy giảm trí nhớ."},
    {"name": "Khoa Truyền nhiễm", "desc": "Chẩn đoán, phòng ngừa và điều trị các bệnh truyền nhiễm nguy hiểm, dịch bệnh theo mùa và tiêm chủng bảo vệ cơ thể."},
    {"name": "Khoa Sản phụ khoa", "desc": "Chăm sóc sức khỏe thai kỳ toàn diện, điều trị phụ khoa và tư vấn kế hoạch hóa gia đình tận tâm."},
    {"name": "Khoa Thận - Lọc máu", "desc": "Điều trị suy thận cấp và mãn tính, lọc máu chu kỳ bằng hệ thống màng lọc thế hệ mới an toàn tuyệt đối."},
    {"name": "Khoa Ung bướu", "desc": "Tầm soát ung thư sớm, tư vấn phác đồ điều trị đa mô thức và đồng hành chăm sóc giảm nhẹ cho người bệnh."},
    {"name": "Khoa Răng Hàm Mặt", "desc": "Chăm sóc và điều trị các bệnh răng miệng, nha khoa thẩm mỹ chất lượng cao, phục hình răng sứ không đau."},
    {"name": "Khoa Tai Mũi Họng", "desc": "Điều trị hiệu quả các bệnh lý tai mũi họng cấp và mãn tính ở cả người lớn và trẻ em bằng kỹ thuật nội soi."},
    {"name": "Khoa Mắt", "desc": "Khám điều trị các tật khúc xạ, phẫu thuật đục thủy tinh thể và bảo vệ thị lực toàn diện."},
    {"name": "Khoa Phục hồi chức năng", "desc": "Thiết kế bài tập chuyên biệt giúp phục hồi khả năng vận động sau tai biến, phẫu thuật hoặc chấn thương cột sống."},
    {"name": "Khoa Da liễu", "desc": "Điều trị chuyên sâu các bệnh lý da liễu bẩm sinh, viêm da, mụn trứng cá và chăm sóc thẩm mỹ da an toàn."},
    {"name": "Khoa Cấp cứu", "desc": "Tiếp nhận và xử trí nhanh chóng, kịp thời các ca bệnh khẩn cấp 24/7 với trang thiết bị hồi sức hiện đại nhất."}
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
        DOCTOR_NAMES = [
            "Phạm Hoàng Nam", "Nguyễn Tấn Phát", "Lê Thị Mai", "Trần Minh Quân",
            "Hoàng Đức Hải", "Vũ Thanh Hằng", "Đỗ Quốc Bảo", "Nguyễn Mỹ Linh",
            "Phan Thanh Bình", "Trần Thị Hồng", "Lý Gia Kiệt", "Nguyễn Hữu Đạt",
            "Lê Huy Hoàng", "Nguyễn Bích Ngọc", "Bùi Anh Tuấn", "Phạm Minh Trí",
            "Trần Ngọc Lan", "Nguyễn Quang Huy", "Đặng Văn Lâm", "Lê Thu Thảo",
            "Vũ Hoàng Long", "Nguyễn Bảo Châu", "Hoàng Kim Oanh", "Trần Việt Anh",
            "Phạm Hùng Cường", "Đỗ Thu Trang", "Nguyễn Duy Mạnh", "Lê Công Vinh"
        ]
        DOCTOR_PROFILES = [
            {"bio": "Hơn 15 năm kinh nghiệm điều trị nội tim mạch, chuyên sâu về suy tim, tăng huyết áp và rối loạn nhịp tim.", "exp": 15, "room": "Phòng 101"},
            {"bio": "Chuyên gia can thiệp tim mạch, tốt nghiệp khóa đào tạo chuyên sâu tại Bệnh viện Tim mạch Quốc gia.", "exp": 12, "room": "Phòng 102"},
            {"bio": "Chuyên điều trị các bệnh lý dạ dày, đại tràng và gan mật. Có thế mạnh về nội soi tiêu hóa không đau.", "exp": 10, "room": "Phòng 103"},
            {"bio": "Nghiên cứu sâu về hội chứng ruột kích thích, trào ngược dạ dày thực quản và các bệnh lý gan mật cấp tính.", "exp": 8, "room": "Phòng 104"},
            {"bio": "Nguyên phó khoa chấn thương tại bệnh viện đầu ngành, chuyên phẫu thuật thay khớp, nội soi khớp và tái tạo dây chằng.", "exp": 18, "room": "Phòng 201"},
            {"bio": "Chuyên gia về chỉnh hình nhi, điều trị dị tật bẩm sinh hệ vận động và phục hồi chức năng sau chấn thương thể thao.", "exp": 7, "room": "Phòng 202"},
            {"bio": "Chuyên điều trị đột quỵ, động kinh, Parkinson và các hội chứng đau đầu mãn tính, rối loạn giấc ngủ.", "exp": 14, "room": "Phòng 203"},
            {"bio": "Bác sĩ nội trú thần kinh, có nhiều công trình nghiên cứu về suy giảm trí nhớ và các bệnh lý thoái hóa thần kinh ở người cao tuổi.", "exp": 9, "room": "Phòng 204"},
            {"bio": "Nhiều năm kinh nghiệm trong công tác phòng chống dịch bệnh, chuyên điều trị viêm gan virus, sốt xuất huyết và các nhiễm trùng cơ hội.", "exp": 16, "room": "Phòng 301"},
            {"bio": "Thạc sĩ Y học lâm sàng nhiệt đới, chuyên sâu về các bệnh lý nhiễm trùng hô hấp và ký sinh trùng đường ruột.", "exp": 11, "room": "Phòng 302"},
            {"bio": "Chuyên gia sản khoa uy tín, hỗ trợ sinh sản, quản lý thai kỳ nguy cơ cao và phẫu thuật nội soi phụ khoa phức tạp.", "exp": 20, "room": "Phòng 303"},
            {"bio": "Chuyên điều trị vô sinh hiếm muộn, phẫu thuật tạo hình phụ khoa và tư vấn chăm sóc sức khỏe tiền hôn nhân.", "exp": 13, "room": "Phòng 304"},
            {"bio": "Chuyên gia lọc máu chu kỳ, quản lý bệnh nhân suy thận mãn tính và điều trị viêm cầu thận cấp.", "exp": 15, "room": "Phòng 401"},
            {"bio": "Nhiều kinh nghiệm vận hành hệ thống lọc máu hiện đại, chăm sóc bệnh nhân trước và sau ghép thận.", "exp": 10, "room": "Phòng 402"},
            {"bio": "Tiến sĩ Y khoa chuyên ngành ung bướu, tư vấn phác đồ điều trị đa mô thức, hóa trị và chăm sóc giảm nhẹ.", "exp": 22, "room": "Phòng 403"},
            {"bio": "Chuyên sâu về tầm soát ung thư sớm đường tiêu hóa và ung thư vú, tư vấn liệu pháp miễn dịch hiện đại.", "exp": 11, "room": "Phòng 404"},
            {"bio": "Chuyên sâu về nha khoa thẩm mỹ, bọc răng sứ, niềng răng mắc cài và khay trong suốt Invisalign.", "exp": 12, "room": "Phòng 501"},
            {"bio": "Bác sĩ chuyên khoa cấy ghép Implant nha khoa, tiểu phẫu răng khôn mọc ngầm không đau bằng máy Piezotome.", "exp": 9, "room": "Phòng 502"},
            {"bio": "Chuyên phẫu thuật nội soi mũi xoang, cắt amidan bằng công nghệ Plasma và điều trị viêm tai giữa cấp.", "exp": 14, "room": "Phòng 503"},
            {"bio": "Khám và điều trị các bệnh lý tai mũi họng trẻ em bẩm sinh, điều trị viêm thanh quản và khản tiếng.", "exp": 8, "room": "Phòng 504"},
            {"bio": "Chuyên phẫu thuật Phaco điều trị đục thủy tinh thể, phẫu thuật khúc xạ (Lasik, Smile) và điều trị Glaucoma.", "exp": 17, "room": "Phòng 601"},
            {"bio": "Chuyên điều trị tật khúc xạ ở trẻ em (cận thị, loạn thị), điều trị bệnh lý võng mạc đái tháo đường.", "exp": 10, "room": "Phòng 602"},
            {"bio": "Chuyên thiết kế các chương trình phục hồi chức năng sau tai biến mạch máu não và chấn thương cột sống phức tạp.", "exp": 15, "room": "Phòng 603"},
            {"bio": "Thế mạnh về vật lý trị liệu chấn thương thể thao, kéo giãn cột sống bằng máy và phục hồi chức năng xương khớp.", "exp": 8, "room": "Phòng 604"},
            {"bio": "Điều trị chuyên sâu các bệnh tự miễn như vảy nến, eczema, viêm da cơ địa và ứng dụng laser thẩm mỹ da.", "exp": 13, "room": "Phòng 701"},
            {"bio": "Chuyên điều trị mụn trứng cá nặng, sẹo rỗ, nám má và tư vấn các liệu trình chăm sóc da khoa học.", "exp": 9, "room": "Phòng 702"},
            {"bio": "Hơn 16 năm công tác tại phòng cấp cứu hồi sức tích cực, chuyên xử trí nhanh các ca sốc phản vệ, đa chấn thương và suy hô hấp.", "exp": 16, "room": "Phòng 703"},
            {"bio": "Bác sĩ hồi sức cấp cứu, thành thạo các kỹ thuật đặt nội khí quản, lọc máu liên tục và cấp cứu ngừng tuần hoàn.", "exp": 10, "room": "Phòng 704"}
        ]
        for i, spec in enumerate(SPECIALTIES_LIST, 1):
            spec_obj = Specialty(name=spec["name"], description=spec["desc"])
            db.add(spec_obj)
            await db.flush()

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

                prof = DOCTOR_PROFILES[idx % len(DOCTOR_PROFILES)]
                doc = Doctor(
                    user_id=dr_user.id,
                    specialty_id=spec_obj.id,
                    bio=prof["bio"],
                    experience_years=prof["exp"],
                    is_approved=True,
                    room_number=prof["room"]
                )
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
