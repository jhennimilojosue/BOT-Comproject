"""
File Validator - Componente del Excel Service.

Responsabilidades:
- Validar extensión del archivo (solo .xlsx)
- Validar que el archivo sea legible
- Validar que no esté corrupto

Este componente NO aplica reglas de negocio, solo validaciones técnicas.
"""

from pathlib import Path

from fastapi import UploadFile

from ..exceptions.excel_exceptions import (
    FileValidationError,
    UnreadableFileError,
)


class FileValidator:
    """
    Valida que el archivo pueda ser procesado.

    Este componente es parte del Excel Service y se encarga de:
    1. Verificar que la extensión sea .xlsx
    2. Verificar que el archivo sea legible
    3. Verificar que no esté corrupto
    """

    SUPPORTED_EXTENSIONS = {".xlsx"}
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    def validate(self, file: UploadFile) -> bool:
        """
        Valida que el archivo sea procesable.

        Args:
            file: Archivo subido por el usuario

        Returns:
            True si el archivo es válido

        Raises:
            FileValidationError: Si el archivo no es válido
            UnreadableFileError: Si el archivo no puede ser leído
        """
        self._validate_extension(file)
        self._validate_file_size(file)
        self._validate_readable(file)
        return True

    def _validate_extension(self, file: UploadFile) -> None:
        """
        Valida que la extensión del archivo sea soportada.

        Args:
            file: Archivo a validar

        Raises:
            FileValidationError: Si la extensión no es soportada
        """
        if file.filename is None:
            raise FileValidationError("El archivo no tiene nombre")

        file_path = Path(file.filename)
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise FileValidationError(
                f"Extensión no soportada: '{extension}'. "
                f"Extensiones permitidas: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    def _validate_file_size(self, file: UploadFile) -> None:
        """
        Valida que el tamaño del archivo sea aceptable.

        Args:
            file: Archivo a validar

        Raises:
            FileValidationError: Si el archivo excede el tamaño máximo
        """
        if file.size is not None and file.size > self.MAX_FILE_SIZE_BYTES:
            size_mb = file.size / (1024 * 1024)
            raise FileValidationError(
                f"El archivo excede el tamaño máximo permitido. "
                f"Tamaño: {size_mb:.2f}MB, Máximo: {self.MAX_FILE_SIZE_MB}MB"
            )

    def _validate_readable(self, file: UploadFile) -> None:
        """
        Valida que el archivo sea legible.

        Args:
            file: Archivo a validar

        Raises:
            UnreadableFileError: Si el archivo no puede ser leído
        """
        try:
            # Intentar leer el contenido del archivo
            content = file.file.read(1024)  # Leer primeros 1KB
            if not content:
                raise UnreadableFileError("El archivo está vacío")
            # Regresar al inicio del archivo
            file.file.seek(0)
        except Exception as e:
            raise UnreadableFileError(
                f"No se pudo leer el archivo: {str(e)}"
            )


def validate_excel_file(file: UploadFile) -> bool:
    """
    Función de conveniencia para validar un archivo Excel.

    Args:
        file: Archivo a validar

    Returns:
        True si el archivo es válido

    Raises:
        FileValidationError: Si el archivo no es válido
        UnreadableFileError: Si el archivo no puede ser leído
    """
    validator = FileValidator()
    return validator.validate(file)
