"""
Time Catalog - Cargador del Catálogo de Tiempos.

Responsabilidades:
- Cargar la configuración de tiempos desde el archivo Excel
- Obtener rangos de tiempo para categorías y tipos de caso
- Determinar si una categoría está configurada

El catálogo define los rangos de tiempo autorizados para las
categorías finales de los casos procesados.
"""

from typing import Optional


class TimeCatalog:
    """
    Cargador del Catálogo de Tiempos.

    Proporciona acceso a la configuración de tiempos definida
    en el catálogo de negocio.

    Attributes:
        _configurations: Diccionario con las configuraciones de tiempos
    """

    def __init__(self):
        """
        Inicializa el catálogo de tiempos.
        """
        self._configurations: dict[tuple[str, str], dict] = {}
        self._load_default_configurations()

    def _load_default_configurations(self) -> None:
        """
        Carga las configuraciones por defecto del catálogo.

        Estas configuraciones representan el catálogo inicial V1.
        """
        default_times = [
            {
                "case_type": "Incidente",
                "final_category": "Cableado puntos de red en sedes Comware o proyectos clientes",
                "minimum_minutes": 30,
                "maximum_minutes": 60,
                "active": True,
                "observations": "Configuración para incidentes",
            },
            {
                "case_type": "Incidente",
                "final_category": "Configurar punto de red Usuarios y/o proyectos",
                "minimum_minutes": 30,
                "maximum_minutes": 40,
                "active": True,
                "observations": "Configuración para incidentes",
            },
            {
                "case_type": "Incidente",
                "final_category": "Configurar segmento de red en los enlaces de comunicaciones",
                "minimum_minutes": 60,
                "maximum_minutes": 90,
                "active": True,
                "observations": "Configuración para incidentes",
            },
            {
                "case_type": "Requerimiento",
                "final_category": "Cableado puntos de red en sedes Comware o proyectos clientes",
                "minimum_minutes": 45,
                "maximum_minutes": 90,
                "active": True,
                "observations": "Configuración para requerimientos",
            },
            {
                "case_type": "Requerimiento",
                "final_category": "Configurar punto de red Usuarios y/o proyectos",
                "minimum_minutes": 45,
                "maximum_minutes": 60,
                "active": True,
                "observations": "Configuración para requerimientos",
            },
            {
                "case_type": "Requerimiento",
                "final_category": "Configurar segmento de red en los enlaces de comunicaciones",
                "minimum_minutes": 90,
                "maximum_minutes": 120,
                "active": True,
                "observations": "Configuración para requerimientos",
            },
        ]

        for config in default_times:
            key = (config["case_type"], config["final_category"])
            self._configurations[key] = config

    def load_from_excel(self, file_path: str) -> None:
        """
        Carga las configuraciones desde un archivo Excel.

        Args:
            file_path: Ruta al archivo Excel del catálogo

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si la estructura del archivo es incorrecta
        """
        # TODO: Implementar carga desde Excel
        pass

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
        key = (case_type, final_category)
        config = self._configurations.get(key)

        if config is None or not config.get("active", False):
            return None

        return {
            "minimum_minutes": config["minimum_minutes"],
            "maximum_minutes": config["maximum_minutes"],
        }

    def is_configured(
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
        key = (case_type, final_category)
        config = self._configurations.get(key)
        return config is not None and config.get("active", False)

    def get_all_configured(self) -> list[dict]:
        """
        Obtiene todas las configuraciones activas.

        Returns:
            Lista de diccionarios con las configuraciones activas
        """
        return [
            config
            for config in self._configurations.values()
            if config.get("active", False)
        ]

    def add_configuration(
        self,
        case_type: str,
        final_category: str,
        minimum_minutes: int,
        maximum_minutes: int,
        active: bool = True,
        observations: str = "",
    ) -> None:
        """
        Agrega o actualiza una configuración de tiempo.

        Args:
            case_type: Tipo de caso (Incidente/Requerimiento)
            final_category: Categoría final del caso
            minimum_minutes: Tiempo mínimo en minutos
            maximum_minutes: Tiempo máximo en minutos
            active: Si la configuración está activa
            observations: Observaciones adicionales

        Raises:
            ValueError: Si minimum_minutes es mayor que maximum_minutes
        """
        if minimum_minutes > maximum_minutes:
            raise ValueError(
                f"El tiempo mínimo ({minimum_minutes}) no puede ser mayor "
                f"que el máximo ({maximum_minutes})"
            )

        key = (case_type, final_category)
        self._configurations[key] = {
            "case_type": case_type,
            "final_category": final_category,
            "minimum_minutes": minimum_minutes,
            "maximum_minutes": maximum_minutes,
            "active": active,
            "observations": observations,
        }
