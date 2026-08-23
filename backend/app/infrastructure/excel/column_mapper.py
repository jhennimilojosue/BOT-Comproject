"""
Column Mapper - Componente del Excel Service.

Responsabilidades:
- Relacionar las columnas físicas del Excel con los campos internos del sistema
- Retornar el mapeo columna física -> campo interno
- Identificar columnas no reconocidas

Este componente NO aplica reglas de negocio, solo mapeo técnico de columnas.
"""

from typing import Dict, List

import pandas as pd


class ColumnMapper:
    """
    Relaciona las columnas del Excel con los campos internos del sistema.

    Este componente es parte del Excel Service y se encarga de:
    1. Definir el mapeo oficial según el Maestro de Casos
    2. Validar que las columnas del DataFrame puedan mapearse
    3. Retornar el diccionario {columna_física: campo_interno}
    """

    # Mapeo oficial según procesamiento_maestro.md sección 6.1
    COLUMN_MAPPING: Dict[str, str] = {
        "Codigo Caso": "case_code",
        "Responsible Name": "responsible_name",
        "Proyecto": "project",
        "Fecha": "registered_at",
        "Estado": "status",
        "Categoria": "final_category",
        "Descripcion": "description",
        "Solucion": "solution",
        "Usuario": "user_name",
    }

    REQUIRED_FIELDS = {
        "case_code",
        "responsible_name",
        "project",
        "registered_at",
        "status",
        "final_category",
        "description",
        "solution",
    }

    def get_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Obtiene el mapeo de columnas presentes en el DataFrame.

        Args:
            df: DataFrame con los headers ya resueltos

        Returns:
            Diccionario {columna_física: campo_interno} solo con
            las columnas presentes en el DataFrame
        """
        df_columns = set(df.columns)
        return {
            excel_col: internal_field
            for excel_col, internal_field in self.COLUMN_MAPPING.items()
            if excel_col in df_columns
        }

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renombra las columnas del DataFrame a los nombres internos oficiales.

        Args:
            df: DataFrame con los headers ya resueltos

        Returns:
            Nuevo DataFrame con columnas renombradas a campos internos

        Raises:
            ValueError: Si falta alguna columna obligatoria para el mapeo
        """
        mapping = self.get_mapping(df)
        missing_fields = self.REQUIRED_FIELDS - set(mapping.values())

        if missing_fields:
            raise ValueError(
                f"El DataFrame no contiene las columnas obligatorias "
                f"para los campos internos: {', '.join(sorted(missing_fields))}"
            )

        return df.rename(columns=mapping).reset_index(drop=True)

    def get_unrecognized_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Identifica columnas del Excel no reconocidas por el mapeo oficial.

        Args:
            df: DataFrame con los headers ya resueltos

        Returns:
            Lista ordenada de columnas no reconocidas
        """
        recognized = set(self.COLUMN_MAPPING.keys())
        return sorted(set(df.columns) - recognized)

    @property
    def official_mapping(self) -> Dict[str, str]:
        """Retorna el mapeo oficial completo (columna física -> campo interno)."""
        return dict(self.COLUMN_MAPPING)


def map_excel_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función de conveniencia para renombrar columnas del Excel a campos internos.

    Args:
        df: DataFrame con los headers ya resueltos

    Returns:
        DataFrame con columnas renombradas a campos internos

    Raises:
        ValueError: Si falta alguna columna obligatoria
    """
    mapper = ColumnMapper()
    return mapper.rename_columns(df)
