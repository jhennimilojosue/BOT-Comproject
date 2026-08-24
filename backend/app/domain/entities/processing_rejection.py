"""
ProcessingRejection Entity - Entidad de dominio para representar un rechazo de caso.

Responsabilidades:
- Registrar el motivo de rechazo de un caso durante el procesamiento
- Mantener la trazabilidad con el Processing y Case asociados
- Permitir la consulta posterior de casos rechazados

Un ProcessingRejection representa un caso que no pudo continuar
hacia las siguientes etapas del procesamiento.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RejectionReason(str, Enum):
    """
    Códigos de motivo de rechazo.

    Estos códigos representan las razones por las cuales un caso
    no puede continuar en el procesamiento.
    """
    INCOMPLETE_DATA = "INCOMPLETE_DATA"
    RESPONSIBLE_NOT_SELECTED = "RESPONSIBLE_NOT_SELECTED"
    RESPONSIBLE_INVALID = "RESPONSIBLE_INVALID"
    STATUS_NOT_PROCESSABLE = "STATUS_NOT_PROCESSABLE"
    CATEGORY_NOT_CONFIGURED = "CATEGORY_NOT_CONFIGURED"
    TIME_RANGE_NOT_CONFIGURED = "TIME_RANGE_NOT_CONFIGURED"
    DUPLICATE = "DUPLICATE"
    INVALID_RESULT = "INVALID_RESULT"


class ProcessingRejection(BaseModel):
    """
    Entidad que representa el rechazo de un caso durante el procesamiento.

    Un ProcessingRejection se genera cuando un caso no cumple las condiciones
    necesarias para continuar hacia las siguientes etapas (Estimation Engine, AI Service).

    Attributes:
        id: Identificador único del rechazo (UUID generado por el sistema)
        processing_id: Identificador del Processing que generó el rechazo
        case_id: Identificador del Case rechazado
        case_code: Código del caso rechazado (para referencia rápida)
        reason_code: Código del motivo de rechazo
        message: Mensaje descriptivo del motivo de rechazo
        created_at: Fecha y hora de creación del registro
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único del rechazo"
    )
    processing_id: UUID = Field(
        ...,
        description="Identificador del Processing que generó el rechazo"
    )
    case_id: UUID = Field(
        ...,
        description="Identificador del Case rechazado"
    )
    case_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código del caso rechazado"
    )
    reason_code: RejectionReason = Field(
        ...,
        description="Código del motivo de rechazo"
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Mensaje descriptivo del motivo de rechazo"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro"
    )

    @property
    def is_duplicate(self) -> bool:
        """Indica si el rechazo es por duplicidad."""
        return self.reason_code == RejectionReason.DUPLICATE

    @property
    def is_data_issue(self) -> bool:
        """Indica si el rechazo es por problema con los datos."""
        return self.reason_code == RejectionReason.INCOMPLETE_DATA

    @property
    def is_status_issue(self) -> bool:
        """Indica si el rechazo es por estado no procesable."""
        return self.reason_code == RejectionReason.STATUS_NOT_PROCESSABLE

    @property
    def is_category_issue(self) -> bool:
        """Indica si el rechazo es por categoría no configurada."""
        return self.reason_code == RejectionReason.CATEGORY_NOT_CONFIGURED

    def to_dict(self) -> dict:
        """
        Convierte el rechazo a un diccionario para persistencia o serialización.

        Returns:
            Diccionario con la información del rechazo
        """
        return {
            "id": str(self.id),
            "processing_id": str(self.processing_id),
            "case_id": str(self.case_id),
            "case_code": self.case_code,
            "reason_code": self.reason_code.value,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
