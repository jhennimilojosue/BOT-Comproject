"""
Tests unitarios para el Column Mapper.

Estos tests validan el mapeo de columnas físicas del Excel a campos internos.
"""

import pandas as pd
import pytest

from app.infrastructure.excel.column_mapper import (
    ColumnMapper,
    map_excel_columns,
)

REQUIRED_COLUMNS = [
    "Codigo Caso",
    "Responsible Name",
    "Proyecto",
    "Fecha",
    "Estado",
    "Categoria",
    "Descripcion",
    "Solucion",
]


class TestColumnMapper:
    """Tests para la clase ColumnMapper."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.mapper = ColumnMapper()

    def test_should_map_all_required_columns(self):
        """Test: Debe mapear todas las columnas requeridas presentes."""
        # Arrange
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

        # Act
        mapping = self.mapper.get_mapping(df)

        # Assert
        assert mapping["Codigo Caso"] == "case_code"
        assert mapping["Responsible Name"] == "responsible_name"
        assert mapping["Proyecto"] == "project"
        assert mapping["Fecha"] == "registered_at"
        assert mapping["Estado"] == "status"
        assert mapping["Categoria"] == "final_category"
        assert mapping["Descripcion"] == "description"
        assert mapping["Solucion"] == "solution"

    def test_should_include_optional_column_when_present(self):
        """Test: Debe incluir la columna opcional Usuario cuando está presente."""
        # Arrange
        df = pd.DataFrame(columns=REQUIRED_COLUMNS + ["Usuario"])

        # Act
        mapping = self.mapper.get_mapping(df)

        # Assert
        assert mapping["Usuario"] == "user_name"

    def test_should_exclude_missing_columns(self):
        """Test: El mapeo no debe incluir columnas ausentes del DataFrame."""
        # Arrange
        df = pd.DataFrame(columns=["Codigo Caso", "Estado"])

        # Act
        mapping = self.mapper.get_mapping(df)

        # Assert
        assert mapping == {"Codigo Caso": "case_code", "Estado": "status"}

    def test_should_rename_columns_to_internal_fields(self):
        """Test: Debe renombrar las columnas a los nombres internos oficiales."""
        # Arrange
        df = pd.DataFrame(
            [[
                "INC001245", "Carlos Rodríguez", "Hospital Militar",
                "2026-08-10", "Solucionado", "Ingreso de Huella",
                "Descripción original", "Solución registrada",
            ]],
            columns=REQUIRED_COLUMNS,
        )

        # Act
        result = self.mapper.rename_columns(df)

        # Assert
        expected = {
            "case_code", "responsible_name", "project", "registered_at",
            "status", "final_category", "description", "solution",
        }
        assert set(result.columns) == expected

    def test_rename_should_preserve_data(self):
        """Test: Renombrar columnas no debe alterar los datos."""
        # Arrange
        df = pd.DataFrame(
            [["INC001245", "Solucionado"]],
            columns=["Codigo Caso", "Estado"],
        )

        # Act
        mapping = self.mapper.get_mapping(df)
        renamed = {mapping[col]: col for col in df.columns}

        # Assert
        assert renamed == {"case_code": "Codigo Caso", "status": "Estado"}

    def test_rename_should_raise_error_for_missing_required_columns(self):
        """Test: Debe lanzar error si faltan columnas obligatorias para mapear."""
        # Arrange
        df = pd.DataFrame(columns=["Codigo Caso", "Usuario"])

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.mapper.rename_columns(df)

        assert "obligatorias" in str(exc_info.value)

    def test_should_identify_unrecognized_columns(self):
        """Test: Debe identificar columnas del Excel no reconocidas."""
        # Arrange
        df = pd.DataFrame(columns=REQUIRED_COLUMNS + ["ColumnaExtra"])

        # Act
        unrecognized = self.mapper.get_unrecognized_columns(df)

        # Assert
        assert unrecognized == ["ColumnaExtra"]

    def test_should_return_empty_list_when_all_recognized(self):
        """Test: No debe reportar columnas no reconocidas si todas son válidas."""
        # Arrange
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

        # Act
        unrecognized = self.mapper.get_unrecognized_columns(df)

        # Assert
        assert unrecognized == []

    def test_official_mapping_contains_eleven_columns(self):
        """Test: El mapeo oficial debe contener 11 columnas (8 requeridas + 3 opcionales)."""
        # Act
        mapping = self.mapper.official_mapping

        # Assert
        assert len(mapping) == 11
        assert mapping["Area"] == "area"
        assert mapping["Fecha de Solución"] == "fecha_solucion"


class TestMapExcelColumns:
    """Tests para la función de conveniencia map_excel_columns."""

    def test_should_map_successfully(self):
        """Test: Debe mapear exitosamente un DataFrame válido."""
        # Arrange
        df = pd.DataFrame(
            [["INC001", "Carlos", "P", "2026-08-10", "Solucionado",
              "Cat", "Desc", "Sol"]],
            columns=REQUIRED_COLUMNS,
        )

        # Act
        result = map_excel_columns(df)

        # Assert
        assert "case_code" in result.columns

    def test_should_raise_error_for_invalid_dataframe(self):
        """Test: Debe lanzar error para un DataFrame sin columnas obligatorias."""
        # Arrange
        df = pd.DataFrame(columns=["ColumnaRandom"])

        # Act & Assert
        with pytest.raises(ValueError):
            map_excel_columns(df)
