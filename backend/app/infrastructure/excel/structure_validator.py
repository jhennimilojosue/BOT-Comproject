"""
Structure Validator - Componente del Excel Service.

Responsabilidades:
- Verificar que las columnas requeridas estén presentes
- Identificar columnas faltantes
- Reportar errores de estructura

Este componente NO aplica reglas de negocio, solo validaciones técnicas de estructura.
"""

from typing import List, Set

import pandas as pd

from ..exceptions.excel_exceptions import StructureValidationError


class StructureValidator:
    """
    Verifica que la estructura requerida del Excel esté presente.

    Este componente es parte del Excel Service y se encarga de:
    1. Identificar las columnas requeridas
    2. Verificar que existan en el DataFrame
    3. Reportar columnas faltantes
    """

    # Columnas requeridas según el Case Contract
    # Adaptado a la estructura real del Maestro de Casos de Aranda
    REQUIRED_COLUMNS = {
        "Cod Caso",
        "Tipo Caso",
        "Responsable",
        "Fecha de Registro",
        "Estado",
        "Categoria",
        "Descripci\u00f3n",
        "Solucion",
    }

    # Columnas opcionales
    OPTIONAL_COLUMNS = {
        "Usuario",
    }

    # Mapa de normalización para caracteres especiales corrupted
    CHARACTER_NORMALIZATION = {
        "\xf3": "ó",  # Latin-1 ó
        "\xf1": "ñ",  # Latin-1 ñ
        "\xed": "í",  # Latin-1 í
        "\xe1": "á",  # Latin-1 á
        "\xe9": "é",  # Latin-1 é
        "\xfa": "ú",  # Latin-1 ú
        "�": "ó",  # Corrupted ó
        "�": "á",  # Corrupted á
        "�": "é",  # Corrupted é
        "�": "í",  # Corrupted í
        "�": "ú",  # Corrupted ú
        "�": "ñ",  # Corrupted ñ
    }

    def _normalize_column_name(self, name: str) -> str:
        """
        Normaliza un nombre de columna para manejar caracteres corrupted.

        Args:
            name: Nombre de columna original

        Returns:
            Nombre normalizado
        """
        normalized = name.strip()
        for corrupted, correct in self.CHARACTER_NORMALIZATION.items():
            normalized = normalized.replace(corrupted, correct)
        return normalized

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga la estructura requerida.

        Args:
            df: DataFrame de pandas con los datos del Excel

        Returns:
            True si la estructura es válida

        Raises:
            StructureValidationError: Si faltan columnas obligatorias
        """
        missing_columns = self._find_missing_columns(df)

        if missing_columns:
            raise StructureValidationError(
                missing_columns=sorted(missing_columns),
                message=f"Faltan columnas obligatorias: {', '.join(sorted(missing_columns))}"
            )

        return True

    def _find_missing_columns(self, df: pd.DataFrame) -> Set[str]:
        """
        Encuentra las columnas faltantes en el DataFrame.

        Args:
            df: DataFrame a validar

        Returns:
            Conjunto de columnas faltantes
        """
        df_columns = set(
            self._normalize_column_name(str(col)) for col in df.columns
        )
        return self.REQUIRED_COLUMNS - df_columns

    def get_required_columns(self) -> List[str]:
        """
        Retorna la lista de columnas requeridas.

        Returns:
            Lista ordenada de columnas requeridas
        """
        return sorted(self.REQUIRED_COLUMNS)

    def get_optional_columns(self) -> List[str]:
        """
        Retorna la lista de columnas opcionales.

        Returns:
            Lista ordenada de columnas opcionales
        """
        return sorted(self.OPTIONAL_COLUMNS)

    def get_all_expected_columns(self) -> List[str]:
        """
        Retorna todas las columnas esperadas (requeridas + opcionales).

        Returns:
            Lista ordenada de todas las columnas esperadas
        """
        return sorted(self.REQUIRED_COLUMNS | self.OPTIONAL_COLUMNS)


def validate_excel_structure(df: pd.DataFrame) -> bool:
    """
    Función de conveniencia para validar la estructura de un Excel.

    Args:
        df: DataFrame a validar

    Returns:
        True si la estructura es válida

    Raises:
        StructureValidationError: Si faltan columnas obligatorias
    """
    validator = StructureValidator()
    return validator.validate(df)
