"""
Processing Repository - Implementación del repositorio de Processings.

Responsabilidades:
- Implementar las operaciones de persistencia para Processing
- Convertir entre entidades de dominio y modelos de SQLAlchemy
- Manejar la conexión con PostgreSQL
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ...domain.entities.processing import Processing, ProcessingStatus
from ...domain.interfaces.repositories import ProcessingRepository
from ..database.models.processing import ProcessingModel


class SQLAlchemyProcessingRepository(ProcessingRepository):
    """
    Implementación del repositorio de Processings utilizando SQLAlchemy.

    Attributes:
        session: Sesión de SQLAlchemy para acceso a datos
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio con una sesión de SQLAlchemy.

        Args:
            session: Sesión de SQLAlchemy
        """
        self.session = session

    def save(self, processing: Processing) -> None:
        """
        Guarda un processing.

        Args:
            processing: Processing a guardar
        """
        model = ProcessingModel(
            id=processing.id,
            upload_id=processing.upload_id,
            responsible_id=processing.responsible_id,
            status=processing.status.value,
            total_cases=processing.total_cases,
            processed_cases=processing.processed_cases,
            rejected_cases=processing.rejected_cases,
            created_at=processing.created_at,
            started_at=processing.started_at,
            completed_at=processing.completed_at,
            updated_at=processing.updated_at,
        )
        self.session.add(model)
        self.session.commit()

    def find_by_id(self, processing_id: UUID) -> Optional[Processing]:
        """
        Busca un processing por su ID.

        Args:
            processing_id: Identificador del processing

        Returns:
            Processing encontrado o None
        """
        model = self.session.query(ProcessingModel).filter(
            ProcessingModel.id == processing_id
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def find_by_upload(self, upload_id: UUID) -> list[Processing]:
        """
        Busca todos los processings de un upload.

        Args:
            upload_id: Identificador del upload

        Returns:
            Lista de processings encontrados
        """
        models = self.session.query(ProcessingModel).filter(
            ProcessingModel.upload_id == upload_id
        ).all()

        return [self._to_entity(model) for model in models]

    def update(self, processing: Processing) -> None:
        """
        Actualiza un processing existente.

        Args:
            processing: Processing con los datos actualizados
        """
        model = self.session.query(ProcessingModel).filter(
            ProcessingModel.id == processing.id
        ).first()

        if model is not None:
            model.status = processing.status.value
            model.total_cases = processing.total_cases
            model.processed_cases = processing.processed_cases
            model.rejected_cases = processing.rejected_cases
            model.started_at = processing.started_at
            model.completed_at = processing.completed_at
            model.updated_at = processing.updated_at
            self.session.commit()

    def _to_entity(self, model: ProcessingModel) -> Processing:
        """
        Convierte un modelo de SQLAlchemy a una entidad de dominio.

        Args:
            model: Modelo de SQLAlchemy

        Returns:
            Entidad de dominio
        """
        return Processing(
            id=model.id,
            upload_id=model.upload_id,
            responsible_id=model.responsible_id,
            status=ProcessingStatus(model.status),
            total_cases=model.total_cases,
            processed_cases=model.processed_cases,
            rejected_cases=model.rejected_cases,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            updated_at=model.updated_at,
        )
