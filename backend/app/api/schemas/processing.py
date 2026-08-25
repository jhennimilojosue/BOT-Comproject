"""
Processing Schemas - Schemas de Pydantic para la API de procesamiento.

Responsabilidades:
- Definir contratos de entrada y salida
- Validar datos de la API
- Documentar la estructura de respuesta
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessingRequest(BaseModel):
    """
    Schema de entrada para el procesamiento de casos.

    Attributes:
        upload_id: Identificador del upload con los casos
        responsible_id: UUID del responsable seleccionado
        responsible_name: Nombre del responsable para filtrar (opcional)
    """
    upload_id: UUID = Field(..., description="Identificador del upload con los casos")
    responsible_id: Optional[UUID] = Field(None, description="UUID del responsable seleccionado")
    responsible_name: Optional[str] = Field(None, description="Nombre del responsable para filtrar")

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "responsible_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }


class CaseResult(BaseModel):
    """
    Resultado del procesamiento de un caso individual.

    Attributes:
        case_code: Código del caso
        case_type: Tipo de caso
        status: Estado del caso
        is_processable: Si el caso es procesable
        rejection_reason: Razón de rechazo (si aplica)
        estimated_minutes: Minutos estimados (si aplica)
        responsible_name: Nombre del responsable
    """
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    status: str = Field(..., description="Estado del caso")
    is_processable: bool = Field(..., description="Si el caso es procesable")
    rejection_reason: Optional[str] = Field(None, description="Razón de rechazo")
    estimated_minutes: Optional[int] = Field(None, description="Minutos estimados")
    responsible_name: Optional[str] = Field(None, description="Nombre del responsable")


class ProcessingResponse(BaseModel):
    """
    Schema de respuesta del procesamiento de casos.

    Attributes:
        processing_id: Identificador de la ejecución
        total_cases: Total de casos recibidos
        processed_cases: Casos procesados exitosamente
        rejected_cases: Casos rechazados
        results: Lista de resultados individuales
    """
    processing_id: UUID = Field(..., description="Identificador de la ejecución")
    total_cases: int = Field(..., description="Total de casos recibidos")
    processed_cases: int = Field(..., description="Casos procesados exitosamente")
    rejected_cases: int = Field(..., description="Casos rechazados")
    results: List[CaseResult] = Field(..., description="Lista de resultados individuales")

    class Config:
        json_schema_extra = {
            "example": {
                "processing_id": "770e8400-e29b-41d4-a716-446655440002",
                "total_cases": 100,
                "processed_cases": 85,
                "rejected_cases": 15,
                "results": [
                    {
                        "case_code": "CASO-001",
                        "case_type": "Incidente",
                        "status": "Solucionado",
                        "is_processable": True,
                        "estimated_minutes": 480,
                        "responsible_name": "Juan Perez",
                    }
                ],
            }
        }
