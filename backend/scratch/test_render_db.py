import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_rows():
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/medbook")
    try:
        engine = create_async_engine(url, echo=False)
        async with engine.connect() as conn:
            # Check users
            try:
                result_users = await conn.execute(text("SELECT count(*) FROM users"))
                users_count = result_users.scalar()
                print(f"Users count: {users_count}")
            except Exception as e:
                print(f"Error checking users (maybe table doesn't exist): {e}")

            # Check medicines
            try:
                result_meds = await conn.execute(text("SELECT count(*) FROM medicines"))
                meds_count = result_meds.scalar()
                print(f"Medicines count: {meds_count}")
            except Exception as e:
                print(f"Error checking medicines: {e}")
                
            sys.stdout.flush()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(check_rows())
