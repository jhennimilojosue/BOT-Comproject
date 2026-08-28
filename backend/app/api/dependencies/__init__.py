"""
Database Dependencies - Dependencias de FastAPI para la base de datos y servicios.

Responsabilidades:
- Proporcionar sesiones de BD a los endpoints
- Proporcionar servicios a los endpoints
- Manejar el ciclo de vida de las conexiones
"""

from typing import Generator

from sqlalchemy.orm import Session

from ...infrastructure.catalogs.catalog_service import CatalogService
from ...infrastructure.catalogs.responsible_catalog import ResponsibleCatalog
from ...infrastructure.catalogs.status_catalog import StatusCatalog
from ...infrastructure.catalogs.time_catalog import TimeCatalog
from ...infrastructure.database.connection import db_config
from ...infrastructure.processing.processing_service import ProcessingService


def get_db() -> Generator[Session, None, None]:
    """
    Dependency de FastAPI para obtener una sesión de BD.

    Yields:
        Sesión de SQLAlchemy
    """
    yield from db_config.get_session()


def get_catalog_service() -> CatalogService:
    """
    Dependency de FastAPI para obtener el CatalogService.

    Returns:
        CatalogService con todos los catálogos cargados
    """
    return CatalogService(
        status_catalog=StatusCatalog(),
        time_catalog=TimeCatalog(),
        responsible_catalog=ResponsibleCatalog(),
    )


def get_processing_service(
    catalog_service: CatalogService = None,
) -> ProcessingService:
    """
    Dependency de FastAPI para obtener el ProcessingService.

    Args:
        catalog_service: CatalogService dependency (opcional)

    Returns:
        ProcessingService configurado
    """
    if catalog_service is None:
        catalog_service = get_catalog_service()
    return ProcessingService(catalog_service=catalog_service)
