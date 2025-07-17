from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    question_text: str
    answer_text: str
    active: Optional[bool] = True


class QuestionCreate(QuestionBase):
    """Used when creating a new question via POST. Embedding will be generated internally."""
    pass  # No need to define `embedding` here


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    active: Optional[bool] = None
    # Optional: you could allow re-generating the embedding manually if needed
    # embedding: Optional[List[float]] = Field(default=None, min_items=384, max_items=384)


class QuestionResponse(QuestionBase):
    id: int
    embedding: List[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkCreateQuestions(BaseModel):
    questions: List[QuestionCreate]


class QuestionListResponse(BaseModel):
    id: int
    question_text: str
    answer_text: str
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionSearch(BaseModel):
    query: str


class QuestionSearchScoredResponse(BaseModel):
    id: int
    question_text: str
    answer_text: str
    score: float





