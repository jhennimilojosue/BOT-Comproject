"""
Results Routes - Endpoints para consultar resultados de procesamiento.

Responsabilidades:
- Consultar resultados de un procesamiento específico
- Consultar rechazos de un procesamiento específico
- Obtener resumen de procesamiento
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...infrastructure.database.models.processing import ProcessingModel
from ..dependencies import get_db
from ..schemas.processing import ProcessingResponse

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.get(
    "/{processing_id}",
    summary="Obtener resultados de un procesamiento",
    description="Retorna el resumen y resultados de una ejecución de procesamiento.",
)
async def get_processing_results(
    processing_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtiene los resultados de un procesamiento específico.

    Args:
        processing_id: Identificador del procesamiento
        db: Sesión de base de datos

    Returns:
        Resumen del procesamiento con estadísticas
    """
    try:
        processing = db.query(ProcessingModel).filter(
            ProcessingModel.id == processing_id
        ).first()

        if not processing:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": f"No se encontró el procesamiento {processing_id}",
                },
            )

        return {
            "processing_id": processing.id,
            "upload_id": processing.upload_id,
            "status": processing.status,
            "total_cases": processing.total_cases,
            "processed_cases": processing.processed_cases,
            "rejected_cases": processing.rejected_cases,
            "created_at": processing.created_at,
            "started_at": processing.started_at,
            "completed_at": processing.completed_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener resultados: {str(e)}",
            },
        )


@router.get(
    "/{processing_id}/rejected",
    summary="Obtener rechazos de un procesamiento",
    description="Retorna la lista de casos rechazados durante el procesamiento.",
)
async def get_processing_rejections(
    processing_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtiene los casos rechazados de un procesamiento específico.

    Args:
        processing_id: Identificador del procesamiento
        db: Sesión de base de datos

    Returns:
        Lista de casos rechazados con sus razones
    """
    try:
        processing = db.query(ProcessingModel).filter(
            ProcessingModel.id == processing_id
        ).first()

        if not processing:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": f"No se encontró el procesamiento {processing_id}",
                },
            )

        # Importar el modelo de rechazos
        from ...infrastructure.database.models.processing_rejection import ProcessingRejectionModel

        rejections = db.query(ProcessingRejectionModel).filter(
            ProcessingRejectionModel.processing_id == processing_id
        ).all()

        rejections_list = [
            {
                "id": r.id,
                "case_code": r.case_code,
                "reason_code": r.reason_code,
                "message": r.message,
                "created_at": r.created_at,
            }
            for r in rejections
        ]

        return {
            "processing_id": processing_id,
            "total_rejections": len(rejections_list),
            "rejections": rejections_list,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener rechazos: {str(e)}",
            },
        )
