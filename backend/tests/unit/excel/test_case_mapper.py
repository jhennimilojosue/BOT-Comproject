"""
Tests unitarios para el Case Mapper.

Estos tests validan la construcción de ExcelCaseDTO según el Case Contract.
"""

import pytest
from pydantic import ValidationError

from app.infrastructure.excel.case_mapper import (
    CaseMapper,
    ExcelCaseDTO,
    map_to_excel_cases,
)


def build_record(**overrides):
    """Construye un registro normalizado base con overrides opcionales."""
    record = {
        "case_code": "INC001245",
        "responsible_name": "Carlos Rodríguez",
        "user_name": None,
        "project": "Hospital Militar",
        "registered_at": "2026-08-10",
        "status": "Solucionado",
        "final_category": "Ingreso de Huella",
        "description": "Problema con el registro de huella.",
        "solution": "Se realizó la configuración correspondiente.",
    }
    record.update(overrides)
    return record


class TestExcelCaseDTO:
    """Tests para el modelo ExcelCaseDTO."""

    def test_should_build_dto_with_valid_data(self):
        """Test: Debe construir un DTO con datos válidos."""
        # Act
        dto = ExcelCaseDTO(**build_record())

        # Assert
        assert dto.case_code == "INC001245"
        assert dto.responsible_name == "Carlos Rodríguez"
        assert dto.user_name is None
        assert dto.registered_at == "2026-08-10"

    def test_should_accept_optional_user_name(self):
        """Test: user_name opcional puede tener valor."""
        # Act
        dto = ExcelCaseDTO(**build_record(user_name="Juan Pérez"))

        # Assert
        assert dto.user_name == "Juan Pérez"

    def test_should_reject_missing_required_field(self):
        """Test: Debe rechazar un registro sin campo obligatorio."""
        # Arrange
        record = build_record()
        del record["case_code"]

        # Act & Assert
        with pytest.raises(ValidationError):
            ExcelCaseDTO(**record)

    def test_should_reject_empty_required_field(self):
        """Test: Debe rechazar un campo obligatorio vacío (None)."""
        # Arrange
        record = build_record(solution=None)

        # Act & Assert
        with pytest.raises(ValidationError):
            ExcelCaseDTO(**record)

    def test_should_reject_case_code_exceeding_max_length(self):
        """Test: Debe rechazar case_code mayor a 50 caracteres."""
        # Arrange
        record = build_record(case_code="X" * 51)

        # Act & Assert
        with pytest.raises(ValidationError):
            ExcelCaseDTO(**record)

    def test_should_accept_case_code_at_max_length(self):
        """Test: Debe aceptar case_code de exactamente 50 caracteres."""
        # Act
        dto = ExcelCaseDTO(**build_record(case_code="X" * 50))

        # Assert
        assert len(dto.case_code) == 50

    def test_should_reject_invalid_date_format(self):
        """Test: Debe rechazar fecha que no sea YYYY-MM-DD."""
        # Arrange
        record = build_record(registered_at="10/08/2026")

        # Act & Assert
        with pytest.raises(ValidationError):
            ExcelCaseDTO(**record)

    def test_should_reject_status_exceeding_max_length(self):
        """Test: Debe rechazar status mayor a 100 caracteres."""
        # Arrange
        record = build_record(status="S" * 101)

        # Act & Assert
        with pytest.raises(ValidationError):
            ExcelCaseDTO(**record)


class TestCaseMapper:
    """Tests para la clase CaseMapper."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.mapper = CaseMapper()

    def test_should_map_multiple_records(self):
        """Test: Debe mapear múltiples registros a DTOs."""
        # Arrange
        records = [
            build_record(),
            build_record(case_code="INC001246", user_name="Ana López"),
        ]

        # Act
        dtos = self.mapper.map(records)

        # Assert
        assert len(dtos) == 2
        assert all(isinstance(dto, ExcelCaseDTO) for dto in dtos)
        assert dtos[1].user_name == "Ana López"

    def test_should_map_empty_list(self):
        """Test: Una lista vacía debe producir una lista vacía."""
        # Act
        dtos = self.mapper.map([])

        # Assert
        assert dtos == []

    def test_should_raise_error_for_invalid_record(self):
        """Test: Debe propagar ValidationError para registros inválidos."""
        # Arrange
        records = [build_record(case_code=None)]

        # Act & Assert
        with pytest.raises(ValidationError):
            self.mapper.map(records)


class TestMapToExcelCases:
    """Tests para la función de conveniencia map_to_excel_cases."""

    def test_should_map_successfully(self):
        """Test: Debe mapear exitosamente registros válidos."""
        # Act
        dtos = map_to_excel_cases([build_record()])

        # Assert
        assert len(dtos) == 1
        assert dtos[0].final_category == "Ingreso de Huella"
