"""
AIResult Entity - Entidad de dominio para representar el resultado generado por IA.

Responsabilidades:
- Almacenar la recomendación de tiempo generada por el modelo de IA
- Almacenar la descripción profesional generada
- Mantener la trazabilidad con el Processing y Case asociados
- Registrar información técnica sobre la inferencia

Un AIResult representa la salida del AI Service para un caso específico.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AIResult(BaseModel):
    """
    Entidad que representa el resultado generado por el AI Service.

    Un AIResult contiene la recomendación de tiempo y la descripción profesional
    generadas por el modelo de IA para un caso específico.

    Attributes:
        id: Identificador único del resultado (UUID generado por el sistema)
        processing_id: Identificador del Processing asociado
        case_id: Identificador del Case procesado
        case_code: Código del caso procesado
        estimated_minutes: Tiempo recomendado por la IA (en minutos)
        generated_description: Descripción profesional generada
        model_name: Nombre del modelo de IA utilizado
        tokens_used: Cantidad de tokens utilizados en la inferencia
        latency_ms: Latencia de la respuesta en milisegundos
        created_at: Fecha y hora de creación del registro
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único del resultado"
    )
    processing_id: UUID = Field(
        ...,
        description="Identificador del Processing asociado"
    )
    case_id: UUID = Field(
        ...,
        description="Identificador del Case procesado"
    )
    case_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código del caso procesado"
    )
    estimated_minutes: int = Field(
        ...,
        ge=0,
        description="Tiempo recomendado por la IA (en minutos)"
    )
    generated_description: str = Field(
        ...,
        min_length=1,
        description="Descripción profesional generada"
    )
    model_name: str = Field(
        ...,
        min_length=1,
        description="Nombre del modelo de IA utilizado"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cantidad de tokens utilizados en la inferencia"
    )
    latency_ms: Optional[float] = Field(
        default=None,
        ge=0,
        description="Latencia de la respuesta en milisegundos"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro"
    )

    @property
    def has_description(self) -> bool:
        """Indica si se generó una descripción."""
        return bool(self.generated_description and self.generated_description.strip())

    @property
    def has_metrics(self) -> bool:
        """Indica si se registraron métricas de inferencia."""
        return self.tokens_used is not None or self.latency_ms is not None

    @property
    def latency_seconds(self) -> Optional[float]:
        """
        Convierte la latencia a segundos.

        Returns:
            Latencia en segundos o None si no hay datos
        """
        if self.latency_ms is None:
            return None
        return self.latency_ms / 1000

    def to_dict(self) -> dict:
        """
        Convierte el resultado a un diccionario para persistencia o serialización.

        Returns:
            Diccionario con la información del resultado
        """
        return {
            "id": str(self.id),
            "processing_id": str(self.processing_id),
            "case_id": str(self.case_id),
            "case_code": self.case_code,
            "estimated_minutes": self.estimated_minutes,
            "generated_description": self.generated_description,
            "model_name": self.model_name,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat(),
        }

    def to_export_dict(self) -> dict:
        """
        Convierte el resultado a un diccionario para exportación.

        Returns:
            Diccionario con la información relevante para exportación
        """
        return {
            "case_code": self.case_code,
            "estimated_minutes": self.estimated_minutes,
            "generated_description": self.generated_description,
        }
