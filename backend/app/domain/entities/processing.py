"""
Processing Entity - Entidad de dominio para representar una ejecución de procesamiento.

Responsabilidades:
- Representar una ejecución concreta del procesamiento de casos
- Mantener la trazabilidad de cada ejecución
- Identificar el Upload utilizado y el responsable seleccionado
- Almacenar el estado técnico de la ejecución

Un Processing es una entidad independiente del Upload y de los casos individuales.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Estados técnicos de una ejecución de procesamiento."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Processing(BaseModel):
    """
    Entidad que representa una ejecución concreta del procesamiento de casos.

    Un Processing permite identificar una operación de procesamiento sobre
    los casos de un Upload específico, seleccionando un responsable.

    Attributes:
        id: Identificador único de la ejecución (UUID generado por el sistema)
        upload_id: Identificador del Upload utilizado
        responsible_id: UUID del responsable seleccionado para la ejecución
        status: Estado técnico de la ejecución
        total_cases: Total de casos en el Upload
        processed_cases: Casos procesados exitosamente
        rejected_cases: Casos rechazados durante el procesamiento
        created_at: Fecha y hora de creación del registro
        started_at: Fecha y hora de inicio del procesamiento
        completed_at: Fecha y hora de finalización del procesamiento
        updated_at: Fecha y hora de la última actualización
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único de la ejecución"
    )
    upload_id: UUID = Field(
        ...,
        description="Identificador del Upload utilizado"
    )
    responsible_id: UUID = Field(
        ...,
        description="UUID del responsable seleccionado para la ejecución"
    )
    status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING,
        description="Estado técnico de la ejecución"
    )
    total_cases: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total de casos en el Upload"
    )
    processed_cases: Optional[int] = Field(
        default=None,
        ge=0,
        description="Casos procesados exitosamente"
    )
    rejected_cases: Optional[int] = Field(
        default=None,
        ge=0,
        description="Casos rechazados durante el procesamiento"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de creación del registro"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de inicio del procesamiento"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de finalización del procesamiento"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de la última actualización"
    )

    def mark_as_processing(self, total_cases: int) -> None:
        """
        Marca la ejecución como en proceso.

        Args:
            total_cases: Total de casos a procesar

        Raises:
            ValueError: Si total_cases es negativo
        """
        if total_cases < 0:
            raise ValueError("El total de casos no puede ser negativo")
        self.status = ProcessingStatus.PROCESSING
        self.total_cases = total_cases
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_as_completed(self, processed_cases: int, rejected_cases: int) -> None:
        """
        Marca la ejecución como completada.

        Args:
            processed_cases: Casos procesados exitosamente
            rejected_cases: Casos rechazados

        Raises:
            ValueError: Si los contadores son negativos o no suman el total
        """
        if processed_cases < 0 or rejected_cases < 0:
            raise ValueError("Los contadores no pueden ser negativos")
        if self.total_cases is not None:
            if processed_cases + rejected_cases != self.total_cases:
                raise ValueError(
                    f"La suma de procesados ({processed_cases}) y rechazados "
                    f"({rejected_cases}) no coincide con el total ({self.total_cases})"
                )
        self.status = ProcessingStatus.COMPLETED
        self.processed_cases = processed_cases
        self.rejected_cases = rejected_cases
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self) -> None:
        """Marca la ejecución como fallida."""
        self.status = ProcessingStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def is_completed(self) -> bool:
        """Indica si la ejecución está completada."""
        return self.status == ProcessingStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Indica si la ejecución falló."""
        return self.status == ProcessingStatus.FAILED

    @property
    def is_in_progress(self) -> bool:
        """Indica si la ejecución está en progreso."""
        return self.status == ProcessingStatus.PROCESSING

    @property
    def has_results(self) -> bool:
        """Indica si existen resultados procesados."""
        return self.processed_cases is not None and self.processed_cases > 0

    @property
    def has_rejections(self) -> bool:
        """Indica si existen casos rechazados."""
        return self.rejected_cases is not None and self.rejected_cases > 0

    @property
    def processing_rate(self) -> Optional[float]:
        """
        Calcula la tasa de procesamiento exitoso.

        Returns:
            Porcentaje de casos procesados (0-100) o None si no hay datos
        """
        if self.total_cases is None or self.total_cases == 0:
            return None
        if self.processed_cases is None:
            return None
        return (self.processed_cases / self.total_cases) * 100
