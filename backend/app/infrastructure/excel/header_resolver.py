"""
Header Resolver - Componente del Excel Service.

Responsabilidades:
- Identificar la fila que contiene los encabezados reales del Maestro de Casos
- No asumir que los encabezados están en la primera fila
- Detectar la fila que contenga el mayor número de columnas esperadas

Este componente NO aplica reglas de negocio, solo identificación técnica de estructura.
"""

from typing import List

import pandas as pd

from ..exceptions.excel_exceptions import StructureValidationError


class HeaderResolver:
    """
    Identifica la fila de encabezados correspondiente al formato oficial
    del Maestro de Casos.

    Este componente es parte del Excel Service y se encarga de:
    1. Buscar en las primeras filas del archivo la que contenga los encabezados
    2. Retornar el DataFrame con la fila de encabezados correcta
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

    DEFAULT_HEADER_SEARCH_LIMIT = 10

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

    def resolve(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Resuelve la fila de encabezados y retorna el DataFrame con headers correctos.

        Args:
            df: DataFrame leído sin header (header=None)

        Returns:
            DataFrame con la fila de encabezados correcta aplicada

        Raises:
            StructureValidationError: Si no se encuentra una fila de encabezados válida
        """
        header_row_index = self._find_header_row(df)

        if header_row_index is None:
            raise StructureValidationError(
                missing_columns=sorted(self.REQUIRED_COLUMNS),
                message=(
                    "No se encontró una fila de encabezados válida. "
                    "Verifique que el archivo corresponda al formato oficial "
                    "del Maestro de Casos."
                ),
            )

        return self._apply_header_row(df, header_row_index)

    def _find_header_row(self, df: pd.DataFrame):
        """
        Encuentra el índice de la fila que contiene los encabezados.

        Se selecciona la fila con mayor coincidencia con las columnas requeridas,
        siempre que alcance el mínimo exigido.

        Args:
            df: DataFrame sin header aplicado

        Returns:
            Índice de la fila de encabezados o None si no se encuentra
        """
        search_limit = min(
            self.DEFAULT_HEADER_SEARCH_LIMIT,
            len(df),
        )

        best_row = None
        best_matches = 0

        for index in range(search_limit):
            row_values = set(
                self._normalize_column_name(str(val))
                for val in df.iloc[index].dropna().astype(str)
            )
            matches = len(row_values & self.REQUIRED_COLUMNS)

            if matches > best_matches:
                best_matches = matches
                best_row = index

        minimum_required = len(self.REQUIRED_COLUMNS)
        if best_matches < minimum_required:
            return None

        return best_row

    def _apply_header_row(
        self, df: pd.DataFrame, header_row_index: int
    ) -> pd.DataFrame:
        """
        Aplica la fila de encabezados encontrada y limpia filas previas.

        Args:
            df: DataFrame original sin header
            header_row_index: Índice de la fila de encabezados

        Returns:
            DataFrame con encabezados aplicados
        """
        new_df = df.iloc[header_row_index + 1:].reset_index(drop=True)
        new_df.columns = [
            self._normalize_column_name(str(col))
            for col in df.iloc[header_row_index]
        ]
        return new_df


def resolve_excel_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función de conveniencia para resolver los encabezados de un Excel.

    Args:
        df: DataFrame leído sin header

    Returns:
        DataFrame con la fila de encabezados correcta aplicada

    Raises:
        StructureValidationError: Si no se encuentra una fila de encabezados válida
    """
    resolver = HeaderResolver()
    return resolver.resolve(df)
