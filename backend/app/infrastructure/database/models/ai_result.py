"""
AIResult Model - Modelo de SQLAlchemy para la entidad AIResult.

Responsabilidades:
- Representar la tabla ai_results en PostgreSQL
- Mantener la estructura definida en el dominio
- Soportar las operaciones CRUD necesarias
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AIResultModel(Base):
    """
    Modelo de SQLAlchemy para la entidad AIResult.

    Representa el resultado generado por el AI Service para un caso específico.

    Attributes:
        id: Identificador único del resultado
        processing_id: Identificador del Processing asociado
        case_id: Identificador del Case procesado
        case_code: Código del caso procesado
        estimated_minutes: Tiempo recomendado por la IA
        generated_description: Descripción profesional generada
        model_name: Nombre del modelo de IA utilizado
        tokens_used: Cantidad de tokens utilizados en la inferencia
        latency_ms: Latencia de la respuesta en milisegundos
        created_at: Fecha y hora de creación del registro
    """

    __tablename__ = "ai_results"
    __table_args__ = (
        Index("ix_ai_results_processing_id", "processing_id"),
        Index("ix_ai_results_case_id", "case_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del resultado"
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
        comment="Identificador del Case procesado"
    )
    case_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="C��digo del caso procesado"
    )
    case_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de caso (Incidente/Requerimiento)"
    )
    status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Estado del caso"
    )
    final_category: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Categor��a final del caso"
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tiempo recomendado por la IA (en minutos)"
    )
    generated_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descripción profesional generada"
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre del modelo de IA utilizado"
    )
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Cantidad de tokens utilizados en la inferencia"
    )
    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Latencia de la respuesta en milisegundos"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    # Relationships
    processing = relationship("ProcessingModel", backref="ai_results")
    case = relationship("CaseModel", backref="ai_results")

    def __repr__(self) -> str:
        return f"<AIResultModel(id={self.id}, case_code={self.case_code}, estimated_minutes={self.estimated_minutes})>"
