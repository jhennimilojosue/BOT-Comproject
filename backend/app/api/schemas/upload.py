"""
Upload Schemas - Schemas de Pydantic para la API de Uploads.

Responsabilidades:
- Definir contratos de entrada y salida
- Validar datos de la API
- Documentar la estructura de respuesta
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """
    Schema de respuesta para un Upload.

    Attributes:
        id: Identificador del upload
        filename: Nombre del archivo
        status: Estado de la carga
        total_cases: Total de casos extraídos
        created_at: Fecha de creación
    """
    id: UUID = Field(..., description="Identificador del upload")
    filename: str = Field(..., description="Nombre del archivo")
    status: str = Field(..., description="Estado de la carga")
    total_cases: Optional[int] = Field(None, description="Total de casos extraídos")
    created_at: datetime = Field(..., description="Fecha de creación")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "maestro_casos.xlsx",
                "status": "pending",
                "total_cases": None,
                "created_at": "2026-08-23T20:00:00",
            }
        }


class UploadCreateResponse(BaseModel):
    """
    Schema de respuesta al crear un Upload.

    Attributes:
        upload_id: Identificador del upload creado
        processing_id: Identificador del processing del archivo (un processing por upload)
        message: Mensaje de confirmación
    """
    upload_id: UUID = Field(..., description="Identificador del upload creado")
    processing_id: UUID = Field(..., description="Identificador del processing del archivo")
    message: str = Field(..., description="Mensaje de confirmación")

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "processing_id": "750e8400-e29b-41d4-a716-446655440002",
                "message": "Archivo cargado exitosamente",
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema de respuesta de error.

    Attributes:
        error: Código de error
        message: Mensaje de error
        details: Detalles adicionales
    """
    error: str = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[dict] = Field(None, description="Detalles adicionales")
