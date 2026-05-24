import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def unlock():
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/medbook")
    print("Terminating other database sessions to release locks...")
    sys.stdout.flush()
    try:
        # Note: we use isolation_level="AUTOCOMMIT" to allow pg_terminate_backend
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
        async with engine.connect() as conn:
            # Terminate other backends
            q = text("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = current_database() 
                  AND pid <> pg_backend_pid()
            """)
            result = await conn.execute(q)
            rows = result.all()
            print(f"Terminated {len(rows)} other sessions.")
            sys.stdout.flush()
    except Exception as e:
        print(f"Failed to release locks: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(unlock())
