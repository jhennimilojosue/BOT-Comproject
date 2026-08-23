"""
Tests unitarios para el Case Normalizer.

Estos tests validan la normalización de representación sin alterar
el significado de los datos (MGC-12).
"""

import pytest

from app.application.services.case_normalizer import CaseNormalizer
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


class TestCaseNormalizer:
    """Tests para la clase CaseNormalizer."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.normalizer = CaseNormalizer()

    def test_should_trim_spaces_in_text_fields(self):
        """Test: Debe eliminar espacios extremos en campos de texto."""
        # Arrange
        case = build_case(status="  Solucionado  ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.status == "Solucionado"

    def test_should_collapse_internal_spaces(self):
        """Test: Debe colapsar espacios internos duplicados."""
        # Arrange
        case = build_case(responsible_name="  Carlos     Rodríguez ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.responsible_name == "Carlos Rodríguez"

    def test_should_normalize_case_code_for_comparisons(self):
        """Test: Debe estandarizar case_code para comparaciones futuras."""
        # Arrange
        case = build_case(case_code=" INC001245 ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.case_code == "INC001245"

    def test_should_preserve_none_in_optional_field(self):
        """Test: user_name None debe permanecer None."""
        # Arrange
        case = build_case(user_name=None)

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.user_name is None

    def test_should_normalize_optional_field_with_value(self):
        """Test: user_name con espacios debe normalizarse."""
        # Arrange
        case = build_case(user_name="  Juan   Pérez  ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.user_name == "Juan Pérez"

    def test_should_not_alter_clean_case(self):
        """Test: Un caso ya limpio debe retornar valores equivalentes."""
        # Arrange
        case = build_case()

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.model_dump() == case.model_dump()

    def test_should_not_modify_original_case(self):
        """Test: No debe modificar la instancia original."""
        # Arrange
        case = build_case(project="  Hospital Militar ")
        original_dump = case.model_dump()

        # Act
        self.normalizer.normalize(case)

        # Assert
        assert case.model_dump() == original_dump

    def test_should_not_alter_meaning_of_description(self):
        """Test: La normalización no debe alterar el significado del texto."""
        # Arrange
        description = "Configuración del punto de red."
        case = build_case(description=f"  {description}  ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert result.description == description

    def test_should_normalize_all_cases(self):
        """Test: Debe normalizar una colección de casos."""
        # Arrange
        cases = [
            build_case(case_code=" INC001245 "),
            build_case(case_code="INC001246", project=" Banco Nacional "),
        ]

        # Act
        results = self.normalizer.normalize_all(cases)

        # Assert
        assert len(results) == 2
        assert results[0].case_code == "INC001245"
        assert results[1].project == "Banco Nacional"

    def test_should_return_same_type_instance(self):
        """Test: El resultado debe ser del mismo tipo que la entrada."""
        # Arrange
        case = build_case(status=" Solucionado ")

        # Act
        result = self.normalizer.normalize(case)

        # Assert
        assert isinstance(result, ExcelCaseDTO)
