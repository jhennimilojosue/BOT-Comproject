"""
Database Connection - Configuración de conexión a PostgreSQL.

Responsabilidades:
- Configurar la conexión a la base de datos
- Proporcionar sesiones de SQLAlchemy
- Manejar el ciclo de vida de las conexiones
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


class DatabaseConfig:
    """
    Configuración de la base de datos.

    Attributes:
        database_url: URL de conexión a la base de datos
    """

    def __init__(self, database_url: str | None = None):
        """
        Inicializa la configuración de la base de datos.

        Args:
            database_url: URL de conexión (opcional, usa variable de entorno si no se proporciona)
        """
        if database_url is None:
            database_url = os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/bot_comproject"
            )
        self.database_url = database_url
        self._engine = None
        self._SessionLocal = None

    @property
    def engine(self):
        """
        Obtiene el motor de SQLAlchemy.

        Returns:
            Motor de SQLAlchemy
        """
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
        return self._engine

    @property
    def session_factory(self):
        """
        Obtiene la fábrica de sesiones.

        Returns:
            Fábrica de sesiones
        """
        if self._SessionLocal is None:
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        return self._SessionLocal

    def get_session(self) -> Generator[Session, None, None]:
        """
        Obtiene una sesión de la base de datos.

        Yields:
            Sesión de SQLAlchemy
        """
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_all_tables(self) -> None:
        """
        Crea todas las tablas definidas en los modelos.
        """
        from .models import Base
        Base.metadata.create_all(bind=self.engine)

    def drop_all_tables(self) -> None:
        """
        Elimina todas las tablas.
        """
        from .models import Base
        Base.metadata.drop_all(bind=self.engine)


# Instancia global de configuración
db_config = DatabaseConfig()
