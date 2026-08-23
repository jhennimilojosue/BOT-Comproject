from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.api_schemas import (
    ProcessCasesRequest,
    ProcessCasesResponse,
    ProcessCasesSummary,
    ProcessingResponse,
    RejectedCasesResponse,
)
from app.infrastructure.ai.models import AIConfig

router = APIRouter(prefix="/api/v1", tags=["processing"])

PROCESSING_TIMEOUT_SECONDS = 300


def get_processing_repository():
    raise NotImplementedError("Dependency injection pending Dev 1 interfaces")


def get_process_cases_use_case():
    raise NotImplementedError("Dependency injection pending")


@router.post("/cases/process", response_model=ProcessCasesResponse)
async def process_cases(
    request: ProcessCasesRequest,
    process_cases_use_case=Depends(get_process_cases_use_case),
):
    try:
        result = await process_cases_use_case.execute(request, AIConfig())
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "INVALID_CONTEXT", "message": str(e)}},
        )
    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={"error": {"code": "PROCESSING_TIMEOUT", "message": "El procesamiento excedió el tiempo máximo permitido"}},
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Error during processing"}},
        )

    return ProcessCasesResponse(
        processing_id=result.processing_id,
        upload_id=request.upload_id,
        responsible_id=request.responsible_id,
        status=result.status,
        summary=ProcessCasesSummary(
            total_cases=result.total_cases,
            processed_cases=result.processed_cases,
            rejected_cases=result.rejected_cases,
        ),
    )


@router.get("/processing/{processing_id}", response_model=ProcessingResponse)
async def get_processing(processing_id: str, processing_repository=Depends(get_processing_repository)):
    processing = processing_repository.find_by_id_with_results(processing_id)
    if processing is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "PROCESSING_NOT_FOUND", "message": "La ejecución solicitada no existe"}},
        )
    return ProcessingResponse(**processing)


@router.get("/processing/{processing_id}/rejected", response_model=RejectedCasesResponse)
async def get_rejected(processing_id: str, processing_repository=Depends(get_processing_repository)):
    processing = processing_repository.find_by_id(processing_id)
    if processing is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "PROCESSING_NOT_FOUND", "message": "La ejecución solicitada no existe"}},
        )

    rejections = processing_repository.find_rejections_by_processing_id(processing_id)
    items = [
        {
            "case_id": r["case_id"],
            "case_code": r["case_code"],
            "reason_code": r["reason_code"],
            "message": r["message"],
        }
        for r in rejections
    ]
    return RejectedCasesResponse(items=items, total=len(items))


@router.get("/processing/{processing_id}/export")
async def export_results(processing_id: str, processing_repository=Depends(get_processing_repository)):
    processing = processing_repository.find_by_id(processing_id)
    if processing is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "PROCESSING_NOT_FOUND", "message": "La ejecución solicitada no existe"}},
        )

    results = processing_repository.find_results_by_processing_id(processing_id)

    from io import BytesIO

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["Código", "Responsable", "Proyecto", "Categoría", "Estado", "Tiempo estimado", "Descripción"])

    for r in results:
        ws.append([
            r.get("case_code"),
            r.get("responsible_name"),
            r.get("project"),
            r.get("final_category"),
            r.get("status"),
            r.get("estimated_minutes"),
            r.get("description"),
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=processing_{processing_id}.xlsx"},
    )
