"""
In-Memory Store - Almacenamiento temporal en memoria.

Responsabilidades:
- Almacenar uploads y casos temporalmente
- Permitir recuperar casos por upload_id
- Filtrar casos por responsable
- Simular persistencia hasta que se implemente la base de datos

NOTA: Este módulo es temporal y será reemplazado por la base de datos.
"""

from typing import Dict, List, Optional, Set
from uuid import UUID


class InMemoryStore:
    """
    Almacenamiento temporal en memoria.

    Attributes:
        uploads: Diccionario de uploads {upload_id: upload_data}
        cases: Diccionario de casos {upload_id: [cases]}
    """

    def __init__(self):
        self.uploads: Dict[UUID, dict] = {}
        self.cases: Dict[UUID, List[dict]] = {}

    def save_upload(self, upload_id: UUID, filename: str, total_cases: int) -> None:
        """
        Guarda un upload en memoria.

        Args:
            upload_id: Identificador del upload
            filename: Nombre del archivo
            total_cases: Total de casos extraídos
        """
        self.uploads[upload_id] = {
            "id": upload_id,
            "filename": filename,
            "total_cases": total_cases,
            "status": "pending",
        }
        self.cases[upload_id] = []

    def save_cases(self, upload_id: UUID, cases: List[dict]) -> None:
        """
        Guarda casos asociados a un upload.

        Args:
            upload_id: Identificador del upload
            cases: Lista de casos a guardar
        """
        if upload_id not in self.cases:
            self.cases[upload_id] = []
        self.cases[upload_id].extend(cases)

    def get_cases(self, upload_id: UUID) -> Optional[List[dict]]:
        """
        Obtiene los casos de un upload.

        Args:
            upload_id: Identificador del upload

        Returns:
            Lista de casos o None si no existe el upload
        """
        return self.cases.get(upload_id)

    def get_upload(self, upload_id: UUID) -> Optional[dict]:
        """
        Obtiene un upload por su ID.

        Args:
            upload_id: Identificador del upload

        Returns:
            Diccionario con la información del upload o None si no existe
        """
        return self.uploads.get(upload_id)

    def get_all_cases(self) -> List[dict]:
        """
        Obtiene todos los casos de todos los uploads.

        Returns:
            Lista con todos los casos
        """
        all_cases = []
        for cases_list in self.cases.values():
            all_cases.extend(cases_list)
        return all_cases

    def get_unique_responsibles(self) -> Set[str]:
        """
        Obtiene la lista de responsables únicos en todos los casos.

        Returns:
            Conjunto de nombres de responsables únicos
        """
        responsibles = set()
        for cases_list in self.cases.values():
            for case in cases_list:
                responsible = case.get("responsible_name")
                if responsible:
                    responsibles.add(responsible)
        return responsibles

    def get_cases_by_responsible(self, responsible_name: str) -> List[dict]:
        """
        Obtiene todos los casos de un responsable específico.

        Args:
            responsible_name: Nombre del responsable

        Returns:
            Lista de casos del responsable
        """
        cases = []
        for cases_list in self.cases.values():
            for case in cases_list:
                if case.get("responsible_name") == responsible_name:
                    cases.append(case)
        return cases

    def get_responsible_stats(self, responsible_name: str) -> dict:
        """
        Obtiene las estadísticas de un responsable.

        Args:
            responsible_name: Nombre del responsable

        Returns:
            Diccionario con total, incidentes y requerimientos
        """
        # Mapa de normalización de tipos de caso
        CASE_TYPE_NORMALIZATION = {
            "INCIDENTES": "Incidente",
            "REQUERIMIENTOS": "Requerimiento",
            "INCIDENTE": "Incidente",
            "REQUERIMIENTO": "Requerimiento",
        }

        def normalize_case_type(case_type: str) -> str:
            if not case_type:
                return "No especificado"
            return CASE_TYPE_NORMALIZATION.get(case_type, case_type)

        cases = self.get_cases_by_responsible(responsible_name)
        total = len(cases)
        incidents = sum(1 for c in cases if normalize_case_type(c.get("case_type")) == "Incidente")
        requirements = sum(1 for c in cases if normalize_case_type(c.get("case_type")) == "Requerimiento")

        return {
            "name": responsible_name,
            "total_cases": total,
            "incidents": incidents,
            "requirements": requirements,
        }


# Instancia global del store
store = InMemoryStore()
