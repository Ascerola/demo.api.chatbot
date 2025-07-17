# src/v1/bitacora/service.py

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple
from src.entities.bitacora import Bitacora


async def get_logs_paginated(db: AsyncSession, limit: int, offset: int) -> Tuple[List[Bitacora], int]:
    # Get total count
    total_result = await db.execute(select(func.count()).select_from(Bitacora))
    total = total_result.scalar()

    # Get logs
    result = await db.execute(
        select(Bitacora)
        .order_by(Bitacora.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    logs = result.scalars().all()
    return logs, total
