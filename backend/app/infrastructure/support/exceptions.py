"""
Exception Handlers - Manejadores de excepciones del sistema.

Responsabilidades:
- Definir excepciones personalizadas para cada módulo
- Proporcionar códigos de error consistentes
- Facilitar el manejo de errores en la API
"""

from typing import Optional


class BotComProjectException(Exception):
    """
    Excepción base para BOT-COMProject.

    Attributes:
        message: Mensaje de error
        error_code: Código de error
        details: Detalles adicionales del error
    """

    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        details: Optional[dict] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# ==================== Excel Service Exceptions ====================


class ExcelServiceException(BotComProjectException):
    """Excepción base para errores del Excel Service."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "EXCEL_SERVICE_ERROR", details)


class FileValidationError(ExcelServiceException):
    """Excepción para errores de validación de archivo."""

    def __init__(self, message: str = "Archivo inválido", details: Optional[dict] = None):
        super().__init__(message, details)


class StructureValidationError(ExcelServiceException):
    """Excepción para errores de estructura del archivo."""

    def __init__(self, missing_columns: list = None, details: Optional[dict] = None):
        message = f"Faltan columnas obligatorias: {', '.join(missing_columns or [])}"
        super().__init__(message, details)


# ==================== Case Management Exceptions ====================


class CaseManagementException(BotComProjectException):
    """Excepción base para errores de Gestión de Casos."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "CASE_MANAGEMENT_ERROR", details)


class InvalidCaseException(CaseManagementException):
    """Excepción para casos inválidos."""

    def __init__(self, case_code: str, reason: str, details: Optional[dict] = None):
        message = f"Caso {case_code} inválido: {reason}"
        super().__init__(message, details)


class DuplicateCaseException(CaseManagementException):
    """Excepción para casos duplicados."""

    def __init__(self, case_code: str, details: Optional[dict] = None):
        message = f"Caso {case_code} duplicado en el mismo upload"
        super().__init__(message, details)


# ==================== Catalog Service Exceptions ====================


class CatalogServiceException(BotComProjectException):
    """Excepción base para errores del Catalog Service."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "CATALOG_SERVICE_ERROR", details)


class CategoryNotConfiguredException(CatalogServiceException):
    """Excepción para categorías no configuradas."""

    def __init__(self, case_type: str, category: str, details: Optional[dict] = None):
        message = f"Categoría '{category}' no configurada para tipo '{case_type}'"
        super().__init__(message, details)


class StatusNotProcessableException(CatalogServiceException):
    """Excepción para estados no procesables."""

    def __init__(self, status: str, details: Optional[dict] = None):
        message = f"Estado '{status}' no es procesable"
        super().__init__(message, details)


# ==================== Estimation Engine Exceptions ====================


class EstimationEngineException(BotComProjectException):
    """Excepción base para errores del Estimation Engine."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "ESTIMATION_ENGINE_ERROR", details)


class EstimationOutOfRangeException(EstimationEngineException):
    """Excepción para estimaciones fuera de rango."""

    def __init__(self, estimated: int, min_val: int, max_val: int, details: Optional[dict] = None):
        message = f"Estimación {estimated} fuera de rango [{min_val}-{max_val}]"
        super().__init__(message, details)


# ==================== AI Service Exceptions ====================


class AIServiceException(BotComProjectException):
    """Excepción base para errores del AI Service."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "AI_SERVICE_ERROR", details)


class AIProviderException(AIServiceException):
    """Excepción para errores del proveedor de IA."""

    def __init__(self, message: str = "Error en el proveedor de IA", details: Optional[dict] = None):
        super().__init__(message, details)


class InvalidAIResponseException(AIServiceException):
    """Excepción para respuestas inválidas de la IA."""

    def __init__(self, message: str = "Respuesta inválida del modelo", details: Optional[dict] = None):
        super().__init__(message, details)


# ==================== Repository Exceptions ====================


class RepositoryException(BotComProjectException):
    """Excepción base para errores de repositorios."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "REPOSITORY_ERROR", details)


class EntityNotFoundException(RepositoryException):
    """Excepción para entidades no encontradas."""

    def __init__(self, entity_type: str, entity_id: str, details: Optional[dict] = None):
        message = f"{entity_type} con ID {entity_id} no encontrado"
        super().__init__(message, details)
