"""
ProcessingRejection Model - Modelo de SQLAlchemy para la entidad ProcessingRejection.

Responsabilidades:
- Representar la tabla processing_rejections en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProcessingRejectionModel(Base):
    """
    Modelo de SQLAlchemy para la entidad ProcessingRejection.

    Representa el rechazo de un caso durante el procesamiento.

    Attributes:
        id: Identificador único del rechazo
        processing_id: Identificador del Processing que generó el rechazo
        case_id: Identificador del Case rechazado
        case_code: Código del caso rechazado
        reason_code: Código del motivo de rechazo
        message: Mensaje descriptivo del motivo de rechazo
        created_at: Fecha y hora de creación del registro
    """

    __tablename__ = "processing_rejections"
    __table_args__ = (
        Index("ix_processing_rejections_processing_id", "processing_id"),
        Index("ix_processing_rejections_case_id", "case_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del rechazo"
    )
    processing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processings.id"),
        nullable=False,
        comment="Identificador del Processing que generó el rechazo"
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        comment="Identificador del Case rechazado"
    )
    case_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código del caso rechazado"
    )
    reason_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código del motivo de rechazo"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mensaje descriptivo del motivo de rechazo"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    # Relationships
    processing = relationship("ProcessingModel", backref="rejections")
    case = relationship("CaseModel", backref="rejections")

    def __repr__(self) -> str:
        return f"<ProcessingRejectionModel(id={self.id}, reason_code={self.reason_code})>"
