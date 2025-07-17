from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...database.core import get_db
from . import models, service

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=List[models.QuestionListResponse])
async def list_questions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_questions(db=db, limit=limit, offset=offset)


@router.get("/{question_id}", response_model=models.QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
):
    question = await service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/", response_model=models.QuestionResponse, status_code=201)
async def create_question(
    question_in: models.QuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_question(db, question_in)


@router.post("/bulk", response_model=List[models.QuestionResponse])
async def bulk_create_questions(
    payload: models.BulkCreateQuestions,
    db: AsyncSession = Depends(get_db),
):
    return await service.bulk_create_questions(db, payload)


@router.put("/{question_id}", response_model=models.QuestionResponse)
async def update_question(
    question_id: int,
    question_in: models.QuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    question = await service.update_question(db, question_id, question_in)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/{question_id}", status_code=204)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")


@router.post(
    "/search",
    response_model=List[models.QuestionSearchScoredResponse],
)
async def search_similar_questions(
    payload: models.QuestionSearch,
    db: AsyncSession = Depends(get_db),
):
    return await service.search_similar_questions(db, payload.query)



