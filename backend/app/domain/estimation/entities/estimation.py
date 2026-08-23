from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Estimation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    estimated_minutes: int = Field(..., ge=0)
    description: str = Field(..., min_length=1)
    min_range: int = Field(..., ge=0)
    max_range: int = Field(..., ge=0)
    status: str = Field(default="VALID")
    rejection_reason: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
