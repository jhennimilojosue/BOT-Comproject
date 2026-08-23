from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Processing(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    upload_id: UUID
    responsible_id: UUID
    status: str = Field(default="PENDING")
    total_cases: int = Field(default=0, ge=0)
    processed_cases: int = Field(default=0, ge=0)
    rejected_cases: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
