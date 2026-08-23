"""
Case Context Builder - Componente de Gestión de Casos.

Responsabilidades (gestion_casos.md sección 21):
- Construir el contexto necesario para Estimation Engine
- Incluir únicamente la información necesaria para la estimación

El contexto NO es un nuevo Case, NO lo reemplaza y NO modifica
el caso original. Este componente NO:
- Calcula tiempos.
- Determina rangos.
- Genera recomendaciones.
- Consulta Ollama directamente.
"""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class CaseContext(BaseModel):
    """
    Contexto de procesamiento para Estimation Engine.

    Representación específica del caso para las etapas posteriores.
    No reemplaza al Case original ni contiene resultados de estimación.
    """

    case_id: UUID = Field(..., description="Identificador interno del Case")
    case_code: str = Field(..., description="Código original de Aranda")
    responsible_name: str = Field(..., description="Responsable original")
    project: str = Field(...)
    final_category: str = Field(...)
    description: str = Field(...)
    solution: str = Field(...)
    status: str = Field(...)


class CaseContextBuilder:
    """
    Construye la información necesaria para Estimation Engine.

    Este componente forma parte de Gestión de Casos y se ubica al final
    del pipeline, recibiendo únicamente casos ya clasificados como
    procesables.
    """

    def build(self, case_id: UUID, case: BaseModel) -> CaseContext:
        """
        Construye el contexto a partir de un caso procesable.

        Args:
            case_id: Identificador interno del Case
            case: DTO del caso compatible con el Case Contract

        Returns:
            CaseContext listo para Estimation Engine

        Raises:
            ValidationError (pydantic): Si faltan campos requeridos
                para construir el contexto
        """
        data = case.model_dump()

        return CaseContext(
            case_id=case_id,
            case_code=data["case_code"],
            responsible_name=data["responsible_name"],
            project=data["project"],
            final_category=data["final_category"],
            description=data["description"],
            solution=data["solution"],
            status=data["status"],
        )

    def build_all(
        self, cases_with_ids: List[tuple[UUID, BaseModel]]
    ) -> List[CaseContext]:
        """
        Construye contextos para una colección de casos procesables.

        Args:
            cases_with_ids: Lista de tuplas (case_id, case)

        Returns:
            Lista de CaseContext
        """
        return [self.build(case_id, case) for case_id, case in cases_with_ids]
