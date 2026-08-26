"""
CatalogoTiempo Model - Modelo de SQLAlchemy para el catálogo de tiempos.

Responsabilidades:
- Representar la tabla catalogo_tiempos en PostgreSQL
- Mantener las categorías y sus tiempos estimados (min/max)
- Soportar la búsqueda por categoría normalizada
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CatalogoTiempoModel(Base):
    """
    Modelo de SQLAlchemy para el catálogo de tiempos.

    Representa las categorías de casos con sus tiempos estimados.

    Attributes:
        id: Identificador único del registro
        nivel1: Nivel 1 de la categoría (ej: "Gestión de Activos")
        nivel2: Nivel 2 de la categoría (ej: "Asignación")
        nivel3: Nivel 3 de la categoría (ej: "Computador portátil")
        path_completo: Ruta completa de la categoría (ej: "Gestión de Activos.Asignación.Computador portátil")
        path_normalizado: Ruta normalizada (sin tildes, minúsculas)
        tiempo_min: Tiempo mínimo estimado en minutos
        tiempo_max: Tiempo máximo estimado en minutos
        created_at: Fecha y hora de creación del registro
    """

    __tablename__ = "catalogo_tiempos"
    __table_args__ = (
        Index("ix_catalogo_tiempos_path_normalizado", "path_normalizado", unique=True),
        Index("ix_catalogo_tiempos_nivel1", "nivel1"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del registro"
    )
    nivel1: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nivel 1 de la categoría"
    )
    nivel2: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nivel 2 de la categoría"
    )
    nivel3: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nivel 3 de la categoría (opcional)"
    )
    path_completo: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Ruta completa de la categoría"
    )
    path_normalizado: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Ruta normalizada (sin tildes, minúsculas)"
    )
    tiempo_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tiempo mínimo estimado en minutos"
    )
    tiempo_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tiempo máximo estimado en minutos"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    def __repr__(self) -> str:
        return f"<CatalogoTiempoModel(path={self.path_completo}, min={self.tiempo_min}, max={self.tiempo_max})>"
