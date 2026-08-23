"""
Data Normalizer - Componente del Excel Service.

Responsabilidades:
- Eliminar espacios innecesarios en campos de texto
- Normalizar fechas al formato ISO 8601 (YYYY-MM-DD)
- No alterar el significado del dato de negocio (REX-07)

Este componente NO aplica reglas de negocio.
"""

from datetime import datetime
from typing import Dict, List, Optional

from ..exceptions.excel_exceptions import InvalidDataFormatError


class DataNormalizer:
    """
    Transforma los datos extraídos a formatos consistentes.

    Este componente es parte del Excel Service y se encarga de:
    1. Normalizar texto: eliminar espacios duplicados y extremos
    2. Normalizar fechas: convertir a formato YYYY-MM-DD
    """

    # Formatos de fecha soportados según procesamiento_maestro.md sección 6.2
    DATE_FORMATS = [
        "%Y-%m-%d",  # YYYY-MM-DD (ISO 8601)
        "%d/%m/%Y",  # DD/MM/YYYY
        "%m/%d/%Y",  # MM/DD/YYYY
    ]

    DATE_FIELD = "registered_at"

    def normalize(
        self, records: List[Dict[str, Optional[str]]]
    ) -> List[Dict[str, Optional[str]]]:
        """
        Normaliza una colección de registros extraídos.

        Args:
            records: Lista de registros provenientes del DataExtractor

        Returns:
            Lista de registros normalizados

        Raises:
            InvalidDataFormatError: Si una fecha no puede interpretarse
                en ningún formato soportado
        """
        normalized_records = []

        for index, record in enumerate(records):
            normalized_records.append(self._normalize_record(record, index))

        return normalized_records

    def _normalize_record(
        self, record: Dict[str, Optional[str]], row_index: int
    ) -> Dict[str, Optional[str]]:
        """
        Normaliza un registro individual.

        Args:
            record: Registro a normalizar
            row_index: Índice del registro para trazabilidad de errores

        Returns:
            Registro normalizado
        """
        normalized: Dict[str, Optional[str]] = {}

        for field, value in record.items():
            if value is None:
                normalized[field] = None
            elif field == self.DATE_FIELD:
                normalized[field] = self._normalize_date(value, row_index)
            else:
                normalized[field] = self._normalize_text(value)

        return normalized

    def _normalize_text(self, value: str) -> str:
        """
        Normaliza un valor textual.

        Elimina espacios extremos y colapsa espacios internos duplicados.
        No altera el contenido semántico del texto.

        Args:
            value: Texto crudo

        Returns:
            Texto normalizado
        """
        return " ".join(value.split())

    def _normalize_date(self, value: str, row_index: int) -> str:
        """
        Normaliza una fecha al formato ISO 8601 (YYYY-MM-DD).

        Orden de intento:
        1. YYYY-MM-DD (ya normalizada)
        2. DD/MM/YYYY
        3. MM/DD/YYYY

        Args:
            value: Fecha cruda como texto
            row_index: Índice del registro para trazabilidad

        Returns:
            Fecha en formato YYYY-MM-DD

        Raises:
            InvalidDataFormatError: Si la fecha no puede interpretarse
        """
        text = value.strip()

        for fmt in self.DATE_FORMATS:
            try:
                parsed = datetime.strptime(text, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise InvalidDataFormatError(
            field=self.DATE_FIELD,
            value=value,
            expected_format="YYYY-MM-DD, DD/MM/YYYY o MM/DD/YYYY",
        )


def normalize_excel_data(
    records: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    """
    Función de conveniencia para normalizar registros extraídos.

    Args:
        records: Lista de registros del DataExtractor

    Returns:
        Lista de registros normalizados

    Raises:
        InvalidDataFormatError: Si una fecha no puede interpretarse
    """
    normalizer = DataNormalizer()
    return normalizer.normalize(records)
