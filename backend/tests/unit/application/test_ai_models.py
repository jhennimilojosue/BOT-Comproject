import pytest
from pydantic import ValidationError

from app.infrastructure.ai.models import AIConfig, AIResponse


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
