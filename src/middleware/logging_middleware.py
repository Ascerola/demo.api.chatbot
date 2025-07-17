# src/middleware/logging_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

from src.database.core import get_db
from src.entities.bitacora import Bitacora

class BitacoraLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get DB session from dependency
        async for db in get_db():
            break  # use first yielded session

        # Extract request info
        ip = request.client.host
        method = request.method
        endpoint = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")

        try:
            request_body = await request.body()
            request_body = request_body.decode("utf-8")
            request_body = json.loads(request_body) if request_body else None
        except Exception:
            request_body = None  # Skip if body not JSON-decodable

        # Continue request
        response: Response = await call_next(request)

        # Log to bitacora
        entry = Bitacora(
            ip_address=ip,
            endpoint=endpoint,
            method=method,
            response_status=response.status_code,
            user_agent=user_agent,
            request_body=request_body,
            timestamp=datetime.utcnow()
        )

        db.add(entry)
        await db.commit()

        return response
