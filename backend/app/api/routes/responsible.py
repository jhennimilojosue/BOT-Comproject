"""
Responsible Routes - Endpoints para consulta de responsables.

Responsabilidades:
- Listar responsables con estadísticas
- Obtener casos por responsable específico
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...infrastructure.store import store
from ..schemas.responsible import (
    CaseByResponsible,
    ResponsibleCasesResponse,
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


def _normalize_case_type(case_type: str) -> str:
    """Normaliza el tipo de caso."""
    if not case_type:
        return "No especificado"
    return CASE_TYPE_NORMALIZATION.get(case_type, case_type)


@router.get(
    "",
    response_model=ResponsibleListResponse,
    summary="Listar responsables con estadísticas",
    description="Retorna la lista de responsables con el total de casos, incidentes y requerimientos.",
)
async def list_responsibles():
    """
    Lista todos los responsables que tienen casos asignados.

    Retorna las estadísticas de cada responsable:
    - Total de casos
    - Incidentes
    - Requerimientos

    Returns:
        ResponsibleListResponse con la lista de responsables
    """
    try:
        # Obtener todos los casos
        all_cases = store.get_all_cases()

        if not all_cases:
            return ResponsibleListResponse(
                responsibles=[],
                total_responsibles=0,
            )

        # Agrupar por responsable
        responsibles_dict = {}
        for case in all_cases:
            responsible_name = case.get("responsible_name")
            if not responsible_name:
                continue

            if responsible_name not in responsibles_dict:
                responsibles_dict[responsible_name] = {
                    "name": responsible_name,
                    "total_cases": 0,
                    "incidents": 0,
                    "requirements": 0,
                }

            responsibles_dict[responsible_name]["total_cases"] += 1
            case_type = _normalize_case_type(case.get("case_type"))
            if case_type == "Incidente":
                responsibles_dict[responsible_name]["incidents"] += 1
            elif case_type == "Requerimiento":
                responsibles_dict[responsible_name]["requirements"] += 1

        # Convertir a lista y ordenar por total de casos
        responsibles_list = [
            ResponsibleStats(**data)
            for data in responsibles_dict.values()
        ]
        responsibles_list.sort(key=lambda x: x.total_cases, reverse=True)

        return ResponsibleListResponse(
            responsibles=responsibles_list,
            total_responsibles=len(responsibles_list),
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
)
async def get_cases_by_responsible(
    responsible_name: str,
    case_type: Optional[str] = Query(None, description="Filtrar por tipo: Incidente o Requerimiento"),
):
    """
    Obtiene todos los casos de un responsable específico.

    Args:
        responsible_name: Nombre del responsable
        case_type: Filtrar por tipo de caso (opcional)

    Returns:
        ResponsibleCasesResponse con los casos del responsable

    Raises:
        404: Si no se encuentra el responsable
    """
    try:
        # Obtener casos del responsable
        cases = store.get_cases_by_responsible(responsible_name)

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
            cases = [c for c in cases if _normalize_case_type(c.get("case_type")) == case_type_normalized]

        # Obtener estadísticas
        stats = store.get_responsible_stats(responsible_name)

        # Convertir casos a schema
        cases_list = [
            CaseByResponsible(
                case_code=c.get("case_code", ""),
                case_type=_normalize_case_type(c.get("case_type")),
                status=c.get("status", ""),
                final_category=c.get("final_category"),
                registered_at=c.get("registered_at"),
                description=c.get("description"),
            )
            for c in cases
        ]

        return ResponsibleCasesResponse(
            responsible_name=responsible_name,
            stats=ResponsibleStats(**stats),
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
