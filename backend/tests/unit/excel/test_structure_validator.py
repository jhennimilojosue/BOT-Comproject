"""
Tests unitarios para el Structure Validator.

Estos tests validan el comportamiento del componente de validación de estructura.
"""

import pandas as pd
import pytest

from app.infrastructure.exceptions.excel_exceptions import StructureValidationError
from app.infrastructure.excel.structure_validator import (
    StructureValidator,
    validate_excel_structure,
)


class TestStructureValidator:
    """Tests para la clase StructureValidator."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = StructureValidator()

    def test_should_validate_dataframe_with_all_required_columns(self):
        """Test: Debe validar un DataFrame con todas las columnas requeridas."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Responsible Name",
            "Proyecto",
            "Fecha",
            "Estado",
            "Categoria",
            "Descripcion",
            "Solucion",
        ]
        df = pd.DataFrame(columns=columns)

        # Act
        result = self.validator.validate(df)

        # Assert
        assert result is True

    def test_should_validate_dataframe_with_optional_columns(self):
        """Test: Debe validar un DataFrame con columnas opcionales adicionales."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Responsible Name",
            "Proyecto",
            "Fecha",
            "Estado",
            "Categoria",
            "Descripcion",
            "Solucion",
            "Usuario",
        ]
        df = pd.DataFrame(columns=columns)

        # Act
        result = self.validator.validate(df)

        # Assert
        assert result is True

    def test_should_reject_dataframe_missing_required_column(self):
        """Test: Debe rechazar un DataFrame que falte una columna requerida."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Responsible Name",
            "Proyecto",
            "Fecha",
            "Estado",
            "Categoria",
            "Descripcion",
            # Falta "Solucion"
        ]
        df = pd.DataFrame(columns=columns)

        # Act & Assert
        with pytest.raises(StructureValidationError) as exc_info:
            self.validator.validate(df)

        assert "Solucion" in exc_info.value.missing_columns
        assert exc_info.value.error_code == "REQUIRED_COLUMN_MISSING"

    def test_should_reject_dataframe_missing_multiple_columns(self):
        """Test: Debe rechazar un DataFrame que falten múltiples columnas."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Proyecto",
            "Fecha",
            "Estado",
            # Faltan: Responsible Name, Categoria, Descripcion, Solucion
        ]
        df = pd.DataFrame(columns=columns)

        # Act & Assert
        with pytest.raises(StructureValidationError) as exc_info:
            self.validator.validate(df)

        assert len(exc_info.value.missing_columns) == 4
        assert "Responsible Name" in exc_info.value.missing_columns
        assert "Categoria" in exc_info.value.missing_columns
        assert "Descripcion" in exc_info.value.missing_columns
        assert "Solucion" in exc_info.value.missing_columns

    def test_should_reject_empty_dataframe(self):
        """Test: Debe rechazar un DataFrame vacío."""
        # Arrange
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(StructureValidationError) as exc_info:
            self.validator.validate(df)

        assert len(exc_info.value.missing_columns) == 8

    def test_should_return_required_columns_sorted(self):
        """Test: Debe retornar las columnas requeridas ordenadas."""
        # Act
        columns = self.validator.get_required_columns()

        # Assert
        assert columns == sorted(columns)
        assert "Codigo Caso" in columns
        assert "Solucion" in columns

    def test_should_return_optional_columns_sorted(self):
        """Test: Debe retornar las columnas opcionales ordenadas."""
        # Act
        columns = self.validator.get_optional_columns()

        # Assert
        assert columns == sorted(columns)
        assert "Usuario" in columns

    def test_should_return_all_expected_columns(self):
        """Test: Debe retornar todas las columnas esperadas."""
        # Act
        columns = self.validator.get_all_expected_columns()

        # Assert
        assert len(columns) == 9  # 8 required + 1 optional
        assert "Codigo Caso" in columns
        assert "Usuario" in columns

    def test_should_validate_dataframe_with_exact_columns(self):
        """Test: Debe validar un DataFrame con exactamente las columnas requeridas."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Responsible Name",
            "Proyecto",
            "Fecha",
            "Estado",
            "Categoria",
            "Descripcion",
            "Solucion",
        ]
        df = pd.DataFrame(columns=columns)

        # Act
        result = self.validator.validate(df)

        # Assert
        assert result is True


class TestValidateExcelStructure:
    """Tests para la función de conveniencia validate_excel_structure."""

    def test_should_validate_structure_successfully(self):
        """Test: Debe validar exitosamente una estructura válida."""
        # Arrange
        columns = [
            "Codigo Caso",
            "Responsible Name",
            "Proyecto",
            "Fecha",
            "Estado",
            "Categoria",
            "Descripcion",
            "Solucion",
        ]
        df = pd.DataFrame(columns=columns)

        # Act
        result = validate_excel_structure(df)

        # Assert
        assert result is True

    def test_should_raise_exception_for_invalid_structure(self):
        """Test: Debe lanzar excepción para estructura inválida."""
        # Arrange
        columns = ["Codigo Caso", "Proyecto"]
        df = pd.DataFrame(columns=columns)

        # Act & Assert
        with pytest.raises(StructureValidationError):
            validate_excel_structure(df)
