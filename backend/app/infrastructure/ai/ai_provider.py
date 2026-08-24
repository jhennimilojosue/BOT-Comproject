from abc import ABC, abstractmethod

from app.infrastructure.ai.models import AIConfig, AIResponse


class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, config: AIConfig) -> AIResponse:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
