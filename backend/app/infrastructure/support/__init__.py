"""
Support Module - Módulo de soporte y utilidades.

Este módulo contiene configuración, logging, manejo de excepciones
y utilidades de verificación del sistema.
"""

from .config import Settings, load_settings, settings
from .exceptions import (
    AIProviderException,
    AIServiceException,
    BotComProjectException,
    CatalogServiceException,
    CategoryNotConfiguredException,
    DuplicateCaseException,
    EntityNotFoundException,
    EstimationEngineException,
    EstimationOutOfRangeException,
    InvalidAIResponseException,
    InvalidCaseException,
    RepositoryException,
    StatusNotProcessableException,
)
from .health_check import HealthChecker
from .logger import (
    ai_logger,
    api_logger,
    case_logger,
    catalog_logger,
    estimation_logger,
    excel_logger,
    processing_logger,
    setup_logger,
)

__all__ = [
    # Config
    "Settings",
    "load_settings",
    "settings",
    # Exceptions
    "BotComProjectException",
    "ExcelServiceException",
    "FileValidationError",
    "StructureValidationError",
    "CaseManagementException",
    "InvalidCaseException",
    "DuplicateCaseException",
    "CatalogServiceException",
    "CategoryNotConfiguredException",
    "StatusNotProcessableException",
    "EstimationEngineException",
    "EstimationOutOfRangeException",
    "AIServiceException",
    "AIProviderException",
    "InvalidAIResponseException",
    "RepositoryException",
    "EntityNotFoundException",
    # Health Check
    "HealthChecker",
    # Logger
    "setup_logger",
    "excel_logger",
    "case_logger",
    "processing_logger",
    "estimation_logger",
    "ai_logger",
    "catalog_logger",
    "api_logger",
]
