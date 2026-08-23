"""
Tests unitarios para el Case Context Builder.

Estos tests validan la construcción del contexto para Estimation Engine
según gestion_casos.md sección 21.
"""

from uuid import uuid4

import pytest

from app.application.services.case_context_builder import (
    CaseContext,
    CaseContextBuilder,
)
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


class TestCaseContextBuilder:
    """Tests para la clase CaseContextBuilder."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.builder = CaseContextBuilder()

    def test_should_build_context_with_all_fields(self):
        """Test: Debe construir el contexto con todos los campos requeridos."""
        # Arrange
        case_id = uuid4()
        case = build_case()

        # Act
        context = self.builder.build(case_id, case)

        # Assert
        assert isinstance(context, CaseContext)
        assert context.case_id == case_id
        assert context.case_code == "INC001245"
        assert context.responsible_name == "Carlos Rodríguez"
        assert context.project == "Hospital Militar"
        assert context.final_category == "Ingreso de Huella"
        assert context.status == "Solucionado"

    def test_context_should_not_contain_internal_only_fields(self):
        """Test: El contexto no debe incluir campos internos innecesarios."""
        # Arrange
        case = build_case(user_name="Juan Pérez")

        # Act
        context = self.builder.build(uuid4(), case)

        # Assert
        context_fields = set(context.model_dump().keys())
        assert "user_name" not in context_fields
        assert "registered_at" not in context_fields

    def test_context_should_not_contain_estimation_fields(self):
        """Test: El contexto NO debe calcular tiempos ni rangos (sección 21)."""
        # Act
        context = self.builder.build(uuid4(), build_case())

        # Assert
        context_fields = set(context.model_dump().keys())
        assert "estimated_minutes" not in context_fields
        assert "minimum_minutes" not in context_fields
        assert "maximum_minutes" not in context_fields

    def test_should_require_valid_case_id(self):
        """Test: Debe exigir un case_id UUID válido."""
        # Act & Assert
        with pytest.raises(Exception):
            self.builder.build("no-es-un-uuid", build_case())

    def test_should_not_modify_original_case(self):
        """Test: La construcción no debe modificar el caso original (MGC-19)."""
        # Arrange
        case = build_case()
        original_dump = case.model_dump()

        # Act
        self.builder.build(uuid4(), case)

        # Assert
        assert case.model_dump() == original_dump

    def test_should_build_multiple_contexts(self):
        """Test: Debe construir contextos para una colección de casos."""
        # Arrange
        id_a, id_b = uuid4(), uuid4()
        cases_with_ids = [(id_a, build_case()), (id_b, build_case(case_code="X2"))]

        # Act
        contexts = self.builder.build_all(cases_with_ids)

        # Assert
        assert len(contexts) == 2
        assert contexts[0].case_id == id_a
        assert contexts[1].case_id == id_b
