from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ResponsibleItem(BaseModel):
    id: UUID
    name: str


class ResponsiblesResponse(BaseModel):
    items: list[ResponsibleItem]
    total: int


class UploadResponse(BaseModel):
    id: UUID
    file_name: str
    status: str
    created_at: datetime


class ProcessCasesRequest(BaseModel):
    upload_id: UUID = Field(..., description="Upload to process")
    responsible_id: UUID = Field(..., description="Selected responsible")


class ProcessCasesSummary(BaseModel):
    total_cases: int
    processed_cases: int
    rejected_cases: int


class ProcessCasesResponse(BaseModel):
    processing_id: UUID
    upload_id: UUID
    responsible_id: UUID
    status: str
    summary: ProcessCasesSummary


class ProcessingResultItem(BaseModel):
    case_id: UUID
    case_code: str
    responsible_name: str
    project: str
    final_category: str
    estimated_minutes: int
    description: str


class ProcessingResponse(BaseModel):
    processing_id: UUID
    upload_id: UUID
    responsible_id: UUID
    status: str
    summary: ProcessCasesSummary
    results: list[ProcessingResultItem]


class RejectedCaseItem(BaseModel):
    case_id: UUID
    case_code: str
    reason_code: str
    message: str


class RejectedCasesResponse(BaseModel):
    items: list[RejectedCaseItem]
    total: int


class CaseItem(BaseModel):
    id: UUID
    case_code: str
    responsible_name: str
    user_name: Optional[str] = None
    project: str
    status: str
    final_category: str
    registered_at: datetime
    description: str
    solution: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class CasesResponse(BaseModel):
    items: list[CaseItem]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: dict
