"""
Tests de integración para las entidades de dominio.

Validan el funcionamiento de las entidades y sus relaciones.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.domain.entities.upload import Upload, UploadStatus
from app.domain.entities.case import Case, CaseType
from app.domain.entities.processing import Processing, ProcessingStatus
from app.domain.entities.processing_rejection import ProcessingRejection, RejectionReason
from app.domain.entities.estimation import Estimation, EstimationStatus
from app.domain.entities.ai_result import AIResult


class TestUploadEntity:
    """Tests para la entidad Upload."""

    def test_should_create_upload_with_defaults(self):
        """Test: Debe crear un Upload con valores por defecto."""
        # Act
        upload = Upload(filename="test.xlsx")

        # Assert
        assert upload.id is not None
        assert upload.filename == "test.xlsx"
        assert upload.status == UploadStatus.PENDING
        assert upload.total_cases is None
        assert upload.created_at is not None

    def test_should_mark_as_processing(self):
        """Test: Debe marcar como en proceso."""
        # Arrange
        upload = Upload(filename="test.xlsx")

        # Act
        upload.mark_as_processing()

        # Assert
        assert upload.status == UploadStatus.PROCESSING

    def test_should_mark_as_completed(self):
        """Test: Debe marcar como completado."""
        # Arrange
        upload = Upload(filename="test.xlsx")

        # Act
        upload.mark_as_completed(total_cases=10)

        # Assert
        assert upload.status == UploadStatus.COMPLETED
        assert upload.total_cases == 10

    def test_should_mark_as_failed(self):
        """Test: Debe marcar como fallido."""
        # Arrange
        upload = Upload(filename="test.xlsx")

        # Act
        upload.mark_as_failed()

        # Assert
        assert upload.status == UploadStatus.FAILED

    def test_should_validate_is_processable(self):
        """Test: Debe validar si es procesable."""
        # Arrange
        upload = Upload(filename="test.xlsx")

        # Act & Assert
        assert upload.is_processable is False

        upload.mark_as_completed(total_cases=10)
        assert upload.is_processable is True


class TestCaseEntity:
    """Tests para la entidad Case."""

    def test_should_create_case_with_required_fields(self):
        """Test: Debe crear un Case con campos obligatorios."""
        # Arrange
        upload_id = uuid4()

        # Act
        case = Case(
            upload_id=upload_id,
            case_code="INC001245",
            case_type=CaseType.INCIDENT,
            responsible_name="Carlos Rodríguez",
            project="Hospital Militar",
            registered_at=datetime.now(),
            status="Solucionado",
            final_category="Ingreso de Huella",
            description="Descripción del caso",
            solution="Solución del caso",
        )

        # Assert
        assert case.id is not None
        assert case.upload_id == upload_id
        assert case.case_code == "INC001245"
        assert case.case_type == CaseType.INCIDENT
        assert case.responsible_name == "Carlos Rodríguez"

    def test_should_validate_responsible(self):
        """Test: Debe validar responsable."""
        # Arrange
        case = Case(
            upload_id=uuid4(),
            case_code="INC001245",
            case_type=CaseType.INCIDENT,
            responsible_name="Carlos Rodríguez",
            project="Hospital Militar",
            registered_at=datetime.now(),
            status="Solucionado",
            final_category="Ingreso de Huella",
            description="Descripción",
            solution="Solución",
        )

        # Act & Assert
        assert case.is_responsible("Carlos Rodríguez") is True
        assert case.is_responsible("carlos rodríguez") is True
        assert case.is_responsible("Juan Pérez") is False

    def test_should_identify_case_type(self):
        """Test: Debe identificar tipo de caso."""
        # Arrange
        incident = Case(
            upload_id=uuid4(),
            case_code="INC001",
            case_type=CaseType.INCIDENT,
            responsible_name="Test",
            project="Test",
            registered_at=datetime.now(),
            status="Solucionado",
            final_category="Test",
            description="Test",
            solution="Test",
        )

        requirement = Case(
            upload_id=uuid4(),
            case_code="REQ001",
            case_type=CaseType.REQUIREMENT,
            responsible_name="Test",
            project="Test",
            registered_at=datetime.now(),
            status="Solucionado",
            final_category="Test",
            description="Test",
            solution="Test",
        )

        # Act & Assert
        assert incident.is_incident is True
        assert incident.is_requirement is False
        assert requirement.is_incident is False
        assert requirement.is_requirement is True

    def test_should_generate_context_dict(self):
        """Test: Debe generar diccionario de contexto."""
        # Arrange
        case = Case(
            upload_id=uuid4(),
            case_code="INC001245",
            case_type=CaseType.INCIDENT,
            responsible_name="Carlos Rodríguez",
            project="Hospital Militar",
            registered_at=datetime.now(),
            status="Solucionado",
            final_category="Ingreso de Huella",
            description="Descripción",
            solution="Solución",
        )

        # Act
        context = case.to_context_dict()

        # Assert
        assert context["case_code"] == "INC001245"
        assert context["case_type"] == "Incidente"
        assert context["responsible_name"] == "Carlos Rodríguez"
        assert context["project"] == "Hospital Militar"


class TestProcessingEntity:
    """Tests para la entidad Processing."""

    def test_should_create_processing_with_defaults(self):
        """Test: Debe crear un Processing con valores por defecto."""
        # Arrange
        upload_id = uuid4()
        responsible_id = uuid4()

        # Act
        processing = Processing(
            upload_id=upload_id,
            responsible_id=responsible_id,
        )

        # Assert
        assert processing.id is not None
        assert processing.upload_id == upload_id
        assert processing.responsible_id == responsible_id
        assert processing.status == ProcessingStatus.PENDING

    def test_should_mark_as_processing(self):
        """Test: Debe marcar como en proceso."""
        # Arrange
        processing = Processing(
            upload_id=uuid4(),
            responsible_id=uuid4(),
        )

        # Act
        processing.mark_as_processing(total_cases=10)

        # Assert
        assert processing.status == ProcessingStatus.PROCESSING
        assert processing.total_cases == 10
        assert processing.started_at is not None

    def test_should_mark_as_completed(self):
        """Test: Debe marcar como completado."""
        # Arrange
        processing = Processing(
            upload_id=uuid4(),
            responsible_id=uuid4(),
        )
        processing.mark_as_processing(total_cases=10)

        # Act
        processing.mark_as_completed(processed_cases=8, rejected_cases=2)

        # Assert
        assert processing.status == ProcessingStatus.COMPLETED
        assert processing.processed_cases == 8
        assert processing.rejected_cases == 2
        assert processing.completed_at is not None

    def test_should_calculate_processing_rate(self):
        """Test: Debe calcular tasa de procesamiento."""
        # Arrange
        processing = Processing(
            upload_id=uuid4(),
            responsible_id=uuid4(),
        )
        processing.mark_as_processing(total_cases=100)

        # Act
        processing.mark_as_completed(processed_cases=80, rejected_cases=20)

        # Assert
        assert processing.processing_rate == 80.0


class TestEstimationEntity:
    """Tests para la entidad Estimation."""

    def test_should_create_estimation(self):
        """Test: Debe crear una Estimation."""
        # Arrange
        processing_id = uuid4()
        case_id = uuid4()

        # Act
        estimation = Estimation(
            processing_id=processing_id,
            case_id=case_id,
            case_code="INC001245",
            estimated_minutes=35,
            minimum_minutes=30,
            maximum_minutes=60,
            final_category="Ingreso de Huella",
        )

        # Assert
        assert estimation.id is not None
        assert estimation.estimated_minutes == 35
        assert estimation.status == EstimationStatus.VALID

    def test_should_validate_within_range(self):
        """Test: Debe validar si está dentro del rango."""
        # Arrange
        estimation = Estimation(
            processing_id=uuid4(),
            case_id=uuid4(),
            case_code="INC001245",
            estimated_minutes=35,
            minimum_minutes=30,
            maximum_minutes=60,
            final_category="Test",
        )

        # Act & Assert
        assert estimation.is_within_range is True

    def test_should_mark_as_rejected(self):
        """Test: Debe marcar como rechazada."""
        # Arrange
        estimation = Estimation(
            processing_id=uuid4(),
            case_id=uuid4(),
            case_code="INC001245",
            estimated_minutes=25,
            minimum_minutes=30,
            maximum_minutes=60,
            final_category="Test",
        )

        # Act
        estimation.mark_as_rejected("Tiempo fuera de rango")

        # Assert
        assert estimation.status == EstimationStatus.REJECTED
        assert estimation.rejection_reason == "Tiempo fuera de rango"


class TestAIResultEntity:
    """Tests para la entidad AIResult."""

    def test_should_create_ai_result(self):
        """Test: Debe crear un AIResult."""
        # Arrange
        processing_id = uuid4()
        case_id = uuid4()

        # Act
        ai_result = AIResult(
            processing_id=processing_id,
            case_id=case_id,
            case_code="INC001245",
            estimated_minutes=35,
            generated_description="Se realizó la configuración correspondiente.",
            model_name="qwen2.5:latest",
        )

        # Assert
        assert ai_result.id is not None
        assert ai_result.estimated_minutes == 35
        assert ai_result.model_name == "qwen2.5:latest"

    def test_should_validate_has_description(self):
        """Test: Debe validar si tiene descripción."""
        # Arrange
        ai_result = AIResult(
            processing_id=uuid4(),
            case_id=uuid4(),
            case_code="INC001245",
            estimated_minutes=35,
            generated_description="Descripción generada",
            model_name="qwen2.5:latest",
        )

        # Act & Assert
        assert ai_result.has_description is True
