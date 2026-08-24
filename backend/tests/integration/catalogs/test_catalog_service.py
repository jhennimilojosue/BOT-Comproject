"""
Tests de integración para el Catalog Service.

Validan el funcionamiento del servicio centralizado de catálogos
incluyendo estados, tiempos y responsables.
"""

import pytest

from app.infrastructure.catalogs.catalog_service import CatalogService
from app.infrastructure.catalogs.status_catalog import StatusCatalog
from app.infrastructure.catalogs.time_catalog import TimeCatalog
from app.infrastructure.catalogs.responsible_catalog import ResponsibleCatalog


class TestCatalogServiceIntegration:
    """Tests de integración del Catalog Service."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.status_catalog = StatusCatalog()
        self.time_catalog = TimeCatalog()
        self.responsible_catalog = ResponsibleCatalog()
        self.service = CatalogService(
            status_catalog=self.status_catalog,
            time_catalog=self.time_catalog,
            responsible_catalog=self.responsible_catalog,
        )

    # ==================== Tests de Estados ====================

    def test_should_identify_processable_status(self):
        """Test: Debe identificar estados procesables."""
        # Act & Assert
        assert self.service.is_status_processable("Solucionado") is True
        assert self.service.is_status_processable("Cerrado") is True

    def test_should_identify_non_processable_status(self):
        """Test: Debe identificar estados no procesables."""
        # Act & Assert
        assert self.service.is_status_processable("Abierto") is False
        assert self.service.is_status_processable("En Progreso") is False

    def test_should_return_false_for_unknown_status(self):
        """Test: Debe retornar False para estados desconocidos."""
        # Act & Assert
        assert self.service.is_status_processable("EstadoInexistente") is False

    def test_should_get_status_config(self):
        """Test: Debe obtener configuración de un estado."""
        # Act
        config = self.service.get_status_config("Solucionado")

        # Assert
        assert config is not None
        assert config["estado"] == "Solucionado"
        assert config["activo"] is True
        assert config["procesable"] is True

    def test_should_return_none_for_unknown_status_config(self):
        """Test: Debe retornar None para configuración de estado desconocido."""
        # Act
        config = self.service.get_status_config("EstadoInexistente")

        # Assert
        assert config is None

    # ==================== Tests de Tiempos ====================

    def test_should_get_time_range_for_incident(self):
        """Test: Debe obtener rango de tiempo para incidente."""
        # Act
        time_range = self.service.get_time_range(
            case_type="Incidente",
            final_category="Cableado puntos de red en sedes Comware o proyectos clientes",
        )

        # Assert
        assert time_range is not None
        assert time_range["minimum_minutes"] == 30
        assert time_range["maximum_minutes"] == 60

    def test_should_get_time_range_for_requirement(self):
        """Test: Debe obtener rango de tiempo para requerimiento."""
        # Act
        time_range = self.service.get_time_range(
            case_type="Requerimiento",
            final_category="Cableado puntos de red en sedes Comware o proyectos clientes",
        )

        # Assert
        assert time_range is not None
        assert time_range["minimum_minutes"] == 45
        assert time_range["maximum_minutes"] == 90

    def test_should_return_none_for_unconfigured_category(self):
        """Test: Debe retornar None para categoría no configurada."""
        # Act
        time_range = self.service.get_time_range(
            case_type="Incidente",
            final_category="Categoría no existente",
        )

        # Assert
        assert time_range is None

    def test_should_validate_configured_category(self):
        """Test: Debe validar si una categoría está configurada."""
        # Act & Assert
        assert self.service.is_category_configured(
            case_type="Incidente",
            final_category="Configurar punto de red Usuarios y/o proyectos",
        ) is True

    def test_should_return_false_for_unconfigured_category(self):
        """Test: Debe retornar False para categoría no configurada."""
        # Act & Assert
        assert self.service.is_category_configured(
            case_type="Incidente",
            final_category="Categoría no existente",
        ) is False

    # ==================== Tests de Responsables ====================

    def test_should_get_active_responsibles(self):
        """Test: Debe obtener lista de responsables activos."""
        # Act
        responsibles = self.service.get_active_responsibles()

        # Assert
        assert len(responsibles) == 5
        for responsible in responsibles:
            assert responsible["activo"] is True

    def test_should_validate_responsible_by_id(self):
        """Test: Debe validar responsable por ID."""
        # Arrange
        responsibles = self.service.get_active_responsibles()
        responsible_id = responsibles[0]["id"]

        # Act
        is_valid = self.service.is_responsible_valid(responsible_id)

        # Assert
        assert is_valid is True

    def test_should_return_false_for_invalid_responsible_id(self):
        """Test: Debe retornar False para ID de responsable inválido."""
        # Arrange
        from uuid import uuid4
        invalid_id = uuid4()

        # Act
        is_valid = self.service.is_responsible_valid(invalid_id)

        # Assert
        assert is_valid is False

    def test_should_get_responsible_by_name(self):
        """Test: Debe obtener responsable por nombre."""
        # Act
        responsible = self.service.get_responsible_by_name("Responsable 1")

        # Assert
        assert responsible is not None
        assert responsible["nombre"] == "Responsable 1"
        assert responsible["activo"] is True

    def test_should_return_none_for_unknown_responsible_name(self):
        """Test: Debe retornar None para nombre de responsable desconocido."""
        # Act
        responsible = self.service.get_responsible_by_name("Responsable Inexistente")

        # Assert
        assert responsible is None
