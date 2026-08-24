"""
Responsible Catalog - Cargador del Catálogo de Responsables.

Responsabilidades:
- Cargar la información de responsables desde el archivo Excel
- Proporcionar lista de responsables activos
- Validar que un responsable sea válido y esté activo

El catálogo define las personas disponibles para ejecutar
el procesamiento de casos.
"""

from typing import Optional
from uuid import UUID, uuid4


class ResponsibleCatalog:
    """
    Cargador del Catálogo de Responsables.

    Proporciona acceso a la información de responsables definida
    en el catálogo de negocio.

    Attributes:
        _responsibles: Diccionario con la información de responsables
    """

    def __init__(self):
        """
        Inicializa el catálogo de responsables.
        """
        self._responsibles: dict[UUID, dict] = {}
        self._load_default_responsibles()

    def _load_default_responsibles(self) -> None:
        """
        Carga los responsables por defecto del catálogo.

        Estos responsables representan el catálogo inicial V1.
        """
        default_responsibles = [
            {
                "id": uuid4(),
                "nombre": "Responsable 1",
                "activo": True,
                "observaciones": "Responsable habilitado para procesamiento",
            },
            {
                "id": uuid4(),
                "nombre": "Responsable 2",
                "activo": True,
                "observaciones": "Responsable habilitado para procesamiento",
            },
            {
                "id": uuid4(),
                "nombre": "Responsable 3",
                "activo": True,
                "observaciones": "Responsable habilitado para procesamiento",
            },
            {
                "id": uuid4(),
                "nombre": "Responsable 4",
                "activo": True,
                "observaciones": "Responsable habilitado para procesamiento",
            },
            {
                "id": uuid4(),
                "nombre": "Responsable 5",
                "activo": True,
                "observaciones": "Responsable habilitado para procesamiento",
            },
        ]

        for responsible in default_responsibles:
            self._responsibles[responsible["id"]] = responsible

    def load_from_excel(self, file_path: str) -> None:
        """
        Carga los responsables desde un archivo Excel.

        Args:
            file_path: Ruta al archivo Excel del catálogo

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si la estructura del archivo es incorrecta
        """
        # TODO: Implementar carga desde Excel
        pass

    def get_active(self) -> list[dict]:
        """
        Obtiene la lista de responsables activos.

        Returns:
            Lista de diccionarios con la información de responsables activos
        """
        return [
            responsible
            for responsible in self._responsibles.values()
            if responsible.get("activo", False)
        ]

    def is_valid(self, responsible_id: UUID) -> bool:
        """
        Determina si un responsable es válido y está activo.

        Args:
            responsible_id: Identificador del responsable

        Returns:
            True si el responsable existe y está activo
        """
        responsible = self._responsibles.get(responsible_id)
        return responsible is not None and responsible.get("activo", False)

    def get_by_id(self, responsible_id: UUID) -> Optional[dict]:
        """
        Obtiene la información de un responsable por su ID.

        Args:
            responsible_id: Identificador del responsable

        Returns:
            Diccionario con la información del responsable o None si no existe
        """
        return self._responsibles.get(responsible_id)

    def get_by_name(self, name: str) -> Optional[dict]:
        """
        Obtiene la información de un responsable por su nombre.

        Args:
            name: Nombre del responsable

        Returns:
            Diccionario con la información del responsable o None si no existe
        """
        for responsible in self._responsibles.values():
            if responsible.get("nombre", "").lower() == name.lower():
                return responsible
        return None

    def add_responsible(
        self,
        name: str,
        active: bool = True,
        observations: str = "",
    ) -> UUID:
        """
        Agrega un nuevo responsable al catálogo.

        Args:
            name: Nombre del responsable
            active: Si el responsable está activo
            observations: Observaciones adicionales

        Returns:
            ID del responsable creado
        """
        responsible_id = uuid4()
        self._responsibles[responsible_id] = {
            "id": responsible_id,
            "nombre": name,
            "activo": active,
            "observaciones": observations,
        }
        return responsible_id

    def deactivate(self, responsible_id: UUID) -> bool:
        """
        Desactiva un responsable.

        Args:
            responsible_id: Identificador del responsable

        Returns:
            True si se desactivó correctamente, False si no existe
        """
        responsible = self._responsibles.get(responsible_id)
        if responsible is None:
            return False
        responsible["activo"] = False
        return True
