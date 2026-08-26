"""
Catalogo Tiempo Repository - Repositorio para el catálogo de tiempos.

Responsabilidades:
- Cargar categorías desde PostgreSQL
- Buscar categorías por path normalizado
- Operaciones CRUD sobre la tabla catalogo_tiempos
"""

import unicodedata
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models.catalogo_tiempos import CatalogoTiempoModel


def normalize_path(s: str) -> str:
    """
    Normaliza un path de categoría.

    - Convierte a minúsculas
    - Elimina tildes
    - Corrige typos comunes
    - Elimina espacios extra

    Args:
        s: String a normalizar

    Returns:
        String normalizado
    """
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("  ", " ")
    # Fix common typos
    s = s.replace("infrastructura", "infraestructura")
    return s


class SQLAlchemyCatalogoTiempoRepository:
    """Repositorio para el catálogo de tiempos en PostgreSQL."""

    def __init__(self, session: Session):
        self._session = session
        self._cache: Optional[Dict[str, CatalogoTiempoModel]] = None

    def _load_cache(self) -> Dict[str, CatalogoTiempoModel]:
        """Carga todas las categorías en memoria (cache)."""
        if self._cache is None:
            stmt = select(CatalogoTiempoModel)
            results = self._session.execute(stmt).scalars().all()
            self._cache = {r.path_normalizado: r for r in results}
        return self._cache

    def find_by_path(self, path: str) -> Optional[CatalogoTiempoModel]:
        """
        Busca una categoría por su path normalizado.

        Args:
            path: Path de la categoría a buscar

        Returns:
            Categoría encontrada o None
        """
        cache = self._load_cache()
        normalized = normalize_path(path)

        # Búsqueda exacta
        if normalized in cache:
            return cache[normalized]

        # Búsqueda parcial (el path contiene la clave o viceversa)
        for key, value in cache.items():
            if key in normalized or normalized in key:
                return value

        return None

    def get_all(self) -> List[CatalogoTiempoModel]:
        """
        Obtiene todas las categorías del catálogo.

        Returns:
            Lista de categorías
        """
        cache = self._load_cache()
        return list(cache.values())

    def get_time_range(self, path: str) -> Optional[Dict[str, int]]:
        """
        Obtiene el rango de tiempo para una categoría.

        Args:
            path: Path de la categoría

        Returns:
            Dict con min y max en minutos, o None si no existe
        """
        category = self.find_by_path(path)
        if category:
            return {"min": category.tiempo_min, "max": category.tiempo_max}
        return None

    def get_all_paths(self) -> List[str]:
        """
        Obtiene todos los paths normalizados del catálogo.

        Returns:
            Lista de paths normalizados
        """
        cache = self._load_cache()
        return list(cache.keys())

    def clear_cache(self) -> None:
        """Limpia el cache."""
        self._cache = None
