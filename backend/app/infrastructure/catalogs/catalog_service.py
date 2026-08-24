"""
Catalog Service - Servicio centralizado de acceso a catálogos.

Responsabilidades:
- Proporcionar acceso centralizado a los catálogos de negocio
- Coordinar la consulta de estados, tiempos y responsables
- Validar configuraciones activas
- Determinar si un estado es procesable
- Obtener rangos de tiempo para categorías

Este es el ÚNICO componente autorizado para consultar directamente
la fuente de los catálogos.
"""

from typing import Optional
from uuid import UUID

from .status_catalog import StatusCatalog
from .time_catalog import TimeCatalog
from .responsible_catalog import ResponsibleCatalog


class CatalogService:
    """
    Servicio centralizado de acceso a catálogos.

    Proporciona una interfaz unificada para consultar la información
    de los catálogos de negocio: Estados, Tiempos y Responsables.

    Attributes:
        status_catalog: Catálogo de estados
        time_catalog: Catálogo de tiempos
        responsible_catalog: Catálogo de responsables
    """

    def __init__(
        self,
        status_catalog: StatusCatalog,
        time_catalog: TimeCatalog,
        responsible_catalog: ResponsibleCatalog,
    ):
        """
        Inicializa el Catalog Service con los catálogos proporcionados.

        Args:
            status_catalog: Catálogo de estados
            time_catalog: Catálogo de tiempos
            responsible_catalog: Catálogo de responsables
        """
        self.status_catalog = status_catalog
        self.time_catalog = time_catalog
        self.responsible_catalog = responsible_catalog

    # ==================== Catálogo de Estados ====================

    def is_status_processable(self, status: str) -> bool:
        """
        Determina si un estado permite procesar un caso.

        Args:
            status: Nombre del estado a consultar

        Returns:
            True si el estado es procesable y está activo
        """
        return self.status_catalog.is_processable(status)

    def get_status_config(self, status: str) -> Optional[dict]:
        """
        Obtiene la configuración de un estado.

        Args:
            status: Nombre del estado a consultar

        Returns:
            Diccionario con la configuración del estado o None si no existe
        """
        return self.status_catalog.get_config(status)

    # ==================== Catálogo de Tiempos ====================

    def get_time_range(
        self,
        case_type: str,
        final_category: str,
    ) -> Optional[dict]:
        """
        Obtiene el rango de tiempo para una categoría y tipo de caso.

        Args:
            case_type: Tipo de caso (Incidente/Requerimiento)
            final_category: Categoría final del caso

        Returns:
            Diccionario con minimum_minutes y maximum_minutes o None si no existe
        """
        return self.time_catalog.get_time_range(case_type, final_category)

    def is_category_configured(
        self,
        case_type: str,
        final_category: str,
    ) -> bool:
        """
        Determina si una categoría está configurada para un tipo de caso.

        Args:
            case_type: Tipo de caso (Incidente/Requerimiento)
            final_category: Categoría final del caso

        Returns:
            True si la categoría tiene una configuración activa
        """
        return self.time_catalog.is_configured(case_type, final_category)

    # ==================== Catálogo de Responsables ====================

    def get_active_responsibles(self) -> list[dict]:
        """
        Obtiene la lista de responsables activos.

        Returns:
            Lista de diccionarios con la información de responsables activos
        """
        return self.responsible_catalog.get_active()

    def is_responsible_valid(self, responsible_id: UUID) -> bool:
        """
        Determina si un responsable es válido y está activo.

        Args:
            responsible_id: Identificador del responsable

        Returns:
            True si el responsable existe y está activo
        """
        return self.responsible_catalog.is_valid(responsible_id)

    def get_responsible_by_id(self, responsible_id: UUID) -> Optional[dict]:
        """
        Obtiene la información de un responsable por su ID.

        Args:
            responsible_id: Identificador del responsable

        Returns:
            Diccionario con la información del responsable o None si no existe
        """
        return self.responsible_catalog.get_by_id(responsible_id)

    def get_responsible_by_name(self, name: str) -> Optional[dict]:
        """
        Obtiene la información de un responsable por su nombre.

        Args:
            name: Nombre del responsable

        Returns:
            Diccionario con la información del responsable o None si no existe
        """
        return self.responsible_catalog.get_by_name(name)
