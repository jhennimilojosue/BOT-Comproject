"""
Processing Service - Servicio de procesamiento de casos.

Responsabilidades:
- Recibir casos de un Upload
- Filtrar casos por estado (procesables vs no procesables)
- Aplicar lookups de catálogos (tiempos, responsables)
- Crear registros de procesamiento
- Retornar resultados del procesamiento

Este servicio orquesta la lógica de negocio del procesamiento de casos.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID, uuid4

from ..catalogs.catalog_service import CatalogService
from ..exceptions.processing_exceptions import (
    CategoryNotConfiguredException,
    ResponsibleNotFoundException,
    StatusNotProcessableException,
)


@dataclass
class CaseProcessingResult:
    """
    Resultado del procesamiento de un caso individual.

    Attributes:
        case_code: Código del caso
        case_type: Tipo de caso (Incidente/Requerimiento)
        status: Estado del caso
        is_processable: Si el caso es procesable
        rejection_reason: Razón de rechazo (si aplica)
        estimated_minutes: Minutos estimados (si aplica)
        responsible_name: Nombre del responsable
    """
    case_code: str
    case_type: str
    status: str
    is_processable: bool
    rejection_reason: Optional[str] = None
    estimated_minutes: Optional[int] = None
    responsible_name: Optional[str] = None


@dataclass
class ProcessingResult:
    """
    Resultado total del procesamiento de un lote de casos.

    Attributes:
        processing_id: Identificador de la ejecución
        total_cases: Total de casos recibidos
        processed_cases: Casos procesados exitosamente
        rejected_cases: Casos rechazados
        results: Lista de resultados individuales
    """
    processing_id: UUID
    total_cases: int
    processed_cases: int
    rejected_cases: int
    results: List[CaseProcessingResult]


class ProcessingService:
    """
    Servicio de procesamiento de casos.

    Orquesta la lógica de negocio para procesar casos del Maestro de Casos,
    aplicando reglas de filtrado por estado y lookups de catálogos.
    """

    # Mapa de normalización para tipos de caso del Excel
    CASE_TYPE_NORMALIZATION = {
        "INCIDENTES": "Incidente",
        "REQUERIMIENTOS": "Requerimiento",
        "INCIDENTE": "Incidente",
        "REQUERIMIENTO": "Requerimiento",
    }

    def __init__(self, catalog_service: CatalogService):
        """
        Inicializa el Processing Service.

        Args:
            catalog_service: Servicio centralizado de catálogos
        """
        self.catalog_service = catalog_service

    def _normalize_case_type(self, case_type: str) -> str:
        """
        Normaliza el tipo de caso del Excel al formato del catálogo.

        Args:
            case_type: Tipo de caso del Excel (ej: INCIDENTES, REQUERIMIENTOS)

        Returns:
            Tipo de caso normalizado (ej: Incidente, Requerimiento)
        """
        if not case_type:
            return "No especificado"
        return self.CASE_TYPE_NORMALIZATION.get(case_type, case_type)

    def process_cases(
        self,
        cases: List[dict],
        responsible_id: Optional[UUID] = None,
    ) -> ProcessingResult:
        """
        Procesa un lote de casos del Maestro de Casos.

        Args:
            cases: Lista de casos extraídos del Excel
            responsible_id: UUID del responsable seleccionado (opcional)

        Returns:
            ProcessingResult con los resultados del procesamiento
        """
        processing_id = uuid4()
        results: List[CaseProcessingResult] = []

        for case in cases:
            result = self._process_single_case(case)
            results.append(result)

        processed = sum(1 for r in results if r.is_processable)
        rejected = sum(1 for r in results if not r.is_processable)

        return ProcessingResult(
            processing_id=processing_id,
            total_cases=len(cases),
            processed_cases=processed,
            rejected_cases=rejected,
            results=results,
        )

    def process_cases_by_responsible(
        self,
        cases: List[dict],
        responsible_name: str,
    ) -> ProcessingResult:
        """
        Procesa casos filtrados por responsable.

        Args:
            cases: Lista de casos extraídos del Excel
            responsible_name: Nombre del responsable a filtrar

        Returns:
            ProcessingResult con los resultados del procesamiento
        """
        processing_id = uuid4()
        results: List[CaseProcessingResult] = []

        for case in cases:
            result = self._process_single_case(case)
            results.append(result)

        processed = sum(1 for r in results if r.is_processable)
        rejected = sum(1 for r in results if not r.is_processable)

        return ProcessingResult(
            processing_id=processing_id,
            total_cases=len(cases),
            processed_cases=processed,
            rejected_cases=rejected,
            results=results,
        )

    def _process_single_case(self, case: dict) -> CaseProcessingResult:
        """
        Procesa un caso individual.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            CaseProcessingResult con el resultado del procesamiento
        """
        case_code = case.get("case_code", "UNKNOWN")
        case_type = self._normalize_case_type(case.get("case_type"))
        status = case.get("status") or "No especificado"
        final_category = case.get("final_category") or "No especificado"

        # Verificar si el estado es procesable
        is_processable = self.catalog_service.is_status_processable(status)

        if not is_processable:
            return CaseProcessingResult(
                case_code=case_code,
                case_type=case_type,
                status=status,
                is_processable=False,
                rejection_reason=f"Estado '{status}' no es procesable",
            )

        # Buscar configuración de tiempo para la categoría
        time_config = self.catalog_service.get_time_range(case_type, final_category)

        # Si la categoría no está configurada, usar valores por defecto
        if time_config is None:
            # Usar valores por defecto para categorías no configuradas
            estimated_minutes = 60  # 1 hora por defecto
        else:
            # Calcular minutos estimados (promedio del rango)
            min_minutes = time_config.get("minimum_minutes", 0)
            max_minutes = time_config.get("maximum_minutes", 0)
            estimated_minutes = (min_minutes + max_minutes) // 2

        # Obtener nombre del responsable
        responsible_name = case.get("responsible_name") or "Sin asignar"

        return CaseProcessingResult(
            case_code=case_code,
            case_type=case_type,
            status=status,
            is_processable=True,
            estimated_minutes=estimated_minutes,
            responsible_name=responsible_name,
        )
