"""
AI Routes - Endpoints para servicios de IA.

Responsabilidades:
- Generar descripciones usando IA
- Estimar tiempos usando IA
- Probar el servicio de IA
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...infrastructure.ai.ai_service import AIService
from ...infrastructure.ai.models import AIConfig
from ...infrastructure.ai.ollama_provider import OllamaProvider
from ...infrastructure.ai.response_parser import ResponseParser

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Instancia del parser
parser = ResponseParser()


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
        # Crear servicio de IA
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        # Verificar disponibilidad
        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible"
                }
            )

        # Generar descripción
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
                    "message": response.error or "Error al generar descripción"
                }
            )

        # Parsear y validar
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
                "message": f"Error al generar descripción: {str(e)}"
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
        # Crear servicio de IA
        provider = OllamaProvider()
        ai_service = AIService(ai_provider=provider)

        # Verificar disponibilidad
        if not await ai_service.health_check():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI_SERVICE_UNAVAILABLE",
                    "message": "El servicio de IA no está disponible"
                }
            )

        # Estimar tiempo
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
                    "message": response.error or "Error al estimar tiempo"
                }
            )

        # Parsear y validar
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
                "message": f"Error al estimar tiempo: {str(e)}"
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
