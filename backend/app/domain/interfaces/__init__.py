"""
Domain Interfaces - Interfaces de dominio.

Este módulo contiene las interfaces que definen los contratos
para acceso a datos y servicios externos.
"""

from .repositories import (
    CaseRepository,
    EstimationRepository,
    ProcessingRejectionRepository,
    ProcessingRepository,
    UploadRepository,
)

__all__ = [
    "CaseRepository",
    "EstimationRepository",
    "ProcessingRejectionRepository",
    "ProcessingRepository",
    "UploadRepository",
]
