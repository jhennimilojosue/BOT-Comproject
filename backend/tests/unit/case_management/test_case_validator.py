"""
Tests unitarios para el Case Validator.

Estos tests validan la estructura mínima del caso según el Case Contract
y las pruebas mínimas definidas en modelo_datos_modulo.md sección 36.
"""

import pytest

from app.application.services.case_validator import CaseValidator
from app.infrastructure.excel.case_mapper import ExcelCaseDTO


def build_case(**overrides) -> ExcelCaseDTO:
    """Construye un ExcelCaseDTO base con overrides opcionales."""
    data = {
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
    data.update(overrides)
    return ExcelCaseDTO(**data)


class TestCaseValidator:
    """Tests para la clase CaseValidator."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = CaseValidator()

    def test_should_validate_complete_case(self):
        """Test: Debe validar un caso completo y válido."""
        # Act
        result = self.validator.validate(build_case())

        # Assert
        assert result.valid is True
        assert result.errors == []

    def test_should_validate_case_without_optional_user_name(self):
        """Test: Caso sin user_name debe ser válido (campo opcional)."""
        # Act
        result = self.validator.validate(build_case(user_name=None))

        # Assert
        assert result.valid is True

    def test_should_report_error_for_missing_field(self):
        """Test: Debe reportar error para campo obligatorio ausente."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["project"] = None

        class MinimalCase(ExcelCaseDTO):
            pass

        broken = type("BrokenCase", (object,), {"model_dump": lambda self: data})()

        # Act
        result = self.validator.validate(broken)

        # Assert
        assert result.valid is False
        assert any(e.field == "project" for e in result.errors)

    @pytest.mark.parametrize(
        "field",
        [
            "case_code",
            "responsible_name",
            "project",
            "status",
            "final_category",
            "description",
            "solution",
        ],
    )
    def test_should_reject_empty_required_fields(self, field):
        """Test: Cada campo obligatorio vacío debe generar error."""
        # Arrange - construir DTO válido y luego vaciar el campo en los datos
        case = build_case()
        data = case.model_dump()

        for name in data:
            if name == field:
                data[name] = None if name != "user_name" else data[name]

        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        assert result.valid is False
        matching = [e for e in result.errors if e.field == field]
        assert len(matching) == 1
        assert matching[0].code == "REQUIRED_FIELD_MISSING"

    def test_should_reject_whitespace_only_required_field(self):
        """Test: Un campo obligatorio con solo espacios debe generar error."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["responsible_name"] = "   "
        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        assert result.valid is False
        assert any(e.field == "responsible_name" for e in result.errors)

    def test_should_accept_valid_iso_date(self):
        """Test: Fecha ISO válida no debe generar errores."""
        # Act
        result = self.validator.validate(build_case(registered_at="2026-12-31"))

        # Assert
        assert result.valid is True

    def test_should_reject_invalid_date_format(self):
        """Test: Fecha en formato no ISO debe generar INVALID_DATE_FORMAT."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["registered_at"] = "10/08/2026"
        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        assert result.valid is False
        date_errors = [e for e in result.errors if e.field == "registered_at"]
        assert len(date_errors) == 1
        assert date_errors[0].code == "INVALID_DATE_FORMAT"

    def test_should_reject_missing_date(self):
        """Test: Fecha ausente debe generar REQUIRED_FIELD_MISSING."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["registered_at"] = None
        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        date_errors = [e for e in result.errors if e.field == "registered_at"]
        assert len(date_errors) == 1
        assert date_errors[0].code == "REQUIRED_FIELD_MISSING"

    def test_should_collect_multiple_errors(self):
        """Test: Debe acumular múltiples errores sin detenerse en el primero."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["case_code"] = None
        data["solution"] = None
        data["registered_at"] = "bad-date"
        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        assert result.valid is False
        assert len(result.errors) == 3

    def test_validation_result_contains_error_details(self):
        """Test: Cada error debe incluir field, code y message."""
        # Arrange
        case = build_case()
        data = case.model_dump()
        data["status"] = ""
        holder = type(
            "BrokenCase", (object,), {"model_dump": lambda self: data}
        )()

        # Act
        result = self.validator.validate(holder)

        # Assert
        error = result.errors[0]
        assert error.field == "status"
        assert error.code == "REQUIRED_FIELD_MISSING"
        assert "status" in error.message
