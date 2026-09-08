"""
Limpieza de datos de uploads en BOT-COMProject.

Elimina todos los uploads y sus datos dependientes:
  ai_results, estimations, processing_rejections, processings, cases, uploads

CONSERVA el catálogo de tiempos (catalogo_tiempos).

Uso:
    cd C:\\Bot-Comproject
    .\\backend\\venv\\Scripts\\python.exe -m backend.scripts.clear_uploads
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import text

from app.infrastructure.database.connection import db_config

# Orden de borrado por dependencias (las FKs no usan ON DELETE CASCADE)
TABLES_IN_ORDER = [
    "ai_results",
    "estimations",
    "processing_rejections",
    "processings",
    "cases",
    "uploads",
]


def main() -> None:
    print("=" * 60)
    print("LIMPIEZA DE UPLOADS")
    print("=" * 60)

    with db_config.engine.begin() as conn:
        for table in TABLES_IN_ORDER:
            result = conn.execute(text(f"DELETE FROM {table}"))
            print(f"[OK] {table}: {result.rowcount} filas eliminadas")

        catalog_count = conn.execute(text("SELECT COUNT(*) FROM catalogo_tiempos")).scalar()
        print(f"[OK] catalogo_tiempos conservado: {catalog_count} categorías")

    print("=" * 60)
    print("Limpieza completada. El sistema quedó listo para un nuevo upload.")
    print("=" * 60)


if __name__ == "__main__":
    main()