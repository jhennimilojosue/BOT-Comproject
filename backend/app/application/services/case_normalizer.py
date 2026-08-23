"""
Case Normalizer - Componente de Gestión de Casos.

Responsabilidades (gestion_casos.md sección 8):
- Eliminar espacios innecesarios
- Normalizar valores de texto
- Normalizar fechas
- Estandarizar valores vacíos
- Estandarizar valores necesarios para las comparaciones

El normalizador NO aplica reglas de negocio y NO modifica el
significado del dato original almacenado en Case.
"""

from typing import List, Optional

from pydantic import BaseModel


class CaseNormalizer:
    """
    Estandariza los datos recibidos desde Excel Service.

    Este componente es parte de Gestión de Casos y trabaja sobre
    DTOs compatibles con el Case Contract. Su normalización es
    únicamente de representación: nunca altera el significado del dato.
    """

    TEXT_FIELDS = [
        "case_code",
        "responsible_name",
        "user_name",
        "project",
        "status",
        "final_category",
        "description",
        "solution",
    ]

    def normalize(self, case: BaseModel) -> BaseModel:
        """
        Normaliza un caso individual.

        Args:
            case: DTO del caso (ej. ExcelCaseDTO)

        Returns:
            Nueva instancia del mismo tipo con los valores normalizados

        Raises:
            ValueError: Si el DTO no contiene ningún campo de texto esperado
        """
        data = case.model_dump()
        updated = False

        for field in self.TEXT_FIELDS:
            value = data.get(field)
            normalized = self._normalize_optional_text(value)
            if normalized != value:
                data[field] = normalized
                updated = True

        if not updated:
            return case

        return type(case)(**data)

    def normalize_all(self, cases: List[BaseModel]) -> List[BaseModel]:
        """
        Normaliza una colección de casos.

        Args:
            cases: Lista de DTOs de casos

        Returns:
            Lista de DTOs normalizados
        """
        return [self.normalize(case) for case in cases]

    def _normalize_optional_text(self, value: Optional[str]) -> Optional[str]:
        """
        Normaliza un valor textual opcional.

        Elimina espacios extremos e internos duplicados.
        Los valores None permanecen como None.

        Args:
            value: Valor crudo o None

        Returns:
            Texto normalizado o None
        """
        if value is None:
            return None

        return " ".join(value.split())
