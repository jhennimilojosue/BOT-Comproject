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
    # Adaptado a la estructura real del Maestro de Casos de Aranda
    COLUMN_MAPPING: Dict[str, str] = {
        "Cod Caso": "case_code",
        "Tipo Caso": "case_type",
        "Responsable": "responsible_name",
        "Fecha de Registro": "registered_at",
        "Estado": "status",
        "Categoria": "final_category",
        "Descripci\u00f3n": "description",
        "Solucion": "solution",
        "Usuario": "user_name",
    }

    REQUIRED_FIELDS = {
        "case_code",
        "case_type",
        "responsible_name",
        "registered_at",
        "status",
        "final_category",
        "description",
        "solution",
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

    def get_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Obtiene el mapeo de columnas presentes en el DataFrame.

        Args:
            df: DataFrame con los headers ya resueltos

        Returns:
            Diccionario {columna_física: campo_interno} solo con
            las columnas presentes en el DataFrame
        """
        df_columns = set(
            self._normalize_column_name(str(col)) for col in df.columns
        )
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
        # Primero normalizar las columnas del DataFrame
        normalized_df = df.copy()
        normalized_df.columns = [
            self._normalize_column_name(str(col)) for col in normalized_df.columns
        ]

        mapping = self.get_mapping(normalized_df)
        missing_fields = self.REQUIRED_FIELDS - set(mapping.values())

        if missing_fields:
            raise ValueError(
                f"El DataFrame no contiene las columnas obligatorias "
                f"para los campos internos: {', '.join(sorted(missing_fields))}"
            )

        return normalized_df.rename(columns=mapping).reset_index(drop=True)

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
