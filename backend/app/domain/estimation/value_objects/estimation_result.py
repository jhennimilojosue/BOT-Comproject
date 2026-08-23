from typing import Optional

from pydantic import BaseModel, Field


class EstimationResult(BaseModel):
    estimated_minutes: int = Field(..., ge=0)
    description: str = Field(..., min_length=1)
    status: str = Field(default="VALID")
    rejection_reason: Optional[str] = Field(default=None)
