"""
AI Schemas - Esquemas Pydantic para requests/responses de IA.

Responsabilidades:
- Validar datos de entrada para procesamiento de IA
- Estructurar respuestas del endpoint
- Definir schemas para WebSocket
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class ProcessResponsibleRequest(BaseModel):
    """Schema de entrada para procesamiento de casos por responsable."""

    upload_id: UUID = Field(..., description="ID del upload a procesar")
    responsible_name: str = Field(
        ..., min_length=1, description="Nombre del responsable a procesar"
    )


# ============================================================================
# RESPONSE SCHEMAS - AI RESULTS
# ============================================================================


class AIResultResponse(BaseModel):
    """Schema de respuesta para un caso procesado por IA."""

    case_code: str = Field(..., description="Código del caso")
    final_category: str = Field(..., description="Categoría del caso")
    status: str = Field(..., description="Estado del caso")
    case_type: str = Field(..., description="Tipo (Incidente/Requerimiento)")
    cliente: Optional[str] = Field(None, description="Cliente del caso (columna Usuario del maestro)")
    area: Optional[str] = Field(None, description="Área del caso")
    fecha_solucion: Optional[str] = Field(
        None, description="Fecha de solución del caso (YYYY-MM-DD)"
    )
    generated_description: str = Field(..., description="Descripción generada por IA")
    estimated_minutes: int = Field(..., description="Tiempo estimado en minutos")
    model_name: str = Field(..., description="Modelo de IA utilizado")
    tokens_used: int = Field(..., description="Tokens utilizados")
    latency_ms: float = Field(..., description="Latencia en milisegundos")


class ProcessingSummary(BaseModel):
    """Resumen del procesamiento."""

    total_hours: float = Field(..., description="Total de horas estimadas")
    avg_minutes: float = Field(..., description="Promedio de minutos por caso")
    by_type: dict = Field(..., description="Desglose por tipo de caso")
    by_category: dict = Field(..., description="Desglose por categoría")
    by_area: dict = Field(..., description="Desglose por área del caso")


class ProcessResponsibleResponse(BaseModel):
    """Schema de respuesta para procesamiento de responsable."""

    processing_id: UUID = Field(..., description="ID del procesamiento")
    responsible_name: str = Field(..., description="Nombre del responsable")
    total_cases: int = Field(..., description="Total de casos del responsable")
    cases_in_catalog: int = Field(..., description="Casos que están en el catálogo")
    processed: int = Field(..., description="Casos procesados exitosamente")
    rejected: int = Field(..., description="Casos rechazados")
    results: List[AIResultResponse] = Field(..., description="Resultados individuales")
    results_by_area: dict = Field(
        ...,
        description=(
            "Resultados agrupados por área y fecha de solución: "
            "{ área: { total_hours, by_date: { 'YYYY-MM-DD': { total_hours, cases: [AIResultResponse, ...] } }, "
            "sin_fecha: { total_hours, cases: [...] } } }"
        ),
    )
    summary: ProcessingSummary = Field(..., description="Resumen del procesamiento")


# ============================================================================
# RESPONSE SCHEMAS - CATALOG
# ============================================================================


class CatalogCategory(BaseModel):
    """Schema para una categoría del catálogo."""

    path: str = Field(..., description="Ruta completa de la categoría")
    nivel1: str = Field(..., description="Nivel 1")
    nivel2: str = Field(..., description="Nivel 2")
    nivel3: Optional[str] = Field(None, description="Nivel 3")
    tiempo_min: int = Field(..., description="Tiempo mínimo en minutos")
    tiempo_max: int = Field(..., description="Tiempo máximo en minutos")


class CatalogResponse(BaseModel):
    """Schema de respuesta para el catálogo de tiempos."""

    total_categories: int = Field(..., description="Total de categorías")
    categories: List[CatalogCategory] = Field(..., description="Lista de categorías")


# ============================================================================
# RESPONSE SCHEMAS - RESULTS
# ============================================================================


class WeekInfo(BaseModel):
    """Schema para una semana disponible en los resultados."""

    fecha_inicio: str = Field(..., description="Inicio de la semana (YYYY-MM-DD, lunes)")
    fecha_fin: str = Field(..., description="Fin de la semana (YYYY-MM-DD, domingo)")
    count: int = Field(..., description="Total de resultados con fecha_solucion en la semana")
    total_hours: float = Field(..., description="Total de horas estimadas en la semana")


class GetResultsResponse(BaseModel):
    """Schema de respuesta para obtener resultados guardados."""

    processing_id: UUID = Field(..., description="ID del procesamiento")
    responsible_name: Optional[str] = Field(None, description="Nombre del responsable (nivel archivo: puede ser nulo)")
    total_results: int = Field(..., description="Total de resultados de la semana seleccionada")
    total_results_all: int = Field(..., description="Total de resultados sin filtro de semana")
    fecha_inicio: Optional[str] = Field(None, description="Inicio del rango aplicado (YYYY-MM-DD)")
    fecha_fin: Optional[str] = Field(None, description="Fin del rango aplicado (YYYY-MM-DD)")
    semanas_disponibles: List[WeekInfo] = Field(
        ...,
        description="Semanas disponibles derivadas de fecha_solucion (para seleccionar en el frontend)",
    )
    results: List[AIResultResponse] = Field(..., description="Lista de resultados")
    results_by_area: dict = Field(
        ...,
        description=(
            "Resultados agrupados por área y fecha de solución: "
            "{ área: { total_hours, by_date: { 'YYYY-MM-DD': { total_hours, cases: [AIResultResponse, ...] } }, "
            "sin_fecha: { total_hours, cases: [...] } } }"
        ),
    )
    summary: ProcessingSummary = Field(..., description="Resumen")


# ============================================================================
# WEBSOCKET SCHEMAS
# ============================================================================


class WebSocketMessage(BaseModel):
    """Schema para mensajes de WebSocket."""

    type: str = Field(
        ...,
        description="Tipo de mensaje: started, progress, case_completed, case_error, completed",
    )
    current: Optional[int] = Field(None, description="Caso actual")
    total: Optional[int] = Field(None, description="Total de casos")
    case_code: Optional[str] = Field(None, description="Código del caso")
    status: Optional[str] = Field(None, description="Estado del caso")
    message: str = Field(..., description="Mensaje descriptivo")
    processed: Optional[int] = Field(None, description="Casos procesados")
    rejected: Optional[int] = Field(None, description="Casos rechazados")
