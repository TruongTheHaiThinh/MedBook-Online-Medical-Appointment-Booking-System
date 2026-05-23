import asyncio
import os
import sys

# Add current dir to path to find app
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_user():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == 'cashier@medbook.vn'))
        user = res.scalar_one_or_none()
        if user:
            print(f"FOUND: {user.email}, ROLE: {user.role}")
        else:
            res = await db.execute(select(User).where(User.email == 'cashier1@medbook.vn'))
            user = res.scalar_one_or_none()
            if user:
                print(f"FOUND: {user.email}, ROLE: {user.role}")
            else:
                print("CASHIER USER NOT FOUND IN DB")

if __name__ == "__main__":
    asyncio.run(check_user())
