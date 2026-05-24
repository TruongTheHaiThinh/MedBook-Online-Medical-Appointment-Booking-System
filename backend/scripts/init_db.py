import asyncio
import uuid
from sqlalchemy import select
from app.database import engine, Base, get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.core.security import hash_password

async def init_db():
    print("Initializing database with new schema requirements...")
    async with engine.begin() as conn:
        # Recreate tables to apply schema changes (caution: clears all data)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.connect() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            # 1. Admin
            admin = User(
                email="admin@medbook.com",
                password_hash=hash_password("Admin@123"),
                full_name="Quản trị viên",
                phone="0000000000",
                address="Hệ thống MedBook",
                role="admin"
            )
            db.add(admin)
            
            # 2. Doctor
            doctor_user = User(
                email="doctor1@medbook.com",
                password_hash=hash_password("Doctor@123"),
                full_name="Bác sĩ Nguyễn Văn A",
                phone="0111111111",
                address="Quận 10, TP.HCM",
                role="doctor"
            )
            db.add(doctor_user)
            await db.flush()
            
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                is_approved=True,
                experience_years=10,
                bio="Bác sĩ chuyên khoa nội, giàu kinh nghiệp."
            )
            db.add(doctor_profile)
            
            # 3. Patient
            patient = User(
                email="patient1@gmail.com",
                password_hash=hash_password("Patient@123"),
                full_name="Bệnh nhân Demo",
                phone="0912345678",
                address="Quận 3, TP.HCM",
                role="patient"
            )
            db.add(patient)
            
            await db.commit()
            print("Successfully created default accounts:")
            print("- Admin: admin@medbook.com / Admin@123")
            print("- Doctor: doctor1@medbook.com / Doctor@123")
            print("- Patient: patient1@gmail.com / Patient@123")

if __name__ == "__main__":
    asyncio.run(init_db())
