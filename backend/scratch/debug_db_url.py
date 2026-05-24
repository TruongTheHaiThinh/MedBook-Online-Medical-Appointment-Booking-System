import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Set DATABASE_URL if not set
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/medbook")

from app.database import engine
print(f"Engine URL configured in app.database: {engine.url}")
sys.stdout.flush()
