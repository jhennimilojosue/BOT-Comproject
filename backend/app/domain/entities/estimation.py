"""
Estimation Entity - Entidad de dominio para representar el resultado de estimación.

Responsabilidades:
- Almacenar el tiempo estimado para un caso
- Mantener la trazabilidad con el Processing y Case asociados
- Registrar el rango autorizado utilizado
- Indicar si la estimación es válida o fue rechazada

Una Estimation representa el resultado final de la etapa de estimación.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EstimationStatus(str, Enum):
    """Estados posibles de una estimación."""
    VALID = "VALID"
    REJECTED = "REJECTED"


class Estimation(BaseModel):
    """
    Entidad que representa el resultado de la estimación de tiempo para un caso.

    Una Estimation contiene el tiempo estimado por la IA, validado por el
    Estimation Engine dentro del rango autorizado por el Catálogo de Tiempos.

    Attributes:
        id: Identificador único de la estimación (UUID generado por el sistema)
        processing_id: Identificador del Processing asociado
        case_id: Identificador del Case estimado
        case_code: Código del caso estimado
        estimated_minutes: Tiempo estimado en minutos
        minimum_minutes: Rango mínimo autorizado del catálogo
        maximum_minutes: Rango máximo autorizado del catálogo
        final_category: Categoría final utilizada para la estimación
        status: Estado de la estimación (VALID o REJECTED)
        rejection_reason: Motivo de rechazo si la estimación no es válida
        created_at: Fecha y hora de creación del registro
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único de la estimación"
    )
    processing_id: UUID = Field(
        ...,
        description="Identificador del Processing asociado"
    )
    case_id: UUID = Field(
        ...,
        description="Identificador del Case estimado"
    )
    case_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código del caso estimado"
    )
    estimated_minutes: int = Field(
        ...,
        ge=0,
        description="Tiempo estimado en minutos"
    )
    minimum_minutes: int = Field(
        ...,
        ge=0,
        description="Rango mínimo autorizado del catálogo"
    )
    maximum_minutes: int = Field(
        ...,
        ge=0,
        description="Rango máximo autorizado del catálogo"
    )
    final_category: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Categoría final utilizada para la estimación"
    )
    status: EstimationStatus = Field(
        default=EstimationStatus.VALID,
        description="Estado de la estimación"
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description="Motivo de rechazo si la estimación no es válida"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro"
    )

    @property
    def is_valid(self) -> bool:
        """Indica si la estimación es válida."""
        return self.status == EstimationStatus.VALID

    @property
    def is_rejected(self) -> bool:
        """Indica si la estimación fue rechazada."""
        return self.status == EstimationStatus.REJECTED

    @property
    def is_within_range(self) -> bool:
        """Verifica si el tiempo estimado está dentro del rango autorizado."""
        return self.minimum_minutes <= self.estimated_minutes <= self.maximum_minutes

    @property
    def range_diff(self) -> int:
        """Calcula la diferencia entre el máximo y mínimo autorizado."""
        return self.maximum_minutes - self.minimum_minutes

    @property
    def deviation_from_min(self) -> int:
        """Calcula la desviación del tiempo estimado respecto al mínimo."""
        return self.estimated_minutes - self.minimum_minutes

    @property
    def deviation_from_max(self) -> int:
        """Calcula la desviación del tiempo estimado respecto al máximo."""
        return self.maximum_minutes - self.estimated_minutes

    def mark_as_rejected(self, reason: str) -> None:
        """
        Marca la estimación como rechazada.

        Args:
            reason: Motivo del rechazo
        """
        self.status = EstimationStatus.REJECTED
        self.rejection_reason = reason

    def to_dict(self) -> dict:
        """
        Convierte la estimación a un diccionario para persistencia o serialización.

        Returns:
            Diccionario con la información de la estimación
        """
        return {
            "id": str(self.id),
            "processing_id": str(self.processing_id),
            "case_id": str(self.case_id),
            "case_code": self.case_code,
            "estimated_minutes": self.estimated_minutes,
            "minimum_minutes": self.minimum_minutes,
            "maximum_minutes": self.maximum_minutes,
            "final_category": self.final_category,
            "status": self.status.value,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat(),
        }
