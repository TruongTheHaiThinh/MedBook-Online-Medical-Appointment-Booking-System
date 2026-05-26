import asyncio
import os
import sys
import io

# Setup sys.path to import app modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Set stdout encoding to utf-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.database import AsyncSessionLocal
from app.models import User, Doctor
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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

async def run_update():
    print("--- UPDATING DOCTOR PROFILES IN DATABASE ---")
    async with AsyncSessionLocal() as db:
        # Fetch all Doctor profiles and load their user relation
        result = await db.execute(select(Doctor).options(selectinload(Doctor.user)))
        doctors = result.scalars().all()
        
        updated_count = 0
        for doc in doctors:
            user = doc.user
            if not user or not user.email:
                continue
            
            email = user.email.strip().lower()
            # Check if email is pk{i}{suffix}@medbook.com
            if email.startswith("pk") and email.endswith("@medbook.com"):
                try:
                    parts = email.replace("pk", "").split("@")[0]
                    suffix = "b" if parts.endswith("b") else ""
                    num_str = parts.replace("b", "")
                    i = int(num_str)
                    
                    idx = (i - 1) * 2 + (1 if suffix == "b" else 0)
                    if 0 <= idx < len(DOCTOR_PROFILES):
                        prof = DOCTOR_PROFILES[idx]
                        doc.bio = prof["bio"]
                        doc.experience_years = prof["exp"]
                        doc.room_number = prof["room"]
                        print(f"Updated Profile for {user.full_name} ({email}): Exp: {doc.experience_years}, Room: {doc.room_number}")
                        updated_count += 1
                except Exception as e:
                    print(f"Error parsing doctor email {email}: {e}")
                    
        await db.commit()
        print(f"--- UPDATE COMPLETED: {updated_count} doctor profiles updated. ---")

if __name__ == "__main__":
    asyncio.run(run_update())
