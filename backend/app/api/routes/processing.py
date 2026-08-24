"""
Processing Routes - Endpoints para procesamiento de casos.

Responsabilidades:
- Recibir solicitudes de procesamiento
- Aplicar reglas de negocio
- Retornar resultados del procesamiento
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from ...infrastructure.catalogs.catalog_service import CatalogService
from ...infrastructure.catalogs.responsible_catalog import ResponsibleCatalog
from ...infrastructure.catalogs.status_catalog import StatusCatalog
from ...infrastructure.catalogs.time_catalog import TimeCatalog
from ...infrastructure.processing.processing_service import ProcessingService
from ...infrastructure.store import store
from ..schemas.processing import (
    CaseResult,
    ProcessingRequest,
    ProcessingResponse,
)

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

# Instancia del Catalog Service
catalog_service = CatalogService(
    status_catalog=StatusCatalog(),
    time_catalog=TimeCatalog(),
    responsible_catalog=ResponsibleCatalog(),
)

# Instancia del Processing Service
processing_service = ProcessingService(catalog_service=catalog_service)


@router.post(
    "/process",
    response_model=ProcessingResponse,
    summary="Procesar casos de un Upload",
    description="Aplica reglas de negocio a los casos de un Upload y retorna resultados.",
)
async def process_cases(request: ProcessingRequest):
    """
    Procesa los casos de un Upload aplicando reglas de negocio.

    El procesamiento incluye:
    1. Filtrar casos por estado (procesables vs no procesables)
    2. Aplicar lookups de catálogos (tiempos, responsables)
    3. Calcular minutos estimados
    4. Retornar resultados detallados

    Args:
        request: Solicitud de procesamiento con upload_id

    Returns:
        ProcessingResponse con los resultados del procesamiento

    Raises:
        404: Si no se encuentra el upload
        500: Si ocurre un error interno
    """
    try:
        # Obtener casos del store
        cases = store.get_cases(request.upload_id)

        if cases is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "UPLOAD_NOT_FOUND",
                    "message": f"Upload con ID {request.upload_id} no encontrado",
                },
            )

        if len(cases) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "EMPTY_UPLOAD",
                    "message": "El upload no contiene casos para procesar",
                },
            )

        # Procesar casos
        result = processing_service.process_cases(
            cases=cases,
            responsible_id=request.responsible_id,
        )

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
