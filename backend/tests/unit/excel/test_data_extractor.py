"""
Tests unitarios para el Data Extractor.

Estos tests validan la extracción de datos de cada registro del DataFrame.
"""

import math

import pandas as pd
import pytest

from app.infrastructure.excel.data_extractor import (
    DataExtractor,
    extract_excel_data,
)

INTERNAL_FIELDS = {
    "case_code": ["INC001245", "INC001246"],
    "responsible_name": ["Carlos Rodríguez", "Ana Gómez"],
    "user_name": [None, "Juan Pérez"],
    "project": ["Hospital Militar", "Banco Nacional"],
    "registered_at": ["2026-08-10", "2026-08-11"],
    "status": ["Solucionado", "Cerrado"],
    "final_category": ["Ingreso de Huella", "Configuración de red"],
    "description": ["Problema con huella.", "Sin conectividad."],
    "solution": ["Se configuró huella.", "Se reinstaló driver."],
}


def build_dataframe() -> pd.DataFrame:
    """Construye un DataFrame con campos internos para los tests."""
    return pd.DataFrame(INTERNAL_FIELDS)


class TestDataExtractor:
    """Tests para la clase DataExtractor."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.extractor = DataExtractor()

    def test_should_extract_all_records(self):
        """Test: Debe extraer todos los registros del DataFrame."""
        # Arrange
        df = build_dataframe()

        # Act
        records = self.extractor.extract(df)

        # Assert
        assert len(records) == 2

    def test_should_extract_internal_fields(self):
        """Test: Cada registro debe contener los 9 campos internos."""
        # Arrange
        df = build_dataframe()

        # Act
        records = self.extractor.extract(df)

        # Assert
        expected_fields = set(DataExtractor.INTERNAL_FIELDS)
        for record in records:
            assert set(record.keys()) == expected_fields

    def test_should_convert_nan_to_none(self):
        """Test: Los valores NaN deben convertirse a None."""
        # Arrange
        df = build_dataframe()
        df.loc[0, "user_name"] = math.nan

        # Act
        records = self.extractor.extract(df)

        # Assert
        assert records[0]["user_name"] is None

    def test_should_convert_empty_string_to_none(self):
        """Test: Las cadenas vacías o con espacios deben convertirse a None."""
        # Arrange
        df = build_dataframe()
        df.loc[1, "user_name"] = "   "

        # Act
        records = self.extractor.extract(df)

        # Assert
        assert records[1]["user_name"] is None

    def test_should_preserve_values_as_strings(self):
        """Test: Los valores deben extraerse como cadenas sin alterar su contenido."""
        # Arrange
        df = build_dataframe()

        # Act
        records = self.extractor.extract(df)

        # Assert
        first = records[0]
        assert first["case_code"] == "INC001245"
        assert first["responsible_name"] == "Carlos Rodríguez"
        assert first["status"] == "Solucionado"
        assert isinstance(first["case_code"], str)

    def test_should_return_empty_list_for_empty_dataframe(self):
        """Test: Un DataFrame sin filas debe producir una lista vacía."""
        # Arrange
        df = build_dataframe().iloc[0:0]

        # Act
        records = self.extractor.extract(df)

        # Assert
        assert records == []

    def test_should_fill_missing_field_with_none(self):
        """Test: Campos ausentes en el DataFrame deben ser None en el registro."""
        # Arrange
        df = build_dataframe()
        df = df.drop(columns=["user_name"])

        # Act
        records = self.extractor.extract(df)

        # Assert
        assert all(record["user_name"] is None for record in records)


class TestExtractExcelData:
    """Tests para la función de conveniencia extract_excel_data."""

    def test_should_extract_successfully(self):
        """Test: Debe extraer exitosamente los datos del DataFrame."""
        # Arrange
        df = build_dataframe()

        # Act
        records = extract_excel_data(df)

        # Assert
        assert len(records) == 2
        assert records[1]["project"] == "Banco Nacional"
