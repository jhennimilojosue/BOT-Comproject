"""
Upload Routes - Endpoints para gestión de Uploads.

Responsabilidades:
- Recibir archivos Excel del Maestro de Casos
- Validar y procesar archivos
- Crear registros de Upload
"""

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from ...infrastructure.catalogs.catalog_service import CatalogService
from ...infrastructure.catalogs.responsible_catalog import ResponsibleCatalog
from ...infrastructure.catalogs.status_catalog import StatusCatalog
from ...infrastructure.catalogs.time_catalog import TimeCatalog
from ...infrastructure.excel.excel_service import ExcelService
from ...infrastructure.exceptions.excel_exceptions import (
    FileValidationError,
    StructureValidationError,
)
from ...infrastructure.store import store
from ..schemas.upload import ErrorResponse, UploadCreateResponse

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

# Instancia del Excel Service
excel_service = ExcelService()


@router.post(
    "",
    response_model=UploadCreateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Cargar archivo del Maestro de Casos",
    description="Recibe un archivo Excel (.xlsx) del Maestro de Casos de Aranda y crea un Upload.",
)
async def create_upload(file: UploadFile = File(...)):
    """
    Crea un nuevo Upload a partir de un archivo Excel.

    El archivo debe:
    - Tener extensión .xlsx
    - Contener las columnas requeridas del Maestro de Casos
    - Ser legible

    Args:
        file: Archivo Excel del Maestro de Casos

    Returns:
        UploadCreateResponse con el ID del upload creado

    Raises:
        400: Si el archivo no es válido o no contiene las columnas requeridas
        500: Si ocurre un error interno
    """
    try:
        # Procesar archivo (validación + extracción de casos)
        cases = excel_service.process(file)

        # Guardar upload y casos en memoria
        from uuid import uuid4
        upload_id = uuid4()

        # Convertir casos a diccionarios para almacenamiento
        cases_dict = [case.model_dump() for case in cases]

        # Guardar en el store
        store.save_upload(upload_id, file.filename, len(cases))
        store.save_cases(upload_id, cases_dict)

        return UploadCreateResponse(
            upload_id=upload_id,
            message=f"Archivo cargado exitosamente. {len(cases)} casos extraídos.",
        )

    except FileValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_FILE",
                "message": str(e),
            },
        )
    except StructureValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STRUCTURE",
                "message": str(e),
                "details": {"missing_columns": e.missing_columns},
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al procesar el archivo: {str(e)}",
            },
        )
