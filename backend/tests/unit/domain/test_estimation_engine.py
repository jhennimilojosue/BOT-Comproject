import json

import pytest

from app.domain.estimation.exceptions.estimation_exceptions import (
    CategoryNotActiveError,
    CategoryNotFoundError,
    DescriptionEmptyError,
    TimeRangeInvalidError,
)
from app.domain.estimation.services.estimation_engine import EstimationEngine
from app.infrastructure.ai.ai_provider import AIProvider
from app.infrastructure.ai.models import AIConfig, AIResponse


class FakeCatalogService:
    def __init__(self, configured=True, time_range=(30, 60)):
        self.configured = configured
        self.time_range = time_range

    def get_time_range(self, category: str) -> tuple:
        return self.time_range

    def is_category_configured(self, category: str) -> bool:
        return self.configured


class FakeAIProvider(AIProvider):
    def __init__(self, response=None, success=True):
        if response is None and success:
            response = {"estimated_minutes": 45, "description": "Se realizó la configuración."}
        self.payload = response
        self.success = success

    async def generate(self, prompt: str, config: AIConfig) -> AIResponse:
        if not self.success:
            return AIResponse(content="", success=False, error="AI_TIMEOUT")
        return AIResponse(content=json.dumps(self.payload))

    async def health_check(self) -> bool:
        return True


def make_case_context(**overrides):
    context = {
        "codigo": "INC001245",
        "responsable": "Carlos Rodríguez",
        "proyecto": "Hospital Militar",
        "categoria_final": "Ingreso de Huella",
        "descripcion": "Se reporta inconveniente con el dispositivo.",
        "solucion": "Se realizó la configuración.",
        "estado": "Solucionado",
    }
    context.update(overrides)
    return context


def make_engine(catalog=None, ai=None):
    catalog = catalog or FakeCatalogService()
    ai = ai or FakeAIProvider()
    return EstimationEngine(catalog_service=catalog, ai_provider=ai), catalog, ai


class TestEstimationEngineHappyPath:
    async def test_should_return_valid_estimation_when_time_in_range(self):
        engine, _, _ = make_engine()

        result = await engine.estimate(make_case_context(), AIConfig())

        assert result.status == "VALID"
        assert result.estimated_minutes == 45
        assert result.description == "Se realizó la configuración."
        assert result.rejection_reason is None

    async def test_should_accept_estimation_at_lower_bound(self):
        engine, _, _ = make_engine(ai=FakeAIProvider({"estimated_minutes": 30, "description": "Trabajo realizado."}))

        result = await engine.estimate(make_case_context(), AIConfig())

        assert result.status == "VALID"
        assert result.estimated_minutes == 30

    async def test_should_accept_estimation_at_upper_bound(self):
        engine, _, _ = make_engine(ai=FakeAIProvider({"estimated_minutes": 60, "description": "Trabajo realizado."}))

        result = await engine.estimate(make_case_context(), AIConfig())

        assert result.status == "VALID"
        assert result.estimated_minutes == 60

    async def test_should_include_range_from_catalog_in_prompt(self):
        engine, catalog, ai = make_engine()

        await engine.estimate(make_case_context(), AIConfig())

        assert "Mínimo: 30" in engine._build_prompt(make_case_context(), *catalog.get_time_range("x"))


class TestEstimationEngineValidationErrors:
    async def test_should_raise_when_case_has_no_final_category(self):
        engine, _, _ = make_engine()

        with pytest.raises(CategoryNotFoundError):
            await engine.estimate(make_case_context(categoria_final=""), AIConfig())

    async def test_should_raise_when_category_not_configured_in_catalog(self):
        engine, _, _ = make_engine(catalog=FakeCatalogService(configured=False))

        with pytest.raises(CategoryNotActiveError):
            await engine.estimate(make_case_context(), AIConfig())

    async def test_should_raise_when_time_range_is_invalid(self):
        engine, _, _ = make_engine(catalog=FakeCatalogService(time_range=(60, 30)))

        with pytest.raises(TimeRangeInvalidError):
            await engine.estimate(make_case_context(), AIConfig())


class TestEstimationEngineAIResponseValidation:
    async def test_should_reject_estimation_below_minimum_range(self):
        engine, _, _ = make_engine(ai=FakeAIProvider({"estimated_minutes": 25, "description": "Trabajo."}))

        result = await engine.estimate(make_case_context(), AIConfig())

        assert result.status == "REJECTED"
        assert result.rejection_reason == "ESTIMATION_OUT_OF_RANGE"

    async def test_should_reject_estimation_above_maximum_range(self):
        engine, _, _ = make_engine(ai=FakeAIProvider({"estimated_minutes": 90, "description": "Trabajo."}))

        result = await engine.estimate(make_case_context(), AIConfig())

        assert result.status == "REJECTED"
        assert result.rejection_reason == "ESTIMATION_OUT_OF_RANGE"

    async def test_should_raise_when_description_is_empty(self):
        engine, _, _ = make_engine(ai=FakeAIProvider({"estimated_minutes": 45, "description": ""}))

        with pytest.raises(DescriptionEmptyError):
            await engine.estimate(make_case_context(), AIConfig())

    async def test_should_raise_when_ai_response_is_invalid_json(self):
        provider = FakeAIProvider()
        provider.generate_original = provider.generate

        async def bad_generate(prompt, config):
            return AIResponse(content="Creo que el tiempo adecuado sería 45 minutos.")

        provider.generate = bad_generate
        engine, _, _ = make_engine(ai=provider)

        from app.domain.estimation.exceptions.estimation_exceptions import EstimationOutOfRangeError

        with pytest.raises(EstimationOutOfRangeError):
            await engine.estimate(make_case_context(), AIConfig())

    async def test_should_raise_when_ai_service_fails(self):
        engine, _, _ = make_engine(ai=FakeAIProvider(success=False))

        from app.domain.estimation.exceptions.estimation_exceptions import EstimationOutOfRangeError

        with pytest.raises(EstimationOutOfRangeError):
            await engine.estimate(make_case_context(), AIConfig())
