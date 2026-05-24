import asyncio
import sys
import os

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User))
        users = res.scalars().all()
        print("--- ALL USERS IN DB ---")
        for u in users:
            print(f"Email: {u.email}, Role: {u.role}, Name: {u.full_name}")
        print("-----------------------")

if __name__ == "__main__":
    asyncio.run(main())
