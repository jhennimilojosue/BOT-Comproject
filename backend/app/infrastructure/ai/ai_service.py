"""
AI Service - Servicio de IA para generación de descripciones y estimaciones.

Responsabilidades:
- Cargar prompts templates
- Generar descripciones breves usando IA
- Estimar tiempos de resolución usando IA
- Validar y parsear respuestas de IA
"""

import os
from pathlib import Path
from typing import Optional

from .ai_provider import AIProvider
from .models import AIConfig, AIResponse


class AIService:
    """
    Servicio de IA para generación de descripciones y estimaciones.

    Utiliza Ollama para generar descripciones breves y formales
    basándose en la información del caso.
    """

    def __init__(
        self,
        ai_provider: AIProvider,
        config: Optional[AIConfig] = None,
    ):
        """
        Inicializa el servicio de IA.

        Args:
            ai_provider: Proveedor de IA (Ollama)
            config: Configuración de IA (opcional)
        """
        self.ai_provider = ai_provider
        self.config = config or AIConfig()
        self._prompts_dir = Path(__file__).parent / "prompts"
        self._description_prompt = None
        self._estimation_prompt = None

    def _load_prompt(self, filename: str) -> str:
        """
        Carga un prompt template desde el archivo.

        Args:
            filename: Nombre del archivo de prompt

        Returns:
            Contenido del prompt template
        """
        prompt_path = self._prompts_dir / filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Prompt template no encontrado: {filename}")

    @property
    def description_prompt(self) -> str:
        """Carga el prompt de descripción (lazy loading)."""
        if self._description_prompt is None:
            self._description_prompt = self._load_prompt("description_prompt.txt")
        return self._description_prompt

    @property
    def estimation_prompt(self) -> str:
        """Carga el prompt de estimación (lazy loading)."""
        if self._estimation_prompt is None:
            self._estimation_prompt = self._load_prompt("estimation_prompt.txt")
        return self._estimation_prompt

    def _build_description_context(self, case: dict) -> str:
        """
        Construye el contexto para generar la descripción.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            Prompt formateado con los datos del caso
        """
        return self.description_prompt.format(
            case_code=case.get("case_code", "N/A"),
            case_type=case.get("case_type", "N/A"),
            final_category=case.get("final_category", "N/A"),
            description=case.get("description", "N/A"),
            solution=case.get("solution", "N/A"),
        )

    def _build_estimation_context(self, case: dict) -> str:
        """
        Construye el contexto para estimar el tiempo.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            Prompt formateado con los datos del caso
        """
        return self.estimation_prompt.format(
            case_code=case.get("case_code", "N/A"),
            case_type=case.get("case_type", "N/A"),
            final_category=case.get("final_category", "N/A"),
            description=case.get("description", "N/A"),
        )

    async def generate_description(self, case: dict) -> AIResponse:
        """
        Genera una descripción breve para un caso usando IA.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            AIResponse con la descripción generada
        """
        prompt = self._build_description_context(case)
        return await self.ai_provider.generate(prompt, self.config)

    async def estimate_time(self, case: dict) -> AIResponse:
        """
        Estima el tiempo de resolución para un caso usando IA.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            AIResponse con los minutos estimados
        """
        prompt = self._build_estimation_context(case)
        return await self.ai_provider.generate(prompt, self.config)

    async def process_case(self, case: dict) -> dict:
        """
        Procesa un caso completo: genera descripción y estima tiempo.

        Args:
            case: Diccionario con los datos del caso

        Returns:
            Diccionario con descripción generada y tiempo estimado
        """
        # Generar descripción
        description_response = await self.generate_description(case)

        # Estimar tiempo
        estimation_response = await self.estimate_time(case)

        # Parsear tiempo estimado
        estimated_minutes = self._parse_estimation(estimation_response.content)

        return {
            "case_code": case.get("case_code"),
            "generated_description": description_response.content,
            "estimated_minutes": estimated_minutes,
            "description_tokens": description_response.tokens_used,
            "estimation_tokens": estimation_response.tokens_used,
            "description_latency_ms": description_response.latency_ms,
            "estimation_latency_ms": estimation_response.latency_ms,
            "description_success": description_response.success,
            "estimation_success": estimation_response.success,
        }

    def _parse_estimation(self, estimation_text: str) -> int:
        """
        Parsea la respuesta de estimación de tiempo.

        Args:
            estimation_text: Texto de respuesta de la IA

        Returns:
            Minutos estimados (valor por defecto: 60)
        """
        try:
            # Limpiar el texto y extraer números
            cleaned = estimation_text.strip()
            # Buscar números en el texto
            numbers = "".join(filter(str.isdigit, cleaned))
            if numbers:
                minutes = int(numbers)
                # Validar rango razonable
                if 5 <= minutes <= 480:  # Entre 5 minutos y 8 horas
                    return minutes
            return 60  # Valor por defecto
        except (ValueError, TypeError):
            return 60  # Valor por defecto en caso de error

    async def health_check(self) -> bool:
        """
        Verifica si el servicio de IA está disponible.

        Returns:
            True si está disponible
        """
        return await self.ai_provider.health_check()
