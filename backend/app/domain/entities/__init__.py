"""
Domain Entities - Entidades de dominio del sistema.

Este módulo contiene las entidades que representan los conceptos
principales del dominio de BOT-COMProject.
"""

from .ai_result import AIResult
from .case import Case, CaseType
from .estimation import Estimation, EstimationStatus
from .processing import Processing, ProcessingStatus
from .processing_rejection import ProcessingRejection, RejectionReason
from .upload import Upload, UploadStatus

__all__ = [
    "AIResult",
    "Case",
    "CaseType",
    "Estimation",
    "EstimationStatus",
    "Processing",
    "ProcessingStatus",
    "ProcessingRejection",
    "RejectionReason",
    "Upload",
    "UploadStatus",
]
