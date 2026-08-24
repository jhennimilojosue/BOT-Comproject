"""
Case Entity - Entidad de dominio para representar un caso de Aranda.

Responsabilidades:
- Representar la información original de un caso proveniente del Maestro de Casos
- Mantener la trazabilidad con el Upload de origen
- Conservar los datos originales sin modificaciones
- Identificar el tipo de caso (Incidente o Requerimiento)

Un Case NO representa una ejecución de procesamiento.
Los resultados (AIResult, Estimation, ProcessingRejection) NO forman parte de esta entidad.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CaseType(str, Enum):
    """Tipos de caso provenientes de Aranda."""
    INCIDENT = "Incidente"
    REQUIREMENT = "Requerimiento"


class Case(BaseModel):
    """
    Entidad que representa un caso proveniente del Maestro de Casos de Aranda.

    Un Case contiene la información original del caso y no debe ser
    confundido con una ejecución de procesamiento (Processing).

    Attributes:
        id: Identificador único del caso (UUID generado por el sistema)
        upload_id: Identificador del Upload de origen
        case_code: Código original del caso en Aranda
        case_type: Tipo de caso (Incidente o Requerimiento)
        responsible_name: Nombre del responsable original en Aranda
        responsible_id: Referencia al catálogo de responsables (opcional)
        user_name: Nombre del usuario asociado al caso (opcional)
        project: Proyecto asociado al caso
        registered_at: Fecha de registro del caso en el sistema origen
        status: Estado original del caso en Aranda
        final_category: Categoría final registrada en Aranda
        description: Descripción original del caso
        solution: Solución registrada en Aranda
        created_at: Fecha y hora de creación del registro en el sistema
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único del caso"
    )
    upload_id: UUID = Field(
        ...,
        description="Identificador del Upload de origen"
    )
    case_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código original del caso en Aranda"
    )
    case_type: CaseType = Field(
        ...,
        description="Tipo de caso (Incidente o Requerimiento)"
    )
    responsible_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del responsable original en Aranda"
    )
    responsible_id: Optional[UUID] = Field(
        default=None,
        description="Referencia al catálogo de responsables"
    )
    user_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Nombre del usuario asociado al caso"
    )
    project: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Proyecto asociado al caso"
    )
    registered_at: datetime = Field(
        ...,
        description="Fecha de registro del caso en el sistema origen"
    )
    status: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Estado original del caso en Aranda"
    )
    final_category: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Categoría final registrada en Aranda"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Descripción original del caso"
    )
    solution: str = Field(
        ...,
        min_length=1,
        description="Solución registrada en Aranda"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro en el sistema"
    )

    @property
    def functional_id(self) -> str:
        """
        Identificador funcional del caso.

        Returns:
            Código del caso (case_code)
        """
        return self.case_code

    def is_responsible(self, responsible_name: str) -> bool:
        """
        Verifica si el caso pertenece al responsable indicado.

        Args:
            responsible_name: Nombre del responsable a comparar

        Returns:
            True si el responsable coincide
        """
        return self.responsible_name.lower() == responsible_name.lower()

    def to_context_dict(self) -> dict:
        """
        Genera un diccionario de contexto para el Estimation Engine.

        Returns:
            Diccionario con la información necesaria para estimación
        """
        return {
            "case_code": self.case_code,
            "case_type": self.case_type.value,
            "responsible_name": self.responsible_name,
            "project": self.project,
            "final_category": self.final_category,
            "description": self.description,
            "solution": self.solution,
            "status": self.status,
        }

    @property
    def is_incident(self) -> bool:
        """Indica si el caso es un incidente."""
        return self.case_type == CaseType.INCIDENT

    @property
    def is_requirement(self) -> bool:
        """Indica si el caso es un requerimiento."""
        return self.case_type == CaseType.REQUIREMENT
