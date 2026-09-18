"""
Data Extractor - Componente del Excel Service.

Responsabilidades:
- Extraer los valores necesarios de cada registro del DataFrame
- Manejar valores nulos/vacíos convirtiéndolos a None
- Reportar registros problemáticos sin detener el procesamiento

Este componente NO aplica reglas de negocio ni normaliza semánticamente los datos.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class DataExtractor:
    """
    Extrae los valores necesarios de cada registro del DataFrame.

    Este componente es parte del Excel Service y se encarga de:
    1. Iterar las filas del DataFrame ya mapeado a campos internos
    2. Extraer únicamente los campos requeridos por el sistema
    3. Convertir valores vacíos/nulos a None
    """

    INTERNAL_FIELDS = [
        "case_code",
        "case_type",
        "responsible_name",
        "user_name",
        "area",
        "project",
        "groups",
        "registered_at",
        "status",
        "final_category",
        "description",
        "solution",
        "fecha_solucion",
    ]

    def extract(self, df: pd.DataFrame) -> List[Dict[str, Optional[str]]]:
        """
        Extrae los datos de cada fila del DataFrame.

        Args:
            df: DataFrame con columnas ya renombradas a campos internos

        Returns:
            Lista de diccionarios {campo_interno: valor} con un registro por fila.
            Los valores vacíos o nulos se convierten a None.
        """
        records: List[Dict[str, Optional[str]]] = []

        for _, row in df.iterrows():
            record = self._extract_record(row)
            if record is not None:
                records.append(record)

        return records

    def _extract_record(self, row: pd.Series) -> Optional[Dict[str, Optional[str]]]:
        """
        Extrae un registro individual de una fila.

        Args:
            row: Fila del DataFrame

        Returns:
            Diccionario con los campos internos extraídos
        """
        record: Dict[str, Optional[str]] = {}

        for field in self.INTERNAL_FIELDS:
            value = row[field] if field in row.index else None
            record[field] = self._clean_value(value)

        return record

    def _clean_value(self, value: Any) -> Optional[str]:
        """
        Convierte un valor del DataFrame a Optional[str].

        Valores NaN, None o cadenas vacías se convierten en None.
        No se modifica el contenido semántico del valor.

        Args:
            value: Valor crudo del DataFrame

        Returns:
            Valor como str o None si está vacío
        """
        if value is None or pd.isna(value):
            return None

        text = str(value)
        if text.strip() == "":
            return None

        return text


def extract_excel_data(df: pd.DataFrame) -> List[Dict[str, Optional[str]]]:
    """
    Función de conveniencia para extraer datos de un Excel.

    Args:
        df: DataFrame con columnas renombradas a campos internos

    Returns:
        Lista de diccionarios con los registros extraídos
    """
    extractor = DataExtractor()
    return extractor.extract(df)
