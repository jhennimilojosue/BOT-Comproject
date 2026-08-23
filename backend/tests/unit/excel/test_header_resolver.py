"""
Tests unitarios para el Header Resolver.

Estos tests validan la identificación de la fila de encabezados del Maestro de Casos.
"""

import pandas as pd
import pytest

from app.infrastructure.exceptions.excel_exceptions import StructureValidationError
from app.infrastructure.excel.header_resolver import (
    HeaderResolver,
    resolve_excel_headers,
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


class TestHeaderResolver:
    """Tests para la clase HeaderResolver."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.resolver = HeaderResolver()

    def test_should_resolve_headers_in_first_row(self):
        """Test: Debe resolver encabezados cuando están en la primera fila."""
        # Arrange
        data = [
            REQUIRED_COLUMNS,
            ["INC001", "Carlos", "Proyecto", "2026-08-10",
             "Solucionado", "Cat", "Desc", "Sol"],
        ]
        df = pd.DataFrame(data)

        # Act
        result = self.resolver.resolve(df)

        # Assert
        assert list(result.columns) == REQUIRED_COLUMNS
        assert len(result) == 1

    def test_should_resolve_headers_with_previous_rows(self):
        """Test: Debe resolver encabezados cuando hay filas previas al header."""
        # Arrange
        rows = [
            ["Reporte Semanal"],
            ["Generado por Aranda"],
            REQUIRED_COLUMNS,
            ["INC001", "Carlos", "Proyecto", "2026-08-10",
             "Solucionado", "Cat", "Desc", "Sol"],
        ]
        df = pd.DataFrame(rows)

        # Act
        result = self.resolver.resolve(df)

        # Assert
        assert list(result.columns) == REQUIRED_COLUMNS
        assert len(result) == 1

    def test_should_exclude_previous_rows_from_data(self):
        """Test: Las filas previas al header no deben aparecer en los datos."""
        # Arrange
        rows = [
            ["Reporte Semanal"],
            ["Generado por Aranda"],
            REQUIRED_COLUMNS,
            ["INC001", "Carlos", "Proyecto", "2026-08-10",
             "Solucionado", "Cat", "Desc", "Sol"],
        ]
        df = pd.DataFrame(rows)

        # Act
        result = self.resolver.resolve(df)

        # Assert
        first_row = result.iloc[0]
        assert first_row["Codigo Caso"] == "INC001"

    def test_should_raise_error_when_no_header_found(self):
        """Test: Debe lanzar excepción si no existe fila de encabezados válida."""
        # Arrange
        rows = [
            ["Reporte Semanal"],
            ["Otro texto"],
            ["Mas texto"],
        ]
        df = pd.DataFrame(rows)

        # Act & Assert
        with pytest.raises(StructureValidationError):
            self.resolver.resolve(df)

    def test_should_raise_error_on_empty_dataframe(self):
        """Test: Debe lanzar excepción con DataFrame vacío."""
        # Arrange
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(StructureValidationError):
            self.resolver.resolve(df)

    def test_should_select_row_with_most_matches(self):
        """Test: Debe seleccionar la fila con más coincidencias si hay varias candidatas."""
        # Arrange
        partial_header = ["Codigo Caso", "Responsible Name"]
        rows = [
            partial_header,
            REQUIRED_COLUMNS,
            ["INC001", "Carlos", "Proyecto", "2026-08-10",
             "Solucionado", "Cat", "Desc", "Sol"],
        ]
        df = pd.DataFrame(rows)

        # Act
        result = self.resolver.resolve(df)

        # Assert
        assert list(result.columns) == REQUIRED_COLUMNS

    def test_should_strip_whitespace_from_headers(self):
        """Test: Debe eliminar espacios en blanco alrededor de los encabezados."""
        # Arrange
        padded_columns = [f" {col} " for col in REQUIRED_COLUMNS]
        rows = [
            padded_columns,
            ["INC001", "Carlos", "Proyecto", "2026-08-10",
             "Solucionado", "Cat", "Desc", "Sol"],
        ]
        df = pd.DataFrame(rows)

        # Act
        result = self.resolver.resolve(df)

        # Assert
        assert list(result.columns) == REQUIRED_COLUMNS


class TestResolveExcelHeaders:
    """Tests para la función de conveniencia resolve_excel_headers."""

    def test_should_resolve_successfully(self):
        """Test: Debe resolver exitosamente un DataFrame válido."""
        # Arrange
        df = pd.DataFrame([REQUIRED_COLUMNS])

        # Act
        result = resolve_excel_headers(df)

        # Assert
        assert list(result.columns) == REQUIRED_COLUMNS

    def test_should_raise_exception_for_invalid_dataframe(self):
        """Test: Debe lanzar excepción para un DataFrame inválido."""
        # Arrange
        df = pd.DataFrame(["texto suelto"])

        # Act & Assert
        with pytest.raises(StructureValidationError):
            resolve_excel_headers(df)
