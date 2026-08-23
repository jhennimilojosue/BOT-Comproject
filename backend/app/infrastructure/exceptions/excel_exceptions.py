"""
Excepciones personalizadas para el módulo de Excel Service.
Estas excepciones representan errores específicos del procesamiento de archivos Excel.
"""


class ExcelServiceError(Exception):
    """Excepción base para errores del Excel Service."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileValidationError(ExcelServiceError):
    """Excepción lanzada cuando el archivo no es válido o no soportado."""

    def __init__(self, message: str = "Archivo inválido o no soportado"):
        super().__init__(message, error_code="INVALID_FILE")


class UnreadableFileError(ExcelServiceError):
    """Excepción lanzada cuando el archivo no puede ser abierto o interpretado."""

    def __init__(self, message: str = "El archivo no puede ser abierto o interpretado"):
        super().__init__(message, error_code="UNREADABLE_FILE")


class StructureValidationError(ExcelServiceError):
    """Excepción lanzada cuando la estructura del archivo no corresponde al formato esperado."""

    def __init__(self, missing_columns: list = None, message: str = None):
        self.missing_columns = missing_columns or []
        if message is None:
            message = f"Faltan columnas obligatorias: {', '.join(self.missing_columns)}"
        super().__init__(message, error_code="REQUIRED_COLUMN_MISSING")


class InvalidDataFormatError(ExcelServiceError):
    """Excepción lanzada cuando uno o más valores no pueden convertirse al formato esperado."""

    def __init__(self, field: str, value: str, expected_format: str = None):
        self.field = field
        self.value = value
        self.expected_format = expected_format
        message = f"Valor inválido para '{field}': '{value}'"
        if expected_format:
            message += f". Formato esperado: {expected_format}"
        super().__init__(message, error_code="INVALID_DATA_FORMAT")
