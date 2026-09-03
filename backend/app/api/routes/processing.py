"""
Processing Routes - Endpoints para procesamiento de casos.

Responsabilidades:
- Recibir solicitudes de procesamiento
- Aplicar reglas de negocio
- Retornar resultados del procesamiento
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...domain.entities.processing import Processing, ProcessingStatus
from ...infrastructure.catalogs.catalog_service import CatalogService
from ...infrastructure.catalogs.responsible_catalog import ResponsibleCatalog
from ...infrastructure.catalogs.status_catalog import StatusCatalog
from ...infrastructure.catalogs.time_catalog import TimeCatalog
from ...infrastructure.processing.processing_service import ProcessingService
from ...infrastructure.repositories.case_repository import SQLAlchemyCaseRepository
from ...infrastructure.repositories.processing_repository import SQLAlchemyProcessingRepository
from ..dependencies import get_db
from ..schemas.processing import (
    CaseResult,
    ProcessingRequest,
    ProcessingResponse,
)

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

# Instancias globales de servicios
_catalog_service = None
_processing_service = None


def _get_catalog_service() -> CatalogService:
    global _catalog_service
    if _catalog_service is None:
        _catalog_service = CatalogService(
            status_catalog=StatusCatalog(),
            time_catalog=TimeCatalog(),
            responsible_catalog=ResponsibleCatalog(),
        )
    return _catalog_service


def _get_processing_service() -> ProcessingService:
    global _processing_service
    if _processing_service is None:
        _processing_service = ProcessingService(
            catalog_service=_get_catalog_service()
        )
    return _processing_service


@router.post(
    "/process",
    response_model=ProcessingResponse,
    summary="Procesar casos de un Upload",
    description="Aplica reglas de negocio a los casos de un Upload y retorna resultados.",
)
async def process_cases(
    request: ProcessingRequest,
    db: Session = Depends(get_db),
):
    """
    Procesa los casos de un Upload aplicando reglas de negocio.

    Args:
        request: Solicitud de procesamiento con upload_id
        db: Sesión de base de datos

    Returns:
        ProcessingResponse con los resultados del procesamiento
    """
    try:
        processing_svc = _get_processing_service()

        # Obtener casos del upload desde PostgreSQL
        case_repo = SQLAlchemyCaseRepository(db)
        cases = case_repo.find_by_upload(request.upload_id)

        if not cases:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "UPLOAD_NOT_FOUND",
                    "message": f"No se encontraron casos para el upload {request.upload_id}",
                },
            )

        # Convertir entidades de dominio a diccionarios para el ProcessingService
        cases_dict = []
        for case in cases:
            cases_dict.append({
                "case_code": case.case_code,
                "case_type": case.case_type.value if case.case_type else None,
                "status": case.status,
                "final_category": case.final_category,
                "responsible_name": case.responsible_name,
            })

        # Si se proporciona responsible_name, filtrar casos por responsable
        if request.responsible_name:
            cases_dict = [c for c in cases_dict if c.get("responsible_name") == request.responsible_name]

        # Procesar casos
        result = processing_svc.process_cases(
            cases=cases_dict,
            responsible_id=request.responsible_id,
        )

        # Crear registro de Processing en PostgreSQL
        processing = Processing(
            upload_id=request.upload_id,
            responsible_id=request.responsible_id,
            status=ProcessingStatus.COMPLETED,
            total_cases=result.total_cases,
            processed_cases=result.processed_cases,
            rejected_cases=result.rejected_cases,
        )

        processing_repo = SQLAlchemyProcessingRepository(db)
        processing_repo.save(processing)

        # Convertir resultados a schemas
        case_results = [
            CaseResult(
                case_code=r.case_code,
                case_type=r.case_type,
                status=r.status,
                is_processable=r.is_processable,
                rejection_reason=r.rejection_reason,
                estimated_minutes=r.estimated_minutes,
                responsible_name=r.responsible_name,
            )
            for r in result.results
        ]

        return ProcessingResponse(
            processing_id=result.processing_id,
            total_cases=result.total_cases,
            processed_cases=result.processed_cases,
            rejected_cases=result.rejected_cases,
            results=case_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al procesar casos: {str(e)}",
            },
        )



