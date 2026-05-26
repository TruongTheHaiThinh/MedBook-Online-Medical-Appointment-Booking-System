import asyncio
import os
import sys
import io

# Setup sys.path to import app modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Set stdout encoding to utf-8 to prevent Windows terminal print crashes
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.database import AsyncSessionLocal
from app.models import Specialty
from sqlalchemy import select

SPECIALTIES_MAPPING = {
    "Khoa Tim mach": {
        "name": "Khoa Tim mạch",
        "desc": "Chẩn đoán và điều trị chuyên sâu các bệnh lý về tim mạch, huyết áp và mạch máu bằng công nghệ y khoa tiên tiến."
    },
    "Khoa Tim mạch": {
        "name": "Khoa Tim mạch",
        "desc": "Chẩn đoán và điều trị chuyên sâu các bệnh lý về tim mạch, huyết áp và mạch máu bằng công nghệ y khoa tiên tiến."
    },
    "Khoa Tieu hoa": {
        "name": "Khoa Tiêu hóa",
        "desc": "Tầm soát, điều trị các bệnh lý đường tiêu hóa, gan mật, kết hợp phương pháp nội soi không đau hiện đại."
    },
    "Khoa Tiêu hóa": {
        "name": "Khoa Tiêu hóa",
        "desc": "Tầm soát, điều trị các bệnh lý đường tiêu hóa, gan mật, kết hợp phương pháp nội soi không đau hiện đại."
    },
    "Khoa Chan thuong chinh hinh": {
        "name": "Khoa Chấn thương chỉnh hình",
        "desc": "Phẫu thuật chấn thương cơ xương khớp, phục hồi vận động và tái tạo chức năng sau chấn thương."
    },
    "Khoa Chấn thương chỉnh hình": {
        "name": "Khoa Chấn thương chỉnh hình",
        "desc": "Phẫu thuật chấn thương cơ xương khớp, phục hồi vận động và tái tạo chức năng sau chấn thương."
    },
    "Khoa Noi Than kinh": {
        "name": "Khoa Nội thần kinh",
        "desc": "Điều trị các bệnh lý thần kinh, đau đầu, đột quỵ, rối loạn giấc ngủ và các hội chứng suy giảm trí nhớ."
    },
    "Khoa Nội thần kinh": {
        "name": "Khoa Nội thần kinh",
        "desc": "Điều trị các bệnh lý thần kinh, đau đầu, đột quỵ, rối loạn giấc ngủ và các hội chứng suy giảm trí nhớ."
    },
    "Khoa Truyen nhiem": {
        "name": "Khoa Truyền nhiễm",
        "desc": "Chẩn đoán, phòng ngừa và điều trị các bệnh truyền nhiễm nguy hiểm, dịch bệnh theo mùa và tiêm chủng bảo vệ cơ thể."
    },
    "Khoa Truyền nhiễm": {
        "name": "Khoa Truyền nhiễm",
        "desc": "Chẩn đoán, phòng ngừa và điều trị các bệnh truyền nhiễm nguy hiểm, dịch bệnh theo mùa và tiêm chủng bảo vệ cơ thể."
    },
    "Khoa San phu khoa": {
        "name": "Khoa Sản phụ khoa",
        "desc": "Chăm sóc sức khỏe thai kỳ toàn diện, điều trị phụ khoa và tư vấn kế hoạch hóa gia đình tận tâm."
    },
    "Khoa Sản phụ khoa": {
        "name": "Khoa Sản phụ khoa",
        "desc": "Chăm sóc sức khỏe thai kỳ toàn diện, điều trị phụ khoa và tư vấn kế hoạch hóa gia đình tận tâm."
    },
    "Khoa Than - Loc mau": {
        "name": "Khoa Thận - Lọc máu",
        "desc": "Điều trị suy thận cấp và mãn tính, lọc máu chu kỳ bằng hệ thống màng lọc thế hệ mới an toàn tuyệt đối."
    },
    "Khoa Thận - Lọc máu": {
        "name": "Khoa Thận - Lọc máu",
        "desc": "Điều trị suy thận cấp và mãn tính, lọc máu chu kỳ bằng hệ thống màng lọc thế hệ mới an toàn tuyệt đối."
    },
    "Khoa Ung buou": {
        "name": "Khoa Ung bướu",
        "desc": "Tầm soát ung thư sớm, tư vấn phác đồ điều trị đa mô thức và đồng hành chăm sóc giảm nhẹ cho người bệnh."
    },
    "Khoa Ung bướu": {
        "name": "Khoa Ung bướu",
        "desc": "Tầm soát ung thư sớm, tư vấn phác đồ điều trị đa mô thức và đồng hành chăm sóc giảm nhẹ cho người bệnh."
    },
    "Khoa Rang Ham Mat": {
        "name": "Khoa Răng Hàm Mặt",
        "desc": "Chăm sóc và điều trị các bệnh răng miệng, nha khoa thẩm mỹ chất lượng cao, phục hình răng sứ không đau."
    },
    "Khoa Răng Hàm Mặt": {
        "name": "Khoa Răng Hàm Mặt",
        "desc": "Chăm sóc và điều trị các bệnh răng miệng, nha khoa thẩm mỹ chất lượng cao, phục hình răng sứ không đau."
    },
    "Khoa Tai Mui Hong": {
        "name": "Khoa Tai Mũi Họng",
        "desc": "Điều trị hiệu quả các bệnh lý tai mũi họng cấp và mãn tính ở cả người lớn và trẻ em bằng kỹ thuật nội soi."
    },
    "Khoa Tai Mũi Họng": {
        "name": "Khoa Tai Mũi Họng",
        "desc": "Điều trị hiệu quả các bệnh lý tai mũi họng cấp và mãn tính ở cả người lớn và trẻ em bằng kỹ thuật nội soi."
    },
    "Khoa Mat": {
        "name": "Khoa Mắt",
        "desc": "Khám điều trị các tật khúc xạ, phẫu thuật đục thủy tinh thể và bảo vệ thị lực toàn diện."
    },
    "Khoa Mắt": {
        "name": "Khoa Mắt",
        "desc": "Khám điều trị các tật khúc xạ, phẫu thuật đục thủy tinh thể và bảo vệ thị lực toàn diện."
    },
    "Khoa Phuc hoi chuc nang": {
        "name": "Khoa Phục hồi chức năng",
        "desc": "Thiết kế bài tập chuyên biệt giúp phục hồi khả năng vận động sau tai biến, phẫu thuật hoặc chấn thương cột sống."
    },
    "Khoa Phục hồi chức năng": {
        "name": "Khoa Phục hồi chức năng",
        "desc": "Thiết kế bài tập chuyên biệt giúp phục hồi khả năng vận động sau tai biến, phẫu thuật hoặc chấn thương cột sống."
    },
    "Khoa Da lieu": {
        "name": "Khoa Da liễu",
        "desc": "Điều trị chuyên sâu các bệnh lý da liễu bẩm sinh, viêm da, mụn trứng cá và chăm sóc thẩm mỹ da an toàn."
    },
    "Khoa Da liễu": {
        "name": "Khoa Da liễu",
        "desc": "Điều trị chuyên sâu các bệnh lý da liễu bẩm sinh, viêm da, mụn trứng cá và chăm sóc thẩm mỹ da an toàn."
    },
    "Khoa Cap cuu": {
        "name": "Khoa Cấp cứu",
        "desc": "Tiếp nhận và xử trí nhanh chóng, kịp thời các ca bệnh khẩn cấp 24/7 với trang thiết bị hồi sức hiện đại nhất."
    },
    "Khoa Cấp cứu": {
        "name": "Khoa Cấp cứu",
        "desc": "Tiếp nhận và xử trí nhanh chóng, kịp thời các ca bệnh khẩn cấp 24/7 với trang thiết bị hồi sức hiện đại nhất."
    }
}

async def run_update():
    print("--- UPDATING SPECIALTIES IN DATABASE ---")
    async with AsyncSessionLocal() as db:
        # Fetch all specialties
        result = await db.execute(select(Specialty))
        specialties = result.scalars().all()
        
        updated_count = 0
        for spec in specialties:
            old_name = spec.name
            match = SPECIALTIES_MAPPING.get(old_name) or SPECIALTIES_MAPPING.get(old_name.strip())
            if match:
                spec.name = match["name"]
                spec.description = match["desc"]
                try:
                    print(f"Updated: '{old_name}' -> '{spec.name}'")
                except Exception:
                    pass
                updated_count += 1
            else:
                if spec.description.startswith("Khám chuyên sâu") or spec.description.startswith("Kham chuyen sau"):
                    spec.description = f"Chuyên khoa {spec.name} cung cấp dịch vụ khám, chẩn đoán và điều trị chất lượng cao với các bác sĩ chuyên khoa đầu ngành."
                    try:
                        print(f"Updated description for unmatched spec: '{spec.name}'")
                    except Exception:
                        pass
                    updated_count += 1
                    
        await db.commit()
        print(f"--- UPDATE COMPLETED: {updated_count} specialties updated successfully. ---")

if __name__ == "__main__":
    asyncio.run(run_update())
