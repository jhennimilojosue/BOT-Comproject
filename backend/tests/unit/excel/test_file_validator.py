"""
Tests unitarios para el File Validator.

Estos tests validan el comportamiento del componente de validación de archivos.
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from app.infrastructure.exceptions.excel_exceptions import (
    FileValidationError,
    UnreadableFileError,
)
from app.infrastructure.excel.file_validator import (
    FileValidator,
    validate_excel_file,
)


class TestFileValidator:
    """Tests para la clase FileValidator."""

    def setup_method(self):
        """Configuración inicial para cada test."""
        self.validator = FileValidator()

    def test_should_validate_xlsx_file_successfully(self):
        """Test: Debe validar exitosamente un archivo .xlsx válido."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.xlsx", file=file_content)
        file.size = 100

        # Act
        result = self.validator.validate(file)

        # Assert
        assert result is True

    def test_should_reject_non_xlsx_extension(self):
        """Test: Debe rechazar archivos con extensión no soportada."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.csv", file=file_content)
        file.size = 100

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate(file)

        assert "Extensión no soportada" in str(exc_info.value.message)
        assert exc_info.value.error_code == "INVALID_FILE"

    def test_should_reject_txt_extension(self):
        """Test: Debe rechazar archivos .txt."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.txt", file=file_content)
        file.size = 100

        # Act & Assert
        with pytest.raises(FileValidationError):
            self.validator.validate(file)

    def test_should_reject_xls_extension(self):
        """Test: Debe rechazar archivos .xls (formato antiguo)."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.xls", file=file_content)
        file.size = 100

        # Act & Assert
        with pytest.raises(FileValidationError):
            self.validator.validate(file)

    def test_should_reject_file_exceeding_max_size(self):
        """Test: Debe rechazar archivos que excedan el tamaño máximo."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.xlsx", file=file_content)
        file.size = 51 * 1024 * 1024  # 51MB

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate(file)

        assert "excede el tamaño máximo" in str(exc_info.value.message)

    def test_should_accept_file_at_max_size(self):
        """Test: Debe aceptar archivos del tamaño máximo permitido."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.xlsx", file=file_content)
        file.size = 50 * 1024 * 1024  # 50MB

        # Act
        result = self.validator.validate(file)

        # Assert
        assert result is True

    def test_should_reject_file_without_name(self):
        """Test: Debe rechazar archivos sin nombre."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename=None, file=file_content)
        file.size = 100

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate(file)

        assert "no tiene nombre" in str(exc_info.value.message)

    def test_should_reject_empty_file(self):
        """Test: Debe rechazar archivos vacíos."""
        # Arrange
        file_content = io.BytesIO(b"")
        file = UploadFile(filename="test.xlsx", file=file_content)
        file.size = 0

        # Act & Assert
        with pytest.raises(UnreadableFileError) as exc_info:
            self.validator.validate(file)

        assert "vacío" in str(exc_info.value.message)

    def test_should_reject_unreadable_file(self):
        """Test: Debe rechazar archivos que no se pueden leer."""
        # Arrange
        file = MagicMock()
        file.filename = "test.xlsx"
        file.size = 100
        file.file.read.side_effect = Exception("Error de lectura")

        # Act & Assert
        with pytest.raises(UnreadableFileError) as exc_info:
            self.validator.validate(file)

        assert "No se pudo leer" in str(exc_info.value.message)

    def test_should_validate_case_insensitive_extension(self):
        """Test: Debe validar extensión sin importar mayúsculas/minúsculas."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.XLSX", file=file_content)
        file.size = 100

        # Act
        result = self.validator.validate(file)

        # Assert
        assert result is True


class TestValidateExcelFile:
    """Tests para la función de conveniencia validate_excel_file."""

    def test_should_validate_file_successfully(self):
        """Test: Debe validar exitosamente un archivo válido."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.xlsx", file=file_content)
        file.size = 100

        # Act
        result = validate_excel_file(file)

        # Assert
        assert result is True

    def test_should_raise_exception_for_invalid_file(self):
        """Test: Debe lanzar excepción para archivo inválido."""
        # Arrange
        file_content = io.BytesIO(b"test content")
        file = UploadFile(filename="test.csv", file=file_content)
        file.size = 100

        # Act & Assert
        with pytest.raises(FileValidationError):
            validate_excel_file(file)
