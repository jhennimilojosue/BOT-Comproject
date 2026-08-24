"""
Estimation Model - Modelo de SQLAlchemy para la entidad Estimation.

Responsabilidades:
- Representar la tabla estimations en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EstimationModel(Base):
    """
    Modelo de SQLAlchemy para la entidad Estimation.

    Representa el resultado de la estimación de tiempo para un caso.

    Attributes:
        id: Identificador único de la estimación
        processing_id: Identificador del Processing asociado
        case_id: Identificador del Case estimado
        case_code: Código del caso estimado
        estimated_minutes: Tiempo estimado en minutos
        minimum_minutes: Rango mínimo autorizado del catálogo
        maximum_minutes: Rango máximo autorizado del catálogo
        final_category: Categoría final utilizada para la estimación
        status: Estado de la estimación (VALID o REJECTED)
        rejection_reason: Motivo de rechazo si la estimación no es válida
        created_at: Fecha y hora de creación del registro
    """

    __tablename__ = "estimations"
    __table_args__ = (
        Index("ix_estimations_processing_id", "processing_id"),
        Index("ix_estimations_case_id", "case_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la estimación"
    )
    processing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processings.id"),
        nullable=False,
        comment="Identificador del Processing asociado"
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        comment="Identificador del Case estimado"
    )
    case_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Código del caso estimado"
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tiempo estimado en minutos"
    )
    minimum_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Rango mínimo autorizado del catálogo"
    )
    maximum_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Rango máximo autorizado del catálogo"
    )
    final_category: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Categoría final utilizada para la estimación"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="VALID",
        comment="Estado de la estimación"
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Motivo de rechazo si la estimación no es válida"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    # Relationships
    processing = relationship("ProcessingModel", backref="estimations")
    case = relationship("CaseModel", backref="estimations")

    def __repr__(self) -> str:
        return f"<EstimationModel(id={self.id}, case_code={self.case_code}, estimated_minutes={self.estimated_minutes})>"
