"""
Case Repository - Implementación del repositorio de Cases.

Responsabilidades:
- Implementar las operaciones de persistencia para Case
- Convertir entre entidades de dominio y modelos de SQLAlchemy
- Manejar la conexión con PostgreSQL
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ...domain.entities.case import Case, CaseType
from ...domain.interfaces.repositories import CaseRepository
from ..database.models.case import CaseModel


class SQLAlchemyCaseRepository(CaseRepository):
    """
    Implementación del repositorio de Cases utilizando SQLAlchemy.

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

    def save(self, case: Case) -> None:
        """
        Guarda un case.

        Args:
            case: Case a guardar
        """
        model = CaseModel(
            id=case.id,
            upload_id=case.upload_id,
            case_code=case.case_code,
            case_type=case.case_type.value,
            responsible_name=case.responsible_name,
            responsible_id=case.responsible_id,
            user_name=case.user_name,
            area=case.area,
            project=case.project,
            registered_at=case.registered_at,
            status=case.status,
            final_category=case.final_category,
            description=case.description,
            solution=case.solution,
            fecha_solucion=case.fecha_solucion,
            created_at=case.created_at,
        )
        self.session.add(model)
        self.session.commit()

    def save_batch(self, cases: list[Case]) -> None:
        """
        Guarda múltiples cases.

        Args:
            cases: Lista de cases a guardar
        """
        models = [
            CaseModel(
                id=case.id,
                upload_id=case.upload_id,
                case_code=case.case_code,
                case_type=case.case_type.value,
                responsible_name=case.responsible_name,
                responsible_id=case.responsible_id,
                user_name=case.user_name,
                area=case.area,
                project=case.project,
                registered_at=case.registered_at,
                status=case.status,
                final_category=case.final_category,
                description=case.description,
                solution=case.solution,
                fecha_solucion=case.fecha_solucion,
                created_at=case.created_at,
            )
            for case in cases
        ]
        self.session.add_all(models)
        self.session.commit()

    def find_by_id(self, case_id: UUID) -> Optional[Case]:
        """
        Busca un case por su ID.

        Args:
            case_id: Identificador del case

        Returns:
            Case encontrado o None
        """
        model = self.session.query(CaseModel).filter(
            CaseModel.id == case_id
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def find_by_upload(self, upload_id: UUID) -> list[Case]:
        """
        Busca todos los cases de un upload.

        Args:
            upload_id: Identificador del upload

        Returns:
            Lista de cases encontrados
        """
        models = self.session.query(CaseModel).filter(
            CaseModel.upload_id == upload_id
        ).all()

        return [self._to_entity(model) for model in models]

    def find_by_code_and_upload(
        self, case_code: str, upload_id: UUID
    ) -> Optional[Case]:
        """
        Busca un case por código y upload.

        Args:
            case_code: Código del caso
            upload_id: Identificador del upload

        Returns:
            Case encontrado o None
        """
        model = self.session.query(CaseModel).filter(
            CaseModel.case_code == case_code,
            CaseModel.upload_id == upload_id,
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def exists_by_code_and_upload(
        self, case_code: str, upload_id: UUID
    ) -> bool:
        """
        Verifica si existe un case por código y upload.

        Args:
            case_code: Código del caso
            upload_id: Identificador del upload

        Returns:
            True si existe
        """
        return self.session.query(CaseModel).filter(
            CaseModel.case_code == case_code,
            CaseModel.upload_id == upload_id,
        ).first() is not None

    def update(self, case: Case) -> None:
        """
        Actualiza un case existente.

        Args:
            case: Case con los datos actualizados
        """
        model = self.session.query(CaseModel).filter(
            CaseModel.id == case.id
        ).first()

        if model is not None:
            model.case_code = case.case_code
            model.case_type = case.case_type.value
            model.responsible_name = case.responsible_name
            model.responsible_id = case.responsible_id
            model.user_name = case.user_name
            model.area = case.area
            model.project = case.project
            model.registered_at = case.registered_at
            model.status = case.status
            model.final_category = case.final_category
            model.description = case.description
            model.solution = case.solution
            model.fecha_solucion = case.fecha_solucion
            self.session.commit()

    def _to_entity(self, model: CaseModel) -> Case:
        """
        Convierte un modelo de SQLAlchemy a una entidad de dominio.

        Args:
            model: Modelo de SQLAlchemy

        Returns:
            Entidad de dominio
        """
        return Case(
            id=model.id,
            upload_id=model.upload_id,
            case_code=model.case_code,
            case_type=CaseType(model.case_type),
            responsible_name=model.responsible_name,
            responsible_id=model.responsible_id,
            user_name=model.user_name,
            area=model.area,
            project=model.project,
            registered_at=model.registered_at,
            status=model.status,
            final_category=model.final_category,
            description=model.description,
            solution=model.solution,
            fecha_solucion=model.fecha_solucion,
            created_at=model.created_at,
        )
