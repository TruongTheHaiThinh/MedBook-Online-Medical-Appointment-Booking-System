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
from app.models import User, Specialty, Doctor
from sqlalchemy import select

DOCTOR_NAMES = [
    "Phạm Hoàng Nam", "Nguyễn Tấn Phát", "Lê Thị Mai", "Trần Minh Quân",
    "Hoàng Đức Hải", "Vũ Thanh Hằng", "Đỗ Quốc Bảo", "Nguyễn Mỹ Linh",
    "Phan Thanh Bình", "Trần Thị Hồng", "Lý Gia Kiệt", "Nguyễn Hữu Đạt",
    "Lê Huy Hoàng", "Nguyễn Bích Ngọc", "Bùi Anh Tuấn", "Phạm Minh Trí",
    "Trần Ngọc Lan", "Nguyễn Quang Huy", "Đặng Văn Lâm", "Lê Thu Thảo",
    "Vũ Hoàng Long", "Nguyễn Bảo Châu", "Hoàng Kim Oanh", "Trần Việt Anh",
    "Phạm Hùng Cường", "Đỗ Thu Trang", "Nguyễn Duy Mạnh", "Lê Công Vinh"
]

async def run_update():
    print("--- UPDATING ACCOUNT NAMES IN DATABASE ---")
    async with AsyncSessionLocal() as db:
        # 1. Update Cashier
        result_cashier = await db.execute(select(User).where(User.role == "cashier_admin"))
        cashiers = result_cashier.scalars().all()
        for cashier in cashiers:
            old_name = cashier.full_name
            if not old_name.startswith("Thu Ngân -"):
                # Clean name if it is default
                clean_name = old_name.replace("Thu ngan chinh", "Nguyễn Minh Khuê").replace("Thu ngân chính", "Nguyễn Minh Khuê")
                cashier.full_name = f"Thu Ngân - {clean_name}"
                print(f"Updated Cashier: '{old_name}' -> '{cashier.full_name}'")

        # 2. Update Admin
        result_admin = await db.execute(select(User).where(User.role == "hr_admin"))
        admins = result_admin.scalars().all()
        for admin in admins:
            old_name = admin.full_name
            if old_name in ["Quan tri vien", "Quản trị viên", "Quản trị hệ thống", "Admin"]:
                admin.full_name = "Quản trị viên Trần Quốc Bảo"
                print(f"Updated Admin: '{old_name}' -> '{admin.full_name}'")

        # 3. Update Doctors
        # Fetch all doctors ordered by ID to apply names consistently
        result_docs = await db.execute(select(User).where(User.role == "doctor").order_by(User.id))
        doctors = result_docs.scalars().all()
        for idx, doc_user in enumerate(doctors):
            old_name = doc_user.full_name
            new_name = f"Bác sĩ {DOCTOR_NAMES[idx % len(DOCTOR_NAMES)]}"
            doc_user.full_name = new_name
            print(f"Updated Doctor {idx+1}: '{old_name}' -> '{new_name}'")

        await db.commit()
        print("--- UPDATE COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(run_update())
