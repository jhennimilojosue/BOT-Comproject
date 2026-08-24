"""
ProcessingRejection Repository - Implementación del repositorio de ProcessingRejections.

Responsabilidades:
- Implementar las operaciones de persistencia para ProcessingRejection
- Convertir entre entidades de dominio y modelos de SQLAlchemy
- Manejar la conexión con PostgreSQL
"""

from uuid import UUID

from sqlalchemy.orm import Session

from ...domain.entities.processing_rejection import (
    ProcessingRejection,
    RejectionReason,
)
from ...domain.interfaces.repositories import ProcessingRejectionRepository
from ..database.models.processing_rejection import ProcessingRejectionModel


class SQLAlchemyProcessingRejectionRepository(ProcessingRejectionRepository):
    """
    Implementación del repositorio de ProcessingRejections utilizando SQLAlchemy.

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

    def save(self, rejection: ProcessingRejection) -> None:
        """
        Guarda un processing rejection.

        Args:
            rejection: ProcessingRejection a guardar
        """
        model = ProcessingRejectionModel(
            id=rejection.id,
            processing_id=rejection.processing_id,
            case_id=rejection.case_id,
            case_code=rejection.case_code,
            reason_code=rejection.reason_code.value,
            message=rejection.message,
            created_at=rejection.created_at,
        )
        self.session.add(model)
        self.session.commit()

    def save_batch(self, rejections: list[ProcessingRejection]) -> None:
        """
        Guarda múltiples processing rejections.

        Args:
            rejections: Lista de processing rejections a guardar
        """
        models = [
            ProcessingRejectionModel(
                id=rejection.id,
                processing_id=rejection.processing_id,
                case_id=rejection.case_id,
                case_code=rejection.case_code,
                reason_code=rejection.reason_code.value,
                message=rejection.message,
                created_at=rejection.created_at,
            )
            for rejection in rejections
        ]
        self.session.add_all(models)
        self.session.commit()

    def find_by_processing(
        self, processing_id: UUID
    ) -> list[ProcessingRejection]:
        """
        Busca todos los rejections de un processing.

        Args:
            processing_id: Identificador del processing

        Returns:
            Lista de processing rejections encontrados
        """
        models = self.session.query(ProcessingRejectionModel).filter(
            ProcessingRejectionModel.processing_id == processing_id
        ).all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: ProcessingRejectionModel) -> ProcessingRejection:
        """
        Convierte un modelo de SQLAlchemy a una entidad de dominio.

        Args:
            model: Modelo de SQLAlchemy

        Returns:
            Entidad de dominio
        """
        return ProcessingRejection(
            id=model.id,
            processing_id=model.processing_id,
            case_id=model.case_id,
            case_code=model.case_code,
            reason_code=RejectionReason(model.reason_code),
            message=model.message,
            created_at=model.created_at,
        )
