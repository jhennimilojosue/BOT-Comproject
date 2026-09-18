"""
Case Model - Modelo de SQLAlchemy para la entidad Case.

Responsabilidades:
- Representar la tabla cases en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CaseModel(Base):
    """
    Modelo de SQLAlchemy para la entidad Case.

    Representa un caso proveniente del Maestro de Casos de Aranda.

    Attributes:
        id: Identificador único del caso
        upload_id: Identificador del Upload de origen
        case_code: Código original del caso en Aranda
        case_type: Tipo de caso (Incidente/Requerimiento)
        responsible_name: Nombre del responsable original en Aranda
        responsible_id: Referencia al catálogo de responsables
        user_name: Nombre del usuario asociado al caso
        area: Área asociada al caso en Aranda
        project: Proyecto asociado al caso
        registered_at: Fecha de registro del caso en el sistema origen
        status: Estado original del caso en Aranda
        final_category: Categoría final registrada en Aranda
        description: Descripción original del caso
        solution: Solución registrada en Aranda
        created_at: Fecha y hora de creación del registro en el sistema
    """

    __tablename__ = "cases"
    __table_args__ = (
        Index("ix_cases_upload_id", "upload_id"),
        Index("ix_cases_case_code", "case_code"),
        Index("ix_cases_upload_case_code", "upload_id", "case_code", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del caso"
    )
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id"),
        nullable=False,
        comment="Identificador del Upload de origen"
    )
    case_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código original del caso en Aranda"
    )
    case_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo de caso (Incidente/Requerimiento)"
    )
    responsible_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del responsable original en Aranda"
    )
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Referencia al catálogo de responsables"
    )
    user_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del usuario asociado al caso"
    )
    area: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Área asociada al caso en Aranda"
    )
    groups: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Grupo(s) asociados al caso en Aranda"
    )
    project: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Proyecto asociado al caso"
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de registro del caso en el sistema origen"
    )
    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Estado original del caso en Aranda"
    )
    final_category: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Categoría final registrada en Aranda"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descripción original del caso"
    )
    solution: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Solución registrada en Aranda"
    )
    fecha_solucion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de solución del caso en el sistema origen"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro en el sistema"
    )

    # Relationships
    upload = relationship("UploadModel", backref="cases")

    def __repr__(self) -> str:
        return f"<CaseModel(id={self.id}, case_code={self.case_code}, case_type={self.case_type})>"
