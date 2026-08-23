"""
Paquete de excepciones personalizadas para infraestructura.
"""

from .excel_exceptions import (
    ExcelServiceError,
    FileValidationError,
    UnreadableFileError,
    StructureValidationError,
    InvalidDataFormatError,
)

__all__ = [
    "ExcelServiceError",
    "FileValidationError",
    "UnreadableFileError",
    "StructureValidationError",
    "InvalidDataFormatError",
]
