# src/v1/questions/service.py

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy.orm import load_only
from typing import List, Optional, Dict

from . import models
from src.entities.question import Question
from .utils.embeddings import generate_embedding
from .models import QuestionListResponse

SIMILARITY_THRESHOLD = 0.70
TOP_K = 5


async def create_question(
    db: AsyncSession,
    data: models.QuestionCreate
) -> Question:
    # 1) Combine question and answer into one string
    combined = f"{data.question_text} — {data.answer_text}"
    # 2) Generate embedding over the combined text
    embedding = generate_embedding(combined)

    question = Question(
        question_text=data.question_text,
        answer_text=data.answer_text,
        embedding=embedding,
        active=data.active,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def bulk_create_questions(
    db: AsyncSession,
    payload: models.BulkCreateQuestions
) -> List[Question]:
    to_insert = []
    for q in payload.questions:
        combined = f"{q.question_text} — {q.answer_text}"
        embedding = generate_embedding(combined)
        to_insert.append({
            "question_text": q.question_text,
            "answer_text": q.answer_text,
            "embedding": embedding,
            "active": q.active if q.active is not None else True,
        })

    stmt = insert(Question).values(to_insert).returning(Question)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalars().all()


async def get_question_by_id(
    db: AsyncSession,
    question_id: int
) -> Optional[Question]:
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    return result.scalar_one_or_none()


async def list_questions(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> List[QuestionListResponse]:
    result = await db.execute(
        select(
            Question.id,
            Question.question_text,
            Question.answer_text,
            Question.active,
            Question.created_at,
            Question.updated_at,
        )
        .order_by(Question.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    return [QuestionListResponse(**row._mapping) for row in rows]


async def update_question(
    db: AsyncSession,
    question_id: int,
    data: models.QuestionUpdate
) -> Optional[Question]:
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        return None

    updates = data.model_dump(exclude_unset=True)

    # If either text changes, regenerate the combined embedding
    if "question_text" in updates or "answer_text" in updates:
        new_q = updates.get("question_text", question.question_text)
        new_a = updates.get("answer_text", question.answer_text)
        combined = f"{new_q} — {new_a}"
        updates["embedding"] = generate_embedding(combined)

    for field, value in updates.items():
        setattr(question, field, value)

    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(
    db: AsyncSession,
    question_id: int
) -> bool:
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        return False

    await db.delete(question)
    await db.commit()
    return True


async def search_similar_questions(
    db: AsyncSession,
    query: str,
    top_k: int = TOP_K,
) -> List[Dict]:
    # 1) Generate embedding for the user query
    q_emb = generate_embedding(query)

    # 2) Retrieve top_k candidates by cosine distance
    stmt = (
        select(
            Question,
            Question.embedding.cosine_distance(q_emb).label("dist")
        )
        .options(load_only(Question.id, Question.question_text, Question.answer_text))
        .order_by("dist")
        .limit(top_k)
    )
    results = await db.execute(stmt)
    rows = results.all()  # List of (Question, dist)

    # 3) Convert distance to similarity score (1 - dist)
    scored = [
        (q, 1.0 - dist if dist is not None else 0.0)
        for q, dist in rows
    ]

    # 4) If best similarity is below threshold, return fallback with real score
    if not scored or scored[0][1] < SIMILARITY_THRESHOLD:
        best = scored[0][1] if scored else 0.0
        return [{
            "id": -1,
            "question_text": query,
            "answer_text": "Lo siento, no encontré una respuesta relacionada con tu consulta.",
            "score": best,
        }]

    # 5) Otherwise, return all above threshold
    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "answer_text": q.answer_text,
            "score": sim,
        }
        for q, sim in scored
        if sim >= SIMILARITY_THRESHOLD
    ]
