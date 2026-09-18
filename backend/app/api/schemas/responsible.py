"""
Responsible Schemas - Schemas de Pydantic para la API de responsables.

Responsabilidades:
- Definir contratos de entrada y salida
- Validar datos de la API
- Documentar la estructura de respuesta
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ResponsibleStats(BaseModel):
    """
    Estadísticas de un responsable.

    Attributes:
        name: Nombre del responsable
        total_cases: Total de casos asignados
        incidents: Casos de tipo Incidente
        requirements: Casos de tipo Requerimiento
    """
    name: str = Field(..., description="Nombre del responsable")
    total_cases: int = Field(..., description="Total de casos asignados")
    incidents: int = Field(..., description="Casos de tipo Incidente")
    requirements: int = Field(..., description="Casos de tipo Requerimiento")


class ResponsibleGroup(BaseModel):
    """
    Grupo de responsables con sus estadísticas.

    Attributes:
        group: Nombre del grupo
        total_cases: Total de casos del grupo
        total_responsibles: Cantidad de responsables en el grupo
        responsibles: Lista de responsables del grupo
    """
    group: str = Field(..., description="Nombre del grupo")
    total_cases: int = Field(..., description="Total de casos del grupo")
    total_responsibles: int = Field(..., description="Cantidad de responsables en el grupo")
    responsibles: List[ResponsibleStats] = Field(..., description="Lista de responsables del grupo")


class ResponsibleListResponse(BaseModel):
    """
    Respuesta con los responsables agrupados por grupo.

    Attributes:
        groups: Lista de grupos con sus responsables
        total_groups: Total de grupos encontrados
        total_responsibles: Total de responsables encontrados
    """
    groups: List[ResponsibleGroup] = Field(..., description="Lista de grupos con sus responsables")
    total_groups: int = Field(..., description="Total de grupos")
    total_responsibles: int = Field(..., description="Total de responsables")


class CaseByResponsible(BaseModel):
    """
    Caso individual filtrado por responsable.

    Attributes:
        case_code: Código del caso
        case_type: Tipo de caso (Incidente/Requerimiento)
        status: Estado del caso
        final_category: Categoría final
        registered_at: Fecha de registro
        description: Descripción del caso
        solution: Solución del caso
    """
    case_code: str = Field(..., description="Código del caso")
    case_type: str = Field(..., description="Tipo de caso")
    status: str = Field(..., description="Estado del caso")
    final_category: Optional[str] = Field(None, description="Categoría final")
    registered_at: Optional[str] = Field(None, description="Fecha de registro")
    description: Optional[str] = Field(None, description="Descripción del caso")
    solution: Optional[str] = Field(None, description="Solución del caso")


class ResponsibleCasesResponse(BaseModel):
    """
    Respuesta con los casos de un responsable específico.

    Attributes:
        responsible_name: Nombre del responsable
        processing_id: ID del último procesamiento (si existe)
        stats: Estadísticas del responsable
        cases: Lista de casos del responsable
    """
    responsible_name: str = Field(..., description="Nombre del responsable")
    upload_id: Optional[str] = Field(None, description="ID del upload consultado")
    processing_id: Optional[str] = Field(None, description="ID del último procesamiento")
    stats: ResponsibleStats = Field(..., description="Estadísticas del responsable")
    cases: List[CaseByResponsible] = Field(..., description="Lista de casos")
