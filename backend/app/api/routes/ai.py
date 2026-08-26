"""
AI Routes - Endpoints para servicios de IA.

Responsabilidades:
- Generar descripciones usando IA
- Estimar tiempos usando IA
- Procesar casos por responsable con WebSocket
- Consultar catálogo de tiempos
- Consultar resultados guardados
"""

import time
import uuid
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...api.schemas.ai import (
    AIResultResponse,
    CatalogCategory,
    CatalogResponse,
    GetResultsResponse,
    ProcessResponsibleRequest,
    ProcessResponsibleResponse,
    ProcessingSummary,
    WebSocketMessage,
)
from ...api.websocket import ConnectionManager
from ...infrastructure.ai.ai_service import AIService
from ...infrastructure.ai.models import AIConfig
from ...infrastructure.ai.ollama_provider import OllamaProvider
from ...infrastructure.ai.response_parser import ResponseParser
from ..dependencies import get_db
from ...infrastructure.database.models.case import CaseModel
from ...infrastructure.database.models.processing import ProcessingModel
from ...infrastructure.repositories.ai_result_repository import SQLAlchemyAIResultRepository
from ...infrastructure.repositories.catalogo_tiempos_repository import SQLAlchemyCatalogoTiempoRepository

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Instancia del parser
parser = ResponseParser()

# WebSocket manager global
ws_manager = ConnectionManager()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Endpoint WebSocket para progreso en tiempo real.

    Args:
        client_id: ID único del cliente
    """
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            # Mantener conexión viva
            data = await websocket.receive_text()
            # Echo para keepalive
            if data == "ping":
                await ws_manager.send_progress(client_id, {"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)


# ============================================================================
# PROCESS RESPONSIBLE ENDPOINT (ASYNC)
# ============================================================================


@router.post(
    "/process-responsible",
    response_model=ProcessResponsibleResponse,
    summary="Procesar casos de un responsable con IA",
    description="Procesa todos los casos de un responsable que estén en el catálogo, generando descripción con IA y tiempo del catálogo.",
)
async def process_responsible(
    request: ProcessResponsibleRequest,
    client_id: Optional[str] = Query(None, description="ID del cliente WebSocket para progreso"),
    db: Session = Depends(get_db),
):
    """
    Procesa todos los casos de un responsable seleccionado.

    Flujo:
    1. Carga catálogo de tiempos desde PostgreSQL
    2. Consulta casos del responsable (Requerimientos + Incidentes)
    3. Filtra casos que están en el catálogo
    4. Para cada caso: genera descripción con IA + tiempo del catálogo
    5. Guarda resultados en ai_results
    6. Retorna resumen

    Args:
        request: Datos del request (upload_id, responsible_name)
        client_id: ID del cliente WebSocket (opcional)
        db: Sesión de base de datos

    Returns:
        Respuesta con resultados y resumen
    """
    try:
        # Verificar servicio de IA
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible",
                },
            )

        # Cargar catálogo de tiempos
        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        all_catalog_paths = catalog_repo.get_all_paths()

        if not all_catalog_paths:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "CATALOG_EMPTY",
                    "message": "El catálogo de tiempos está vacío",
                },
            )

        # Consultar casos del responsable (Requerimientos + Incidentes)
        cases = (
            db.query(CaseModel)
            .filter(
                CaseModel.upload_id == request.upload_id,
                CaseModel.responsible_name == request.responsible_name,
                CaseModel.case_type.in_(["Incidente", "Requerimiento"]),
            )
            .all()
        )

        if not cases:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NO_CASES_FOUND",
                    "message": f"No se encontraron casos para el responsable '{request.responsible_name}'",
                },
            )

        # Filtrar casos que están en el catálogo
        processable_cases = []
        for case in cases:
            if catalog_repo.find_by_path(case.final_category):
                processable_cases.append(case)

        if not processable_cases:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NO_CASES_IN_CATALOG",
                    "message": "Ninguno de los casos está en el catálogo de tiempos",
                },
            )

        # Crear processing_id único
        processing_id = uuid.uuid4()

        # Crear registro de processing
        processing = ProcessingModel(
            upload_id=request.upload_id,
            responsible_id=None,
            responsible_name=request.responsible_name,
            status="processing",
            cases_total=len(cases),
            cases_processed=0,
            cases_rejected=0,
        )
        db.add(processing)
        db.flush()
        processing_id = processing.id

        # Repositorio de resultados AI
        ai_result_repo = SQLAlchemyAIResultRepository(db)

        # Procesar cada caso
        results = []
        total_tokens = 0
        total_latency = 0.0
        rejected = 0

        for idx, case in enumerate(processable_cases):
            # Enviar progreso por WebSocket
            if client_id:
                await ws_manager.send_progress(
                    client_id,
                    {
                        "type": "progress",
                        "current": idx + 1,
                        "total": len(processable_cases),
                        "case_code": case.case_code,
                        "status": "processing",
                        "message": f"Procesando caso {idx + 1}/{len(processable_cases)}",
                    },
                )

            try:
                # Obtener tiempo del catálogo
                time_range = catalog_repo.get_time_range(case.final_category)
                estimated_minutes = (time_range["min"] + time_range["max"]) // 2

                # Generar descripción con IA
                case_data = {
                    "case_code": case.case_code,
                    "case_type": case.case_type,
                    "final_category": case.final_category,
                    "description": case.description,
                    "solution": case.solution or "",
                }

                start_time = time.time()
                ai_response = await ai_service.generate_description(case_data)
                latency_ms = (time.time() - start_time) * 1000

                if ai_response.success:
                    # Parsear descripción
                    parsed = parser.parse_description(ai_response.content)
                    generated_description = parsed.text

                    # Guardar resultado
                    ai_result = ai_result_repo.save(
                        processing_id=processing_id,
                        case_id=case.id,
                        case_code=case.case_code,
                        estimated_minutes=estimated_minutes,
                        generated_description=generated_description,
                        model_name=ai_service.config.model,
                        tokens_used=ai_response.tokens_used or 0,
                        latency_ms=latency_ms,
                    )

                    total_tokens += ai_response.tokens_used or 0
                    total_latency += latency_ms

                    results.append(
                        AIResultResponse(
                            case_code=case.case_code,
                            final_category=case.final_category,
                            status=case.status,
                            case_type=case.case_type,
                            generated_description=generated_description,
                            estimated_minutes=estimated_minutes,
                            model_name=ai_service.config.model,
                            tokens_used=ai_response.tokens_used or 0,
                            latency_ms=latency_ms,
                        )
                    )

                    # Enviar caso completado
                    if client_id:
                        await ws_manager.send_progress(
                            client_id,
                            {
                                "type": "case_completed",
                                "current": idx + 1,
                                "total": len(processable_cases),
                                "case_code": case.case_code,
                                "status": "completed",
                                "message": f"Caso {case.case_code} procesado",
                            },
                        )
                else:
                    rejected += 1
                    if client_id:
                        await ws_manager.send_progress(
                            client_id,
                            {
                                "type": "case_error",
                                "current": idx + 1,
                                "total": len(processable_cases),
                                "case_code": case.case_code,
                                "status": "error",
                                "message": f"Error en caso {case.case_code}: {ai_response.error}",
                            },
                        )
            except Exception as e:
                rejected += 1
                if client_id:
                    await ws_manager.send_progress(
                        client_id,
                        {
                            "type": "case_error",
                            "current": idx + 1,
                            "total": len(processable_cases),
                            "case_code": case.case_code,
                            "status": "error",
                            "message": f"Error en caso {case.case_code}: {str(e)}",
                        },
                    )

        # Actualizar processing
        processing.status = "completed"
        processing.cases_processed = len(results)
        processing.cases_rejected = rejected

        # Commit
        db.commit()

        # Calcular resumen
        total_minutes = sum(r.estimated_minutes for r in results)
        total_hours = total_minutes / 60
        avg_minutes = total_minutes / len(results) if results else 0

        by_type = defaultdict(lambda: {"count": 0, "hours": 0})
        by_category = defaultdict(lambda: {"count": 0, "hours": 0})

        for r in results:
            by_type[r.case_type]["count"] += 1
            by_type[r.case_type]["hours"] += r.estimated_minutes / 60

            cat_short = r.final_category.split(".")[-1] if "." in r.final_category else r.final_category
            by_category[cat_short]["count"] += 1
            by_category[cat_short]["hours"] += r.estimated_minutes / 60

        summary = ProcessingSummary(
            total_hours=round(total_hours, 2),
            avg_minutes=round(avg_minutes, 2),
            by_type=dict(by_type),
            by_category=dict(by_category),
        )

        # Enviar completado por WebSocket
        if client_id:
            await ws_manager.send_progress(
                client_id,
                {
                    "type": "completed",
                    "message": "Procesamiento completado",
                    "processed": len(results),
                    "rejected": rejected,
                },
            )

        return ProcessResponsibleResponse(
            processing_id=processing_id,
            responsible_name=request.responsible_name,
            total_cases=len(cases),
            cases_in_catalog=len(processable_cases),
            processed=len(results),
            rejected=rejected,
            results=results,
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al procesar casos: {str(e)}",
            }
        )


# ============================================================================
# CATALOG ENDPOINT
# ============================================================================


@router.get(
    "/catalog",
    response_model=CatalogResponse,
    summary="Obtener catálogo de tiempos",
    description="Retorna el catálogo de tiempos cargado en la base de datos.",
)
async def get_catalog(db: Session = Depends(get_db)):
    """
    Retorna el catálogo de tiempos.

    Returns:
        Lista de categorías con sus tiempos
    """
    try:
        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        all_categories = catalog_repo.get_all()

        categories = []
        for cat in all_categories:
            categories.append(
                CatalogCategory(
                    path=cat.path_completo,
                    nivel1=cat.nivel1,
                    nivel2=cat.nivel2,
                    nivel3=cat.nivel3,
                    tiempo_min=cat.tiempo_min,
                    tiempo_max=cat.tiempo_max,
                )
            )

        return CatalogResponse(
            total_categories=len(categories),
            categories=categories,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener catálogo: {str(e)}",
            }
        )


# ============================================================================
# RESULTS ENDPOINT
# ============================================================================


@router.get(
    "/results/{processing_id}",
    response_model=GetResultsResponse,
    summary="Obtener resultados de procesamiento",
    description="Retorna los resultados guardados de un procesamiento específico.",
)
async def get_results(
    processing_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Retorna los resultados de un procesamiento.

    Args:
        processing_id: ID del procesamiento

    Returns:
        Resultados y resumen
    """
    try:
        # Verificar que el processing existe
        processing = db.query(ProcessingModel).filter(ProcessingModel.id == processing_id).first()
        if not processing:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROCESSING_NOT_FOUND",
                    "message": "No se encontró el procesamiento",
                },
            )

        # Obtener resultados
        ai_result_repo = SQLAlchemyAIResultRepository(db)
        db_results = ai_result_repo.find_by_processing(processing_id)

        results = []
        for r in db_results:
            results.append(
                AIResultResponse(
                    case_code=r.case_code,
                    final_category="",
                    status="",
                    case_type="",
                    generated_description=r.generated_description,
                    estimated_minutes=r.estimated_minutes,
                    model_name=r.model_name,
                    tokens_used=r.tokens_used or 0,
                    latency_ms=r.latency_ms or 0.0,
                )
            )

        # Calcular resumen
        total_minutes = sum(r.estimated_minutes for r in results)
        total_hours = total_minutes / 60
        avg_minutes = total_minutes / len(results) if results else 0

        summary = ProcessingSummary(
            total_hours=round(total_hours, 2),
            avg_minutes=round(avg_minutes, 2),
            by_type={},
            by_category={},
        )

        return GetResultsResponse(
            processing_id=processing_id,
            responsible_name=processing.responsible_name if hasattr(processing, "responsible_name") else "",
            total_results=len(results),
            results=results,
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener resultados: {str(e)}",
            }
        )


# ============================================================================
# SINGLE CASE ENDPOINTS (EXISTING)
# ============================================================================


class DescriptionRequest(BaseModel):
    """Schema de entrada para generación de descripción."""
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    final_category: str = Field(..., description="Categoría del caso")
    description: str = Field(..., description="Descripción original")
    solution: Optional[str] = Field(None, description="Solución del caso")


class DescriptionResponse(BaseModel):
    """Schema de respuesta para descripción generada."""
    case_code: str
    generated_description: str
    is_valid: bool
    starts_with_se_realizo: bool
    length: int


class EstimationRequest(BaseModel):
    """Schema de entrada para estimación de tiempo."""
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    final_category: str = Field(..., description="Categoría del caso")
    description: str = Field(..., description="Descripción del caso")


class EstimationResponse(BaseModel):
    """Schema de respuesta para estimación de tiempo."""
    case_code: str
    estimated_minutes: int
    is_valid: bool
    in_range: bool


class HealthResponse(BaseModel):
    """Schema de respuesta para health check de IA."""
    status: str
    model: str
    available: bool


@router.post(
    "/generate-description",
    response_model=DescriptionResponse,
    summary="Generar descripción con IA",
    description="Genera una descripción breve y formal para un caso usando IA.",
)
async def generate_description(request: DescriptionRequest):
    """
    Genera una descripción breve para un caso.

    Args:
        request: Datos del caso

    Returns:
        Descripción generada validada
    """
    try:
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible",
                },
            )

        case = {
            "case_code": request.case_code,
            "case_type": request.case_type,
            "final_category": request.final_category,
            "description": request.description,
            "solution": request.solution or "",
        }

        response = await ai_service.generate_description(case)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "AI_GENERATION_FAILED",
                    "message": response.error or "Error al generar descripción",
                },
            )

        parsed = parser.parse_description(response.content)

        return DescriptionResponse(
            case_code=request.case_code,
            generated_description=parsed.text,
            is_valid=parsed.is_valid,
            starts_with_se_realizo=parsed.starts_with_se_realizo,
            length=parsed.length,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al generar descripción: {str(e)}",
            }
        )


@router.post(
    "/estimate-time",
    response_model=EstimationResponse,
    summary="Estimar tiempo con IA",
    description="Estima el tiempo de resolución para un caso usando IA.",
)
async def estimate_time(request: EstimationRequest):
    """
    Estima el tiempo de resolución para un caso.

    Args:
        request: Datos del caso

    Returns:
        Estimación de tiempo validada
    """
    try:
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible",
                },
            )

        case = {
            "case_code": request.case_code,
            "case_type": request.case_type,
            "final_category": request.final_category,
            "description": request.description,
        }

        response = await ai_service.estimate_time(case)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "AI_ESTIMATION_FAILED",
                    "message": response.error or "Error al estimar tiempo",
                },
            )

        parsed = parser.parse_estimation(response.content)

        return EstimationResponse(
            case_code=request.case_code,
            estimated_minutes=parsed.minutes,
            is_valid=parsed.is_valid,
            in_range=parsed.in_range,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al estimar tiempo: {str(e)}",
            }
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar salud del servicio de IA",
    description="Verifica que el servicio de IA esté disponible y funcionando.",
)
async def ai_health_check():
    """
    Verifica la salud del servicio de IA.

    Returns:
        Estado del servicio de IA
    """
    try:
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        is_healthy = await ai_service.health_check()

        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            model=ai_service.config.model,
            available=is_healthy,
        )

    except Exception as e:
        return HealthResponse(
            status="error",
            model="unknown",
            available=False,
        )
