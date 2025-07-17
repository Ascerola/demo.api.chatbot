# src/entities/bitacora.py

from sqlalchemy import Column, String, Integer, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database.core import Base

class Bitacora(Base):
    __tablename__ = "bitacora"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_address = Column(String(45), nullable=False)
    endpoint = Column(Text, nullable=False)
    method = Column(String(10), nullable=False)
    user_agent = Column(Text)
    request_body = Column(JSON)
    response_status = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<Bitacora(ip={self.ip_address}, endpoint={self.endpoint}, "
            f"status={self.response_status}, time={self.timestamp})>"
        )
