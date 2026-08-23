from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExcelCaseDTO(BaseModel):
    case_code: str = Field(..., min_length=1, max_length=50)
    responsible_name: str = Field(..., min_length=1, max_length=200)
    user_name: Optional[str] = Field(default=None, max_length=200)
    project: str = Field(..., min_length=1, max_length=200)
    registered_at: datetime
    status: str = Field(..., min_length=1, max_length=100)
    final_category: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    solution: str = Field(..., min_length=1)


class ProcessableCaseDTO(BaseModel):
    case_id: UUID
    case_code: str
    responsible_name: str
    project: str
    registered_at: datetime
    status: str
    final_category: str
    description: str
    solution: str


class CaseRejectionDTO(BaseModel):
    case_code: str
    reason_code: str
    message: str


class ProcessCasesRequest(BaseModel):
    upload_id: UUID
    processing_id: UUID
    responsible_id: UUID


class ProcessCasesResponse(BaseModel):
    processing_id: UUID
    total_cases: int
    processed_cases: int
    rejected_cases: int
    status: str
    created_at: datetime
