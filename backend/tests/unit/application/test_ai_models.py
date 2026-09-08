import pytest
from pydantic import ValidationError

from app.infrastructure.ai.models import AIConfig, AIResponse


def _build_ai_result(case_code: str, area, fecha_solucion=None):
    from app.api.schemas.ai import AIResultResponse

    return AIResultResponse(
        case_code=case_code,
        final_category="Cat.A.B",
        status="Cerrado",
        case_type="Requerimiento",
        area=area,
        fecha_solucion=fecha_solucion,
        generated_description="Se realizó la gestión del caso.",
        estimated_minutes=45,
        model_name="qwen2.5-coder:3b",
        tokens_used=10,
        latency_ms=100.0,
    )


class TestGroupResultsByArea:
    def test_should_group_results_by_area_preserving_order(self):
        from app.api.routes.ai import _group_results_by_area

        results = [
            _build_ai_result("1", "Gestion Humana", fecha_solucion="2026-09-05"),
            _build_ai_result("2", "Proyecto La Previsora", fecha_solucion="2026-09-06"),
            _build_ai_result("3", "Gestion Humana", fecha_solucion="2026-09-05"),
        ]

        grouped = _group_results_by_area(results)

        assert list(grouped.keys()) == ["Gestion Humana", "Proyecto La Previsora"]

        gh = grouped["Gestion Humana"]
        assert gh["total_hours"] == 1.5  # 2 casos * 45 min
        assert list(gh["by_date"].keys()) == ["2026-09-05"]
        assert [r.case_code for r in gh["by_date"]["2026-09-05"]["cases"]] == ["1", "3"]
        assert gh["by_date"]["2026-09-05"]["total_hours"] == 1.5
        assert gh["sin_fecha"]["cases"] == []

        prev = grouped["Proyecto La Previsora"]
        assert [r.case_code for r in prev["by_date"]["2026-09-06"]["cases"]] == ["2"]

    def test_should_assign_none_area_to_sin_area(self):
        from app.api.routes.ai import _group_results_by_area

        results = [
            _build_ai_result("1", None, fecha_solucion="2026-09-05"),
            _build_ai_result("2", "Gestion Humana"),
        ]

        grouped = _group_results_by_area(results)

        assert list(grouped.keys()) == ["Sin área", "Gestion Humana"]
        assert [r.case_code for r in grouped["Sin área"]["by_date"]["2026-09-05"]["cases"]] == ["1"]

    def test_should_group_cases_without_solution_date_under_sin_fecha(self):
        from app.api.routes.ai import _group_results_by_area

        results = [
            _build_ai_result("1", "Gestion Humana", fecha_solucion=None),
            _build_ai_result("2", "Gestion Humana", fecha_solucion="2026-09-05"),
        ]

        grouped = _group_results_by_area(results)

        gh = grouped["Gestion Humana"]
        assert gh["total_hours"] == 1.5
        assert [r.case_code for r in gh["sin_fecha"]["cases"]] == ["1"]
        assert gh["sin_fecha"]["total_hours"] == 0.75
        assert [r.case_code for r in gh["by_date"]["2026-09-05"]["cases"]] == ["2"]

    def test_should_return_empty_dict_for_no_results(self):
        from app.api.routes.ai import _group_results_by_area

        assert _group_results_by_area([]) == {}


class TestAIConfig:
    def test_should_use_default_values_when_not_provided(self):
        config = AIConfig()

        assert config.model == "qwen2.5-coder:3b"
        assert config.temperature == 0.3
        assert config.timeout == 60
        assert config.max_tokens == 500

    def test_should_accept_custom_values(self):
        config = AIConfig(model="llama3:latest", temperature=0.5, timeout=30, max_tokens=200)

        assert config.model == "llama3:latest"
        assert config.temperature == 0.5
        assert config.timeout == 30
        assert config.max_tokens == 200

    def test_should_reject_negative_timeout(self):
        with pytest.raises(ValidationError):
            AIConfig(timeout=-1)

    def test_should_reject_zero_max_tokens(self):
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=0)

    def test_should_reject_temperature_above_limit(self):
        with pytest.raises(ValidationError):
            AIConfig(temperature=3.0)


class TestAIResponse:
    def test_should_require_content(self):
        with pytest.raises(ValidationError):
            AIResponse()

    def test_should_default_success_to_true(self):
        response = AIResponse(content="ok")

        assert response.success is True
        assert response.error is None

    def test_should_allow_error_response_with_empty_content(self):
        response = AIResponse(content="", success=False, error="AI_TIMEOUT")

        assert response.success is False
        assert response.error == "AI_TIMEOUT"
