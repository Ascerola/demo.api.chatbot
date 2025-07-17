from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.core import get_db
from src.v1.bitacora.models import LogResponse
from src.v1.bitacora.service import get_logs_paginated

router = APIRouter()

@router.get("/logs", response_model=dict)
async def get_logs(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    logs, total = await get_logs_paginated(db, limit=limit, offset=offset)
    return {
        "total": total,
        "logs": [LogResponse.from_orm(log) for log in logs]
    }
