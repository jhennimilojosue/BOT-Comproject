"""
AI Result Repository - Repositorio para resultados de IA.

Responsabilidades:
- Guardar resultados generados por IA
- Consultar resultados por processing_id
- Operaciones CRUD sobre la tabla ai_results
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models.ai_result import AIResultModel


class SQLAlchemyAIResultRepository:
    """Repositorio para resultados de IA en PostgreSQL."""

    def __init__(self, session: Session):
        self._session = session

    def save(
        self,
        processing_id: uuid.UUID,
        case_id: uuid.UUID,
        case_code: str,
        estimated_minutes: int,
        generated_description: str,
        model_name: str,
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        case_type: Optional[str] = None,
        status: Optional[str] = None,
        final_category: Optional[str] = None,
    ) -> AIResultModel:
        """
        Guarda un resultado de IA.

        Args:
            processing_id: ID del procesamiento
            case_id: ID del caso
            case_code: Código del caso
            estimated_minutes: Tiempo estimado en minutos
            generated_description: Descripción generada por IA
            model_name: Nombre del modelo utilizado
            tokens_used: Tokens utilizados
            latency_ms: Latencia en milisegundos
            case_type: Tipo de caso (Incidente/Requerimiento)
            status: Estado del caso
            final_category: Categoría final del caso

        Returns:
            Modelo guardado
        """
        ai_result = AIResultModel(
            processing_id=processing_id,
            case_id=case_id,
            case_code=case_code,
            estimated_minutes=estimated_minutes,
            generated_description=generated_description,
            model_name=model_name,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            case_type=case_type,
            status=status,
            final_category=final_category,
        )
        self._session.add(ai_result)
        self._session.flush()
        return ai_result

    def save_batch(self, results: List[dict]) -> List[AIResultModel]:
        """
        Guarda múltiples resultados de IA en lote.

        Args:
            results: Lista de diccionarios con los datos

        Returns:
            Lista de modelos guardados
        """
        saved = []
        for data in results:
            ai_result = AIResultModel(
                processing_id=data["processing_id"],
                case_id=data["case_id"],
                case_code=data["case_code"],
                estimated_minutes=data["estimated_minutes"],
                generated_description=data["generated_description"],
                model_name=data["model_name"],
                tokens_used=data.get("tokens_used", 0),
                latency_ms=data.get("latency_ms", 0.0),
                case_type=data.get("case_type"),
                status=data.get("status"),
                final_category=data.get("final_category"),
            )
            self._session.add(ai_result)
            saved.append(ai_result)
        self._session.flush()
        return saved

    def find_by_processing(self, processing_id: uuid.UUID) -> List[AIResultModel]:
        """
        Busca resultados por processing_id.

        Args:
            processing_id: ID del procesamiento

        Returns:
            Lista de resultados encontrados
        """
        stmt = select(AIResultModel).where(
            AIResultModel.processing_id == processing_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def find_by_case(self, case_id: uuid.UUID) -> Optional[AIResultModel]:
        """
        Busca resultado por case_id.

        Args:
            case_id: ID del caso

        Returns:
            Resultado encontrado o None
        """
        stmt = select(AIResultModel).where(AIResultModel.case_id == case_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def count_by_processing(self, processing_id: uuid.UUID) -> int:
        """
        Cuenta resultados por processing_id.

        Args:
            processing_id: ID del procesamiento

        Returns:
            Cantidad de resultados
        """
        stmt = select(AIResultModel).where(
            AIResultModel.processing_id == processing_id
        )
        return len(list(self._session.execute(stmt).scalars().all()))
