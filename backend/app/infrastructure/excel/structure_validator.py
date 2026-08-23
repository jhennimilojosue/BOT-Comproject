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
    REQUIRED_COLUMNS = {
        "Codigo Caso",
        "Responsible Name",
        "Proyecto",
        "Fecha",
        "Estado",
        "Categoria",
        "Descripcion",
        "Solucion",
    }

    # Columnas opcionales
    OPTIONAL_COLUMNS = {
        "Usuario",
    }

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
        df_columns = set(df.columns)
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
