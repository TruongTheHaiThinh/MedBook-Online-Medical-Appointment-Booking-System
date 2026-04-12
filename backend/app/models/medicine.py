import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100))
    dosage_form = Column(String(100))
    strength = Column(String(50))
    manufacturer = Column(String(255))
    indication = Column(Text)
    classification = Column(String(50))
