from sqlalchemy import Column, Integer, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pgvector.sqlalchemy import Vector
from datetime import datetime

from ..database.core import Base

class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False, comment="pgvector (384D)")
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Question(id={self.id}, question_text='{self.question_text[:30]}...', active={self.active})>"
