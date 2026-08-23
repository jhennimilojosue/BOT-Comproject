from typing import Protocol

from app.domain.estimation.exceptions.estimation_exceptions import (
    CatalogServiceError,
    CategoryNotActiveError,
    CategoryNotFoundError,
    DescriptionEmptyError,
    EstimationOutOfRangeError,
    TimeRangeInvalidError,
)
from app.domain.estimation.value_objects.estimation_result import EstimationResult
from app.infrastructure.ai.ai_provider import AIProvider
from app.infrastructure.ai.models import AIConfig


class CatalogServiceProtocol(Protocol):
    def get_time_range(self, category: str) -> tuple[int, int]:
        pass

    def is_category_configured(self, category: str) -> bool:
        pass


class EstimationEngine:
    def __init__(self, catalog_service: CatalogServiceProtocol, ai_provider: AIProvider):
        self.catalog_service = catalog_service
        self.ai_provider = ai_provider

    async def estimate(self, case_context: dict, config: AIConfig) -> EstimationResult:
        category = case_context.get("categoria_final")
        if not category:
            raise CategoryNotFoundError("")

        if not self.catalog_service.is_category_configured(category):
            raise CategoryNotActiveError(category)

        try:
            min_time, max_time = self.catalog_service.get_time_range(category)
        except Exception as e:
            raise CatalogServiceError(str(e))

        if min_time >= max_time:
            raise TimeRangeInvalidError(min_time, max_time)

        prompt = self._build_prompt(case_context, min_time, max_time)
        ai_response = await self.ai_provider.generate(prompt, config)

        if not ai_response.success:
            raise EstimationOutOfRangeError(0, min_time, max_time)

        try:
            import json
            response_data = json.loads(ai_response.content)
            estimated_minutes = response_data.get("estimated_minutes")
            description = response_data.get("description")
        except (json.JSONDecodeError, AttributeError):
            raise EstimationOutOfRangeError(0, min_time, max_time)

        if estimated_minutes is None or not isinstance(estimated_minutes, (int, float)):
            raise EstimationOutOfRangeError(0, min_time, max_time)

        if not description or not description.strip():
            raise DescriptionEmptyError()

        estimated_minutes = int(estimated_minutes)

        if estimated_minutes < min_time or estimated_minutes > max_time:
            return EstimationResult(
                estimated_minutes=estimated_minutes,
                description=description,
                status="REJECTED",
                rejection_reason="ESTIMATION_OUT_OF_RANGE",
            )

        return EstimationResult(
            estimated_minutes=estimated_minutes,
            description=description,
            status="VALID",
        )

    def _build_prompt(self, case_context: dict, min_time: int, max_time: int) -> str:
        return f"""Eres un asistente encargado de analizar casos de soporte y generar una recomendación de tiempo y una descripción profesional.

Debes utilizar exclusivamente la información proporcionada.
No debes inventar información.
No debes modificar la categoría.
No debes crear reglas.
Debes recomendar un tiempo dentro del rango autorizado.
Debes responder exclusivamente en el formato JSON solicitado.

Información del caso:
- Código: {case_context.get('codigo', 'N/A')}
- Proyecto: {case_context.get('proyecto', 'N/A')}
- Categoría final: {case_context.get('categoria_final', 'N/A')}
- Descripción: {case_context.get('descripcion', 'N/A')}
- Solución: {case_context.get('solucion', 'N/A')}
- Estado: {case_context.get('estado', 'N/A')}

Rango autorizado:
- Mínimo: {min_time} minutos
- Máximo: {max_time} minutos

Responde únicamente con el siguiente formato JSON:
{{
    "estimated_minutes": <número entero entre {min_time} y {max_time}>,
    "description": "<descripción profesional de la actividad realizada>"
}}"""
