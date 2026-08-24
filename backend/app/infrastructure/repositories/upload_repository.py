"""
Upload Repository - Implementación del repositorio de Uploads.

Responsabilidades:
- Implementar las operaciones de persistencia para Upload
- Convertir entre entidades de dominio y modelos de SQLAlchemy
- Manejar la conexión con PostgreSQL
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ...domain.entities.upload import Upload
from ...domain.interfaces.repositories import UploadRepository
from ..database.models.upload import UploadModel


class SQLAlchemyUploadRepository(UploadRepository):
    """
    Implementación del repositorio de Uploads utilizando SQLAlchemy.

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

    def save(self, upload: Upload) -> None:
        """
        Guarda un upload.

        Args:
            upload: Upload a guardar
        """
        model = UploadModel(
            id=upload.id,
            filename=upload.filename,
            status=upload.status.value,
            total_cases=upload.total_cases,
            created_at=upload.created_at,
            updated_at=upload.updated_at,
        )
        self.session.add(model)
        self.session.commit()

    def find_by_id(self, upload_id: UUID) -> Optional[Upload]:
        """
        Busca un upload por su ID.

        Args:
            upload_id: Identificador del upload

        Returns:
            Upload encontrado o None
        """
        model = self.session.query(UploadModel).filter(
            UploadModel.id == upload_id
        ).first()

        if model is None:
            return None

        return self._to_entity(model)

    def update(self, upload: Upload) -> None:
        """
        Actualiza un upload existente.

        Args:
            upload: Upload con los datos actualizados
        """
        model = self.session.query(UploadModel).filter(
            UploadModel.id == upload.id
        ).first()

        if model is not None:
            model.filename = upload.filename
            model.status = upload.status.value
            model.total_cases = upload.total_cases
            model.updated_at = upload.updated_at
            self.session.commit()

    def _to_entity(self, model: UploadModel) -> Upload:
        """
        Convierte un modelo de SQLAlchemy a una entidad de dominio.

        Args:
            model: Modelo de SQLAlchemy

        Returns:
            Entidad de dominio
        """
        from ...domain.entities.upload import UploadStatus

        return Upload(
            id=model.id,
            filename=model.filename,
            status=UploadStatus(model.status),
            total_cases=model.total_cases,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
