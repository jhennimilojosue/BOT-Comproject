from typing import Optional

from pydantic import BaseModel, Field


class AIConfig(BaseModel):
    model: str = Field(default="qwen2.5-coder:3b", description="AI model to use")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    timeout: int = Field(default=60, gt=0, description="Timeout in seconds")
    max_tokens: int = Field(default=500, gt=0, description="Max tokens in response")


class AIResponse(BaseModel):
    content: str = Field(..., description="AI response content")
    tokens_used: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    success: bool = Field(default=True)
    error: Optional[str] = Field(default=None)
