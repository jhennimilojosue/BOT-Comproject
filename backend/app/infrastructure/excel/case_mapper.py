"""
Case Mapper - Componente del Excel Service.

Responsabilidades:
- Construir los objetos ExcelCaseDTO a partir de los registros normalizados
- Garantizar que la salida cumpla el Case Contract

Este componente NO aplica reglas de negocio de procesabilidad.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ExcelCaseDTO(BaseModel):
    """
    DTO del caso proveniente del Maestro de Casos de Aranda.

    Representa únicamente la información original del Excel.
    Los campos id, upload_id, responsible_id y created_at son generados
    por el sistema y no forman parte de este DTO.
    """

    case_code: str = Field(..., min_length=1, max_length=50)
    case_type: Optional[str] = Field(default=None, max_length=50)
    responsible_name: str = Field(..., min_length=1, max_length=200)
    user_name: Optional[str] = Field(default=None, max_length=200)
    groups: Optional[str] = Field(default=None, max_length=200)
    area: Optional[str] = Field(default=None, max_length=200)
    project: Optional[str] = Field(default=None, max_length=200)
    registered_at: str = Field(
        ...,
        description="Fecha de registro en formato ISO 8601: YYYY-MM-DD",
    )
    status: str = Field(..., min_length=1, max_length=100)
    final_category: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    solution: Optional[str] = Field(default=None)
    fecha_solucion: Optional[str] = Field(
        default=None,
        description="Fecha de solución en formato ISO 8601: YYYY-MM-DD",
    )


class CaseMapper:
    """
    Construye los objetos ExcelCaseDTO utilizados por el resto del sistema.

    Este componente es parte del Excel Service y se encarga de:
    1. Validar que cada registro normalizado cumpla el Case Contract
    2. Convertir registros crudos a ExcelCaseDTO tipados
    """

    def map(self, records: List[Dict[str, Optional[str]]]) -> List[ExcelCaseDTO]:
        """
        Convierte una colección de registros normalizados a ExcelCaseDTO.

        Args:
            records: Registros normalizados provenientes del DataNormalizer

        Returns:
            Lista de ExcelCaseDTO validados según el Case Contract

        Raises:
            ValidationError (pydantic): Si un registro no cumple el contrato
        """
        return [ExcelCaseDTO(**record) for record in records]


def map_to_excel_cases(
    records: List[Dict[str, Optional[str]]]
) -> List[ExcelCaseDTO]:
    """
    Función de conveniencia para convertir registros a ExcelCaseDTO.

    Args:
        records: Registros normalizados

    Returns:
        Lista de ExcelCaseDTO

    Raises:
        ValidationError (pydantic): Si un registro no cumple el contrato
    """
    mapper = CaseMapper()
    return mapper.map(records)
