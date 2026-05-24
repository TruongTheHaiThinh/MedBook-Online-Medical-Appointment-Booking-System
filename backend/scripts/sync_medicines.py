import csv
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import Base
from app.models.medicine import Medicine
from app.models.prescription import Prescription, PrescriptionItem

async def sync_medicines():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Create tables if not exist
        await conn.run_sync(Base.metadata.create_all)

    csv_path = "medicine_dataset.csv"
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    async with async_session() as session:
        # Check if we already have medicines
        result = await session.execute(select(Medicine).limit(1))
        if result.scalar_one_or_none():
            print("Medicines already exist, skipping seed.")
            return

        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            medicines = []
            for row in reader:
                med = Medicine(
                    name=row.get('Name'),
                    category=row.get('Category'),
                    dosage_form=row.get('Dosage Form'),
                    strength=row.get('Strength'),
                    manufacturer=row.get('Manufacturer'),
                    indication=row.get('Indication'),
                    classification=row.get('Classification')
                )
                medicines.append(med)
            
            session.add_all(medicines)
            await session.commit()
            print(f"Successfully added {len(medicines)} medicines.")

if __name__ == "__main__":
    asyncio.run(sync_medicines())
