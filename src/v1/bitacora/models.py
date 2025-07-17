from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class LogResponse(BaseModel):
    id: UUID
    ip_address: str
    endpoint: str
    method: str
    user_agent: Optional[str] = None
    request_body: Optional[dict] = None
    response_status: Optional[int]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
