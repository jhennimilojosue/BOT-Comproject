"""
Upload Entity - Entidad de dominio para representar una carga de archivo.

Responsabilidades:
- Identificar una carga concreta del Maestro de Casos
- Mantener la trazabilidad del archivo recibido
- Asociar los casos extraídos con la carga correspondiente

Un Upload NO representa una ejecución de procesamiento.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    """Estados posibles de un Upload."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Upload(BaseModel):
    """
    Entidad que representa una carga concreta del Maestro de Casos.

    Un Upload permite identificar el archivo que posteriormente
    podrá ser utilizado para ejecutar uno o varios procesamientos.

    Attributes:
        id: Identificador único del Upload (UUID generado por el sistema)
        filename: Nombre del archivo cargado
        status: Estado actual de la carga
        total_cases: Total de casos extraídos del archivo
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de la última actualización
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único del Upload"
    )
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre del archivo cargado"
    )
    status: UploadStatus = Field(
        default=UploadStatus.PENDING,
        description="Estado actual de la carga"
    )
    total_cases: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total de casos extraídos del archivo"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de la última actualización"
    )

    def mark_as_processing(self) -> None:
        """Marca el Upload como en proceso de carga."""
        self.status = UploadStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_as_completed(self, total_cases: int) -> None:
        """
        Marca el Upload como completado exitosamente.

        Args:
            total_cases: Total de casos extraídos del archivo

        Raises:
            ValueError: Si total_cases es negativo
        """
        if total_cases < 0:
            raise ValueError("El total de casos no puede ser negativo")
        self.status = UploadStatus.COMPLETED
        self.total_cases = total_cases
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self) -> None:
        """Marca el Upload como fallido."""
        self.status = UploadStatus.FAILED
        self.updated_at = datetime.utcnow()

    @property
    def is_processable(self) -> bool:
        """Indica si el Upload puede ser utilizado para procesamiento."""
        return self.status == UploadStatus.COMPLETED

    @property
    def has_cases(self) -> bool:
        """Indica si el Upload tiene casos asociados."""
        return self.total_cases is not None and self.total_cases > 0
