from fastapi import APIRouter, Depends, HTTPException, Query
from math import ceil

from app.api.schemas.api_schemas import CaseItem, CasesResponse, PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["cases"])


def get_case_repository():
    raise NotImplementedError("Dependency injection pending Dev 1 interfaces")


@router.get("/cases", response_model=CasesResponse)
async def get_cases(
    upload_id: str | None = Query(default=None),
    responsible_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    case_repository=Depends(get_case_repository),
):
    try:
        items, total = case_repository.find_paginated(
            upload_id=upload_id,
            responsible_id=responsible_id,
            status=status,
            page=page,
            page_size=page_size,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Error querying cases"}},
        )

    return CasesResponse(
        items=[CaseItem(**item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if total else 0,
        ),
    )


@router.get("/cases/{case_id}", response_model=CaseItem)
async def get_case(case_id: str, case_repository=Depends(get_case_repository)):
    case = case_repository.find_by_id(case_id)
    if case is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "CASE_NOT_FOUND", "message": "El caso solicitado no existe"}},
        )
    return CaseItem(**case)
