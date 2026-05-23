import asyncio
import csv
import os
import sys
from uuid import uuid4

# Ensure app directory is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.medicine import Medicine

async def import_medicines(csv_file_path: str):
    print(f"Starting medicine import from {csv_file_path}...")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: File {csv_file_path} not found")
        return

    async with AsyncSessionLocal() as db:
        with open(csv_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            batch_size = 500
            batch = []
            
            for row in reader:
                medicine = Medicine(
                    id=uuid4(),
                    name=row['Name'],
                    category=row.get('Category'),
                    dosage_form=row.get('Dosage Form'),
                    strength=row.get('Strength'),
                    manufacturer=row.get('Manufacturer'),
                    indication=row.get('Indication'),
                    classification=row.get('Classification')
                )
                batch.append(medicine)
                count += 1
                
                if len(batch) >= batch_size:
                    db.add_all(batch)
                    await db.commit()
                    batch = []
                    print(f"Imported {count} medicines...")
            
            if batch:
                db.add_all(batch)
                await db.commit()
                
            print(f"Done! Total {count} medicines imported into database.")

if __name__ == "__main__":
    csv_path = "medicine_dataset.csv"
    asyncio.run(import_medicines(csv_path))
