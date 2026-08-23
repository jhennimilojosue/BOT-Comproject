"""
Tests unitarios para el Data Normalizer.

Estos tests validan la normalización técnica de texto y fechas.
"""

import pytest

from app.infrastructure.exceptions.excel_exceptions import InvalidDataFormatError
from app.infrastructure.excel.data_normalizer import (
    DataNormalizer,
    normalize_excel_data,
)


def build_record(**overrides):
    """Construye un registro base con overrides opcionales."""
    record = {
        "case_code": "INC001245",
        "responsible_name": "Carlos Rodríguez",
        "user_name": None,
        "project": "Hospital Militar",
        "registered_at": "2026-08-10",
        "status": "Solucionado",
        "final_category": "Ingreso de Huella",
        "description": "Problema con huella.",
        "solution": "Se configuró huella.",
    }
    record.update(overrides)
    return record


class TestDataNormalizerText:
    """Tests para la normalización de texto."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.normalizer = DataNormalizer()

    def test_should_trim_leading_and_trailing_spaces(self):
        """Test: Debe eliminar espacios al inicio y final."""
        # Arrange
        records = [build_record(status="  Solucionado  ")]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["status"] == "Solucionado"

    def test_should_collapse_internal_multiple_spaces(self):
        """Test: Debe colapsar espacios internos duplicados."""
        # Arrange
        records = [build_record(responsible_name="Carlos    Rodríguez")]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["responsible_name"] == "Carlos Rodríguez"

    def test_should_preserve_none_values(self):
        """Test: Los valores None deben permanecer como None."""
        # Arrange
        records = [build_record(user_name=None)]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["user_name"] is None

    def test_should_not_alter_clean_text(self):
        """Test: Texto ya limpio no debe modificarse (REX-07)."""
        # Arrange
        original = "Configuración del punto de red"
        records = [build_record(description=original)]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["description"] == original


class TestDataNormalizerDates:
    """Tests para la normalización de fechas."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.normalizer = DataNormalizer()

    def test_should_keep_iso_date_unchanged(self):
        """Test: Fecha YYYY-MM-DD debe permanecer igual."""
        # Arrange
        records = [build_record(registered_at="2026-08-10")]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["registered_at"] == "2026-08-10"

    def test_should_normalize_dd_mm_yyyy(self):
        """Test: Fecha DD/MM/YYYY debe convertirse a YYYY-MM-DD."""
        # Arrange
        records = [build_record(registered_at="10/08/2026")]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["registered_at"] == "2026-08-10"

    def test_should_normalize_mm_dd_yyyy_when_invalid_as_day_first(self):
        """Test: Fecha MM/DD/YYYY se interpreta cuando DD/MM/YYYY es inválido."""
        # Arrange
        # 23 no puede ser mes, por lo que se interpreta como MM/DD/YYYY
        records = [build_record(registered_at="03/23/2026")]

        # Act
        result = self.normalizer.normalize(records)

        # Assert
        assert result[0]["registered_at"] == "2026-03-23"

    def test_should_raise_error_for_invalid_date(self):
        """Test: Debe lanzar excepción para fecha inválida."""
        # Arrange
        records = [build_record(registered_at="fecha-invalida")]

        # Act & Assert
        with pytest.raises(InvalidDataFormatError) as exc_info:
            self.normalizer.normalize(records)

        assert exc_info.value.field == "registered_at"
        assert exc_info.value.error_code == "INVALID_DATA_FORMAT"

    def test_should_raise_error_for_impossible_date(self):
        """Test: Debe lanzar excepción para fecha imposible (32/13/2026)."""
        # Arrange
        records = [build_record(registered_at="32/13/2026")]

        # Act & Assert
        with pytest.raises(InvalidDataFormatError):
            self.normalizer.normalize(records)


class TestNormalizeExcelData:
    """Tests para la función de conveniencia normalize_excel_data."""

    def test_should_normalize_complete_records(self):
        """Test: Debe normalizar una colección completa de registros."""
        # Arrange
        records = [
            build_record(
                case_code="  INC001245 ",
                registered_at="10/08/2026",
                user_name=None,
            ),
            build_record(case_code="INC001246", registered_at="2026-08-11"),
        ]

        # Act
        result = normalize_excel_data(records)

        # Assert
        assert len(result) == 2
        assert result[0]["case_code"] == "INC001245"
        assert result[0]["registered_at"] == "2026-08-10"
        assert result[1]["registered_at"] == "2026-08-11"
