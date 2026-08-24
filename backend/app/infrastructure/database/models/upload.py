"""
Upload Model - Modelo de SQLAlchemy para la entidad Upload.

Responsabilidades:
- Representar la tabla uploads en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UploadModel(Base):
    """
    Modelo de SQLAlchemy para la entidad Upload.

    Representa una carga concreta del Maestro de Casos de Aranda.

    Attributes:
        id: Identificador único del Upload
        filename: Nombre del archivo cargado
        status: Estado actual de la carga
        total_cases: Total de casos extraídos del archivo
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de la última actualización
    """

    __tablename__ = "uploads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del Upload"
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nombre del archivo cargado"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Estado actual de la carga"
    )
    total_cases: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Total de casos extraídos del archivo"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de la última actualización"
    )

    def __repr__(self) -> str:
        return f"<UploadModel(id={self.id}, filename={self.filename}, status={self.status})>"
