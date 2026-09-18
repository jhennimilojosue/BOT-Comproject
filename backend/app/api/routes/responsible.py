"""
Responsible Routes - Endpoints para consulta de responsables.

Responsabilidades:
- Listar responsables con estadísticas
- Obtener casos por responsable específico
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...infrastructure.database.models.case import CaseModel
from ...infrastructure.database.models.processing import ProcessingModel
from ...infrastructure.database.models.upload import UploadModel
from ..dependencies import get_db
from ..schemas.responsible import (
    CaseByResponsible,
    ResponsibleCasesResponse,
    ResponsibleGroup,
    ResponsibleListResponse,
    ResponsibleStats,
)

router = APIRouter(prefix="/api/v1/cases/responsible", tags=["responsible"])

# Mapa de normalización de tipos de caso
CASE_TYPE_NORMALIZATION = {
    "INCIDENTES": "Incidente",
    "REQUERIMIENTOS": "Requerimiento",
    "INCIDENTE": "Incidente",
    "REQUERIMIENTO": "Requerimiento",
}

# Grupos permitidos para listar responsables (columna "Grupos" del maestro de casos)
ALLOWED_GROUPS = {
    "service desk": "Service Desk",
    "soporte en sitio corporativo": "Soporte en sitio Corporativo",
    "soporte en sitio regional cali": "Soporte en sitio regional Cali",
    "soporte en sitio regional med": "Soporte en sitio regional Med",
}


def _normalize_group(groups: Optional[str]) -> str:
    """Normaliza el valor de la columna Grupos (minúsculas, sin espacios extremos)."""
    if not groups:
        return ""
    return " ".join(groups.strip().lower().split())


def _is_allowed_group(groups: Optional[str]) -> bool:
    """Indica si el caso pertenece a uno de los grupos permitidos."""
    return _normalize_group(groups) in ALLOWED_GROUPS


def _normalize_case_type(case_type: str) -> str:
    """Normaliza el tipo de caso."""
    if not case_type:
        return "No especificado"
    return CASE_TYPE_NORMALIZATION.get(case_type, case_type)


def _resolve_upload_id(db: Session, upload_id: Optional[str] = None) -> Optional[str]:
    """
    Resuelve el upload_id a usar para filtrar los casos.

    Si no se indica, usa el upload más reciente.

    Args:
        db: Sesión de base de datos
        upload_id: ID de upload opcional

    Returns:
        ID del upload resuelto o None si no hay uploads
    """
    if upload_id:
        upload = (
            db.query(UploadModel)
            .filter(UploadModel.id == upload_id)
            .first()
        )
        if not upload:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "UPLOAD_NOT_FOUND",
                    "message": f"No se encontró el upload '{upload_id}'",
                },
            )
        return str(upload.id)

    latest = (
        db.query(UploadModel)
        .order_by(UploadModel.created_at.desc())
        .first()
    )
    return str(latest.id) if latest else None


@router.get(
    "",
    response_model=ResponsibleListResponse,
    summary="Listar responsables con estadísticas",
    description="Retorna la lista de responsables con el total de casos, incidentes y requerimientos.",
    operation_id="list_responsibles_responsible",
)
async def list_responsibles(
    upload_id: Optional[str] = Query(None, description="ID del upload a filtrar (por defecto usa el más reciente)"),
    db: Session = Depends(get_db),
):
    """
    Lista todos los responsables que tienen casos asignados.

    Returns:
        ResponsibleListResponse con la lista de responsables
    """
    try:
        # Obtener todos los casos
        resolved_upload = _resolve_upload_id(db, upload_id)
        if resolved_upload is None:
            return ResponsibleListResponse(
                groups=[],
                total_groups=0,
                total_responsibles=0,
            )

        query = db.query(CaseModel).filter(CaseModel.upload_id == resolved_upload)
        all_cases = query.all()

        if not all_cases:
            return ResponsibleListResponse(
                groups=[],
                total_groups=0,
                total_responsibles=0,
            )

        # Agrupar por grupo y responsable (solo casos de los grupos permitidos)
        groups_dict = {}
        for case in all_cases:
            if not _is_allowed_group(case.groups):
                continue

            group_key = _normalize_group(case.groups)
            group_name = ALLOWED_GROUPS[group_key]

            responsible_name = case.responsible_name
            if not responsible_name:
                continue

            group_data = groups_dict.setdefault(
                group_name,
                {"group": group_name, "responsibles": {}},
            )

            if responsible_name not in group_data["responsibles"]:
                group_data["responsibles"][responsible_name] = {
                    "name": responsible_name,
                    "total_cases": 0,
                    "incidents": 0,
                    "requirements": 0,
                }

            group_data["responsibles"][responsible_name]["total_cases"] += 1
            case_type = _normalize_case_type(case.case_type)
            if case_type == "Incidente":
                group_data["responsibles"][responsible_name]["incidents"] += 1
            elif case_type == "Requerimiento":
                group_data["responsibles"][responsible_name]["requirements"] += 1

        # Convertir a estructura groups, ordenando responsables por total de casos
        groups_list = []
        total_responsibles = 0
        for group_name, group_data in groups_dict.items():
            responsibles_list = [
                ResponsibleStats(**data)
                for data in group_data["responsibles"].values()
            ]
            responsibles_list.sort(key=lambda x: x.total_cases, reverse=True)
            total_cases = sum(r.total_cases for r in responsibles_list)
            groups_list.append(
                ResponsibleGroup(
                    group=group_name,
                    total_cases=total_cases,
                    total_responsibles=len(responsibles_list),
                    responsibles=responsibles_list,
                )
            )
            total_responsibles += len(responsibles_list)

        return ResponsibleListResponse(
            groups=groups_list,
            total_groups=len(groups_list),
            total_responsibles=total_responsibles,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener responsables: {str(e)}",
            },
        )


@router.get(
    "/{responsible_name}",
    response_model=ResponsibleCasesResponse,
    summary="Obtener casos por responsable",
    description="Retorna todos los casos de un responsable específico con sus estadísticas.",
    operation_id="get_cases_by_responsible_name",
)
async def get_cases_by_responsible(
    responsible_name: str,
    case_type: Optional[str] = Query(None, description="Filtrar por tipo: Incidente o Requerimiento"),
    upload_id: Optional[str] = Query(None, description="ID del upload a filtrar (por defecto usa el más reciente)"),
    db: Session = Depends(get_db),
):
    """
    Obtiene todos los casos de un responsable específico.

    Args:
        responsible_name: Nombre del responsable
        case_type: Filtrar por tipo de caso (opcional)
        upload_id: ID del upload a filtrar (opcional)

    Returns:
        ResponsibleCasesResponse con los casos del responsable
    """
    try:
        resolved_upload = _resolve_upload_id(db, upload_id)
        if resolved_upload is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NO_UPLOADS",
                    "message": "No hay uploads registrados",
                },
            )

        # Buscar casos por responsable y upload
        query = (
            db.query(CaseModel)
            .filter(
                CaseModel.responsible_name == responsible_name,
                CaseModel.upload_id == resolved_upload,
            )
        )
        cases = query.all()

        if not cases:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "RESPONSABLE_NOT_FOUND",
                    "message": f"No se encontraron casos para el responsable '{responsible_name}'",
                },
            )

        # Filtrar por tipo si se especifica
        if case_type:
            case_type_normalized = _normalize_case_type(case_type)
            cases = [c for c in cases if _normalize_case_type(c.case_type) == case_type_normalized]

        # Calcular estadísticas
        total = len(cases)
        incidents = sum(1 for c in cases if _normalize_case_type(c.case_type) == "Incidente")
        requirements = sum(1 for c in cases if _normalize_case_type(c.case_type) == "Requerimiento")

        # Convertir casos a schema
        cases_list = [
            CaseByResponsible(
                case_code=c.case_code,
                case_type=_normalize_case_type(c.case_type),
                status=c.status,
                final_category=c.final_category,
                registered_at=c.registered_at.isoformat() if c.registered_at else None,
                description=c.description,
                solution=c.solution,
            )
            for c in cases
        ]

        # Buscar último processing del responsable para el upload resuelto
        latest_processing = (
            db.query(ProcessingModel)
            .filter(
                ProcessingModel.responsible_name == responsible_name,
                ProcessingModel.upload_id == resolved_upload,
            )
            .order_by(ProcessingModel.created_at.desc())
            .first()
        )

        processing_id = str(latest_processing.id) if latest_processing else None

        return ResponsibleCasesResponse(
            responsible_name=responsible_name,
            upload_id=resolved_upload,
            processing_id=processing_id,
            stats=ResponsibleStats(
                name=responsible_name,
                total_cases=total,
                incidents=incidents,
                requirements=requirements,
            ),
            cases=cases_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Error al obtener casos del responsable: {str(e)}",
            },
        )
