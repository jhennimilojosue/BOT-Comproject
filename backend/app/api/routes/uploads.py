"""
Upload Routes - Endpoints para gestión de Uploads.

Responsabilidades:
- Recibir archivos Excel del Maestro de Casos
- Validar y procesar archivos
- Crear registros de Upload en PostgreSQL
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...domain.entities.case import Case, CaseType
from ...domain.entities.upload import Upload, UploadStatus
from ...infrastructure.database.connection import db_config
from ...infrastructure.exceptions.excel_exceptions import (
    FileValidationError,
    StructureValidationError,
)
from ...infrastructure.excel.excel_service import ExcelService
from ...infrastructure.database.models.processing import ProcessingModel
from ...infrastructure.repositories.case_repository import SQLAlchemyCaseRepository
from ...infrastructure.repositories.upload_repository import SQLAlchemyUploadRepository
from ..dependencies import get_db
from ..schemas.upload import ErrorResponse, UploadCreateResponse

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

# Instancia del Excel Service
excel_service = ExcelService()


@router.get(
    "",
    summary="Listar uploads existentes",
    description="Retorna la lista de uploads cargados con su ID, nombre de archivo y fecha.",
    operation_id="list_uploads",
)
async def list_uploads(db: Session = Depends(get_db)):
    """Lista todos los uploads existentes en la base de datos."""
    from ...infrastructure.database.models.upload import UploadModel

    uploads = db.query(UploadModel).order_by(UploadModel.created_at.desc()).all()
    return {
        "uploads": [
            {
                "upload_id": str(u.id),
                "filename": u.filename,
                "status": u.status,
                "total_cases": u.total_cases,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in uploads
        ],
        "total": len(uploads),
    }


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
async def create_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo Upload a partir de un archivo Excel.

    Args:
        file: Archivo Excel del Maestro de Casos
        db: Sesión de base de datos

    Returns:
        UploadCreateResponse con el ID del upload creado
    """
    try:
        # Procesar archivo (validación + extracción de casos)
        excel_cases = excel_service.process(file)

        # Crear entidad Upload
        upload_id = uuid4()
        upload = Upload(
            id=upload_id,
            filename=file.filename,
            status=UploadStatus.PENDING,
            total_cases=len(excel_cases),
        )

        # Guardar Upload en PostgreSQL
        upload_repo = SQLAlchemyUploadRepository(db)
        upload_repo.save(upload)

        # Mapa de normalización de tipos de caso
        CASE_TYPE_NORMALIZATION = {
            "INCIDENTES": "Incidente",
            "REQUERIMIENTOS": "Requerimiento",
            "INCIDENTE": "Incidente",
            "REQUERIMIENTO": "Requerimiento",
        }

        def normalize_case_type(case_type: str) -> CaseType:
            if not case_type:
                return CaseType.INCIDENT
            normalized = CASE_TYPE_NORMALIZATION.get(case_type, case_type)
            return CaseType(normalized)

        # Convertir casos del Excel a entidades de dominio
        cases = []
        for excel_case in excel_cases:
            case = Case(
                upload_id=upload_id,
                case_code=excel_case.case_code,
                case_type=normalize_case_type(excel_case.case_type),
                responsible_name=excel_case.responsible_name,
                user_name=excel_case.user_name,
                project=excel_case.project or "COMProject",  # Valor por defecto si no existe en Excel
                registered_at=excel_case.registered_at,
                status=excel_case.status,
                final_category=excel_case.final_category,
                description=excel_case.description or "Sin descripción",
                solution=excel_case.solution or "Sin solución",
            )
            cases.append(case)

        # Guardar Cases en PostgreSQL
        case_repo = SQLAlchemyCaseRepository(db)
        case_repo.save_batch(cases)

        # Crear el Processing del archivo: un único processing_id por upload.
        # Los resultados de IA de todos los responsables se acumulan bajo él.
        processing_id = uuid4()
        processing = ProcessingModel(
            id=processing_id,
            upload_id=upload_id,
            responsible_id=None,
            responsible_name=None,
            status="pending",
            total_cases=len(cases),
        )
        db.add(processing)
        db.commit()
        db.refresh(processing)

        return UploadCreateResponse(
            upload_id=upload_id,
            processing_id=processing_id,
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
