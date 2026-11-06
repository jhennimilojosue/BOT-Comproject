"""
Catalogo Tiempo Repository - Repositorio para el catálogo de tiempos.

Responsabilidades:
- Cargar categorías desde PostgreSQL
- Buscar categorías por path normalizado y tipo de caso
- Operaciones CRUD sobre la tabla catalogo_tiempos
"""

import unicodedata
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models.catalogo_tiempos import CatalogoTiempoModel


def normalize_path(s: str) -> str:
    """
    Normaliza un path de categor��a.

    - Convierte a minúsculas
    - Elimina tildes
    - Corrige typos comunes
    - Normaliza espacios alrededor de puntuación (guiones, puntos, barras)
    - Elimina espacios extra

    Args:
        s: String a normalizar

    Returns:
        String normalizado
    """
    import re
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # Normalize spacing around punctuation
    s = re.sub(r"\s*[-/]\s*", "-", s)  # - / with optional spaces -> -
    s = re.sub(r"\s*\.\s*", ".", s)    # . with optional spaces -> .
    s = re.sub(r"\s+", " ", s)         # multiple spaces -> single space
    # Fix common typos
    s = s.replace("infrastructura", "infraestructura")
    return s


class SQLAlchemyCatalogoTiempoRepository:
    """Repositorio para el catálogo de tiempos en PostgreSQL."""

    def __init__(self, session: Session):
        self._session = session
        self._cache: Optional[Dict[Tuple[str, str], CatalogoTiempoModel]] = None

    def _load_cache(self) -> Dict[Tuple[str, str], CatalogoTiempoModel]:
        """Carga todas las categorías en memoria (cache)."""
        if self._cache is None:
            stmt = select(CatalogoTiempoModel)
            results = self._session.execute(stmt).scalars().all()
            self._cache = {
                (r.case_type, r.path_normalizado): r
                for r in results
            }
        return self._cache

    def find_by_path(
        self,
        path: str,
        case_type: str = "Requerimiento",
    ) -> Optional[CatalogoTiempoModel]:
        """
        Busca una categoría por su path normalizado y tipo de caso.

        Args:
            path: Path de la categoría a buscar
            case_type: Tipo de caso (Incidente/Requerimiento)

        Returns:
            Categoría encontrada o None
        """
        cache = self._load_cache()
        normalized = normalize_path(path)

        # Si el case_type no es reconocido, intentar "Requerimiento"
        case_type = case_type if case_type in ("Incidente", "Requerimiento") else "Requerimiento"

        # Búsqueda exacta
        exact_key = (case_type, normalized)
        if exact_key in cache:
            return cache[exact_key]

        # Búsqueda parcial (el path contiene la clave o viceversa)
        # Filtrar solo entradas del mismo tipo de caso
        for (ctype, key), value in cache.items():
            if ctype == case_type and (key in normalized or normalized in key):
                return value

        return None

    def get_all(self, case_type: Optional[str] = None) -> List[CatalogoTiempoModel]:
        """
        Obtiene todas las categorías del catálogo.

        Args:
            case_type: Si se indica, filtra por tipo de caso (opcional)

        Returns:
            Lista de categorías
        """
        cache = self._load_cache()
        if case_type is None:
            return list(cache.values())
        return [v for (ctype, _), v in cache.items() if ctype == case_type]

    def get_time_range(self, path: str, case_type: str = "Requerimiento") -> Optional[Dict[str, int]]:
        """
        Obtiene el rango de tiempo para una categoría.

        Args:
            path: Path de la categoría
            case_type: Tipo de caso (Incidente/Requerimiento)

        Returns:
            Dict con min y max en minutos, o None si no existe
        """
        category = self.find_by_path(path, case_type)
        if category:
            return {"min": category.tiempo_min, "max": category.tiempo_max}
        return None

    def get_all_paths(self, case_type: Optional[str] = None) -> List[str]:
        """
        Obtiene todos los paths normalizados del catálogo.

        Args:
            case_type: Si se indica, filtra por tipo de caso (opcional)

        Returns:
            Lista de paths normalizados
        """
        cache = self._load_cache()
        if case_type is None:
            return [key for (ctype, key) in cache.keys()]
        return [key for (ctype, key) in cache.keys() if ctype == case_type]

    def clear_cache(self) -> None:
        """Limpia el cache."""
        self._cache = None