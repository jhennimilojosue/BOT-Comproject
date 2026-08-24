"""
Base Model - Modelo base para SQLAlchemy.

Responsabilidades:
- Definir la configuración base para todos los modelos
- Establecer el comportamiento por defecto
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos de SQLAlchemy.

    Utiliza DeclarativeBase de SQLAlchemy 2.0.
    """
    pass


class TimestampMixin:
    """
    Mixin para agregar campos de timestamp a los modelos.
    """
    created_at: bool = True
    updated_at: bool = True
