"""
Estimation Repository - Implementación del repositorio de Estimations.

Responsabilidades:
- Implementar las operaciones de persistencia para Estimation
- Convertir entre entidades de dominio y modelos de SQLAlchemy
- Manejar la conexión con PostgreSQL
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ...domain.entities.estimation import Estimation, EstimationStatus
from ...domain.interfaces.repositories import EstimationRepository
from ..database.models.estimation import EstimationModel


class SQLAlchemyEstimationRepository(EstimationRepository):
    """
    Implementación del repositorio de Estimations utilizando SQLAlchemy.

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

    def save(self, estimation: Estimation) -> None:
        """
        Guarda una estimation.

        Args:
            estimation: Estimation a guardar
        """
        model = EstimationModel(
            id=estimation.id,
            processing_id=estimation.processing_id,
            case_id=estimation.case_id,
            case_code=estimation.case_code,
            estimated_minutes=estimation.estimated_minutes,
            minimum_minutes=estimation.minimum_minutes,
            maximum_minutes=estimation.maximum_minutes,
            final_category=estimation.final_category,
            status=estimation.status.value,
            rejection_reason=estimation.rejection_reason,
            created_at=estimation.created_at,
        )
        self.session.add(model)
        self.session.commit()

    def save_batch(self, estimations: list[Estimation]) -> None:
        """
        Guarda múltiples estimations.

        Args:
            estimations: Lista de estimations a guardar
        """
        models = [
            EstimationModel(
                id=estimation.id,
                processing_id=estimation.processing_id,
                case_id=estimation.case_id,
                case_code=estimation.case_code,
                estimated_minutes=estimation.estimated_minutes,
                minimum_minutes=estimation.minimum_minutes,
                maximum_minutes=estimation.maximum_minutes,
                final_category=estimation.final_category,
                status=estimation.status.value,
                rejection_reason=estimation.rejection_reason,
                created_at=estimation.created_at,
            )
            for estimation in estimations
        ]
        self.session.add_all(models)
        self.session.commit()

    def find_by_id(self, estimation_id: UUID) -> Optional[Estimation]:
        """
        Busca una estimation por su ID.

        Args:
            estimation_id: Identificador de la estimation

        Returns:
            Estimation encontrada o None
        """
        model = self.session.query(EstimationModel).filter(
            EstimationModel.id == estimation_id
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def find_by_processing(
        self, processing_id: UUID
    ) -> list[Estimation]:
        """
        Busca todas las estimations de un processing.

        Args:
            processing_id: Identificador del processing

        Returns:
            Lista de estimations encontradas
        """
        models = self.session.query(EstimationModel).filter(
            EstimationModel.processing_id == processing_id
        ).all()

        return [self._to_entity(model) for model in models]

    def find_by_case(self, case_id: UUID) -> Optional[Estimation]:
        """
        Busca la estimation de un case.

        Args:
            case_id: Identificador del case

        Returns:
            Estimation encontrada o None
        """
        model = self.session.query(EstimationModel).filter(
            EstimationModel.case_id == case_id
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: EstimationModel) -> Estimation:
        """
        Convierte un modelo de SQLAlchemy a una entidad de dominio.

        Args:
            model: Modelo de SQLAlchemy

        Returns:
            Entidad de dominio
        """
        return Estimation(
            id=model.id,
            processing_id=model.processing_id,
            case_id=model.case_id,
            case_code=model.case_code,
            estimated_minutes=model.estimated_minutes,
            minimum_minutes=model.minimum_minutes,
            maximum_minutes=model.maximum_minutes,
            final_category=model.final_category,
            status=EstimationStatus(model.status),
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
        )
