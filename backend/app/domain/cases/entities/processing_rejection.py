from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProcessingRejection(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    processing_id: UUID
    case_id: UUID
    reason_code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
