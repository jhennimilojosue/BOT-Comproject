"""
Response Parser - Parser para respuestas de IA.

Responsabilidades:
- Limpiar y validar respuestas de IA
- Extraer descripciones generadas
- Extraer estimaciones de tiempo
- Validar formato de respuestas
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedDescription:
    """Descripción parseada y validada."""
    text: str
    is_valid: bool
    starts_with_se_realizo: bool
    length: int
    error: Optional[str] = None


@dataclass
class ParsedEstimation:
    """Estimación parseada y validada."""
    minutes: int
    is_valid: bool
    in_range: bool
    error: Optional[str] = None


class ResponseParser:
    """
    Parser para respuestas de IA.

    Valida y limpia las respuestas generadas por el modelo de IA
    para asegurar que cumplan con los requisitos del sistema.
    """

    # Patrones para limpiar respuestas
    QUOTES_PATTERN = re.compile(r'^["\']|["\']$')
    WHITESPACE_PATTERN = re.compile(r'\s+')

    # Rangos de tiempo válidos
    MIN_MINUTES = 5
    MAX_MINUTES = 480  # 8 horas

    def parse_description(self, raw_response: str) -> ParsedDescription:
        """
        Parsea y valida una descripción generada por IA.

        Args:
            raw_response: Respuesta cruda de la IA

        Returns:
            ParsedDescription con la descripción parseada
        """
        if not raw_response or not raw_response.strip():
            return ParsedDescription(
                text="",
                is_valid=False,
                starts_with_se_realizo=False,
                length=0,
                error="Respuesta vacía"
            )

        # Limpiar la respuesta
        cleaned = self._clean_response(raw_response)

        # Verificar que comience con "Se realizó"
        starts_with_se_realizo = cleaned.lower().startswith("se realizó")

        # Validar longitud
        length = len(cleaned)
        is_valid = (
            starts_with_se_realizo and
            length > 15 and  # Mínimo "Se realizó X."
            length < 200  # Máximo razonable
        )

        return ParsedDescription(
            text=cleaned,
            is_valid=is_valid,
            starts_with_se_realizo=starts_with_se_realizo,
            length=length,
            error=None if is_valid else self._get_description_error(cleaned)
        )

    def parse_estimation(self, raw_response: str) -> ParsedEstimation:
        """
        Parsea y valida una estimación de tiempo generada por IA.

        Args:
            raw_response: Respuesta cruda de la IA

        Returns:
            ParsedEstimation con la estimación parseada
        """
        if not raw_response or not raw_response.strip():
            return ParsedEstimation(
                minutes=60,
                is_valid=False,
                in_range=False,
                error="Respuesta vacía"
            )

        # Extraer número de la respuesta
        minutes = self._extract_minutes(raw_response)

        # Validar rango
        in_range = self.MIN_MINUTES <= minutes <= self.MAX_MINUTES
        is_valid = in_range

        return ParsedEstimation(
            minutes=minutes,
            is_valid=is_valid,
            in_range=in_range,
            error=None if is_valid else f"Fuera de rango: {minutes} minutos"
        )

    def _clean_response(self, response: str) -> str:
        """
        Limpia una respuesta de IA.

        Args:
            response: Respuesta cruda

        Returns:
            Respuesta limpia
        """
        # Eliminar comillas al inicio y final
        cleaned = self.QUOTES_PATTERN.sub("", response.strip())

        # Eliminar saltos de línea múltiples
        cleaned = self.WHITESPACE_PATTERN.sub(" ", cleaned)

        # Eliminar espacios al inicio y final
        cleaned = cleaned.strip()

        # Asegurar que termine con punto
        if cleaned and not cleaned.endswith("."):
            cleaned += "."

        return cleaned

    def _extract_minutes(self, response: str) -> int:
        """
        Extrae los minutos de una respuesta.

        Args:
            response: Respuesta de la IA

        Returns:
            Número de minutos extraído
        """
        try:
            # Buscar números en la respuesta
            numbers = re.findall(r'\d+', response)
            if numbers:
                # Tomar el primer número encontrado
                minutes = int(numbers[0])
                return minutes
            return 60  # Valor por defecto
        except (ValueError, IndexError):
            return 60  # Valor por defecto

    def _get_description_error(self, description: str) -> str:
        """
        Genera un mensaje de error para descripciones inválidas.

        Args:
            description: Descripción a evaluar

        Returns:
            Mensaje de error
        """
        if not description.lower().startswith("se realizó"):
            return "La descripción no comienza con 'Se realizó'"
        if len(description) <= 15:
            return "La descripción es demasiado corta"
        if len(description) >= 200:
            return "La descripción es demasiado larga"
        return "Descripción no válida"

    def validate_batch(self, results: list[dict]) -> dict:
        """
        Valida un lote de resultados de IA.

        Args:
            results: Lista de resultados de IA

        Returns:
            Estadísticas de validación
        """
        total = len(results)
        valid_descriptions = 0
        valid_estimations = 0
        errors = []

        for result in results:
            # Validar descripción
            desc_parsed = self.parse_description(result.get("generated_description", ""))
            if desc_parsed.is_valid:
                valid_descriptions += 1
            else:
                errors.append({
                    "case_code": result.get("case_code"),
                    "type": "description",
                    "error": desc_parsed.error
                })

            # Validar estimación
            est_parsed = self.parse_estimation(str(result.get("estimated_minutes", "")))
            if est_parsed.is_valid:
                valid_estimations += 1
            else:
                errors.append({
                    "case_code": result.get("case_code"),
                    "type": "estimation",
                    "error": est_parsed.error
                })

        return {
            "total": total,
            "valid_descriptions": valid_descriptions,
            "valid_estimations": valid_estimations,
            "description_accuracy": valid_descriptions / total if total > 0 else 0,
            "estimation_accuracy": valid_estimations / total if total > 0 else 0,
            "errors": errors
        }
