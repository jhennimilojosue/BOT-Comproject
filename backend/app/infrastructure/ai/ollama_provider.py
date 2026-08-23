import time

import httpx

from app.infrastructure.ai.ai_provider import AIProvider
from app.infrastructure.ai.models import AIConfig, AIResponse


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def generate(self, prompt: str, config: AIConfig) -> AIResponse:
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": config.temperature,
                            "num_predict": config.max_tokens,
                        },
                    },
                )
                response.raise_for_status()

                data = response.json()
                latency_ms = (time.time() - start_time) * 1000

                return AIResponse(
                    content=data.get("response", ""),
                    tokens_used=data.get("eval_count", 0),
                    latency_ms=latency_ms,
                    success=True,
                )

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error="AI_TIMEOUT",
            )

        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error=f"AI_CONNECTION_ERROR: {str(e)}",
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error=f"AI_MODEL_ERROR: {str(e)}",
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
