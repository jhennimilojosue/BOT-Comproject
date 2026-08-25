"""
Processing Model - Modelo de SQLAlchemy para la entidad Processing.

Responsabilidades:
- Representar la tabla processings en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProcessingModel(Base):
    """
    Modelo de SQLAlchemy para la entidad Processing.

    Representa una ejecución concreta del procesamiento de casos.

    Attributes:
        id: Identificador único de la ejecución
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

    __tablename__ = "processings"
    __table_args__ = (
        Index("ix_processings_upload_id", "upload_id"),
        Index("ix_processings_responsible_id", "responsible_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la ejecución"
    )
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id"),
        nullable=False,
        comment="Identificador del Upload utilizado"
    )
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="UUID del responsable seleccionado para la ejecución"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Estado técnico de la ejecución"
    )
    total_cases: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Total de casos en el Upload"
    )
    processed_cases: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Casos procesados exitosamente"
    )
    rejected_cases: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Casos rechazados durante el procesamiento"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de inicio del procesamiento"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de finalización del procesamiento"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de la última actualización"
    )

    # Relationships
    upload = relationship("UploadModel", backref="processings")

    def __repr__(self) -> str:
        return f"<ProcessingModel(id={self.id}, status={self.status})>"
