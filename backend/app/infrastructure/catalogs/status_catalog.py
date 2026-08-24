"""
Status Catalog - Cargador del Catálogo de Estados.

Responsabilidades:
- Cargar la configuración de estados desde el archivo Excel
- Determinar si un estado es procesable
- Proporcionar información de configuración de estados

El catálogo constituye la fuente oficial de configuración de estados.
"""

from typing import Optional


class StatusCatalog:
    """
    Cargador del Catálogo de Estados.

    Proporciona acceso a la configuración de estados definida
    en el catálogo de negocio.

    Attributes:
        _configurations: Diccionario con las configuraciones de estados
    """

    def __init__(self):
        """
        Inicializa el catálogo de estados.
        """
        self._configurations: dict[str, dict] = {}
        self._load_default_configurations()

    def _load_default_configurations(self) -> None:
        """
        Carga las configuraciones por defecto del catálogo.

        Estas configuraciones representan el catálogo inicial V1.
        """
        default_states = [
            {
                "estado": "Solucionado",
                "activo": True,
                "procesable": True,
                "observaciones": "Estado procesable por defecto",
            },
            {
                "estado": "Cerrado",
                "activo": True,
                "procesable": True,
                "observaciones": "Estado procesable por defecto",
            },
            {
                "estado": "Abierto",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
            {
                "estado": "En Progreso",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
            {
                "estado": "En proceso",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
            {
                "estado": "Suspendido",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
            {
                "estado": "Anulado",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
            {
                "estado": "Registrado",
                "activo": True,
                "procesable": False,
                "observaciones": "Estado no procesable en V1",
            },
        ]

        for state in default_states:
            self._configurations[state["estado"]] = state

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

    def is_processable(self, status: str) -> bool:
        """
        Determina si un estado permite procesar un caso.

        Un estado es procesable cuando:
        - Existe en el catálogo
        - Está activo (activo = true)
        - Está configurado como procesable (procesable = true)

        Args:
            status: Nombre del estado a consultar

        Returns:
            True si el estado es procesable y está activo
        """
        config = self._configurations.get(status)
        if config is None:
            return False
        return config.get("activo", False) and config.get("procesable", False)

    def get_config(self, status: str) -> Optional[dict]:
        """
        Obtiene la configuración de un estado.

        Args:
            status: Nombre del estado a consultar

        Returns:
            Diccionario con la configuración del estado o None si no existe
        """
        return self._configurations.get(status)

    def get_all_processable(self) -> list[str]:
        """
        Obtiene la lista de todos los estados procesables.

        Returns:
            Lista con los nombres de los estados procesables
        """
        return [
            status
            for status, config in self._configurations.items()
            if config.get("activo", False) and config.get("procesable", False)
        ]

    def add_configuration(
        self,
        status: str,
        active: bool = True,
        processable: bool = True,
        observations: str = "",
    ) -> None:
        """
        Agrega o actualiza la configuración de un estado.

        Args:
            status: Nombre del estado
            active: Si la configuración está activa
            processable: Si el estado permite procesamiento
            observations: Observaciones adicionales
        """
        self._configurations[status] = {
            "estado": status,
            "activo": active,
            "procesable": processable,
            "observaciones": observations,
        }
