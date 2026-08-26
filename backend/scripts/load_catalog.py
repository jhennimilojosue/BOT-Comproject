"""
Script para cargar el catálogo de tiempos desde Excel a PostgreSQL.

Uso:
    cd C:\\Bot-Comproject
    python -m backend.scripts.load_catalog

Este script lee el archivo test_data/catalogo_tiempos.xlsx y carga
las categorías y tiempos en la tabla catalogo_tiempos de PostgreSQL.
"""

import os
import sys
import uuid
import unicodedata

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


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


def load_catalog(file_path: str, db_config: dict) -> int:
    """
    Carga el catálogo de tiempos desde Excel a PostgreSQL.

    Args:
        file_path: Ruta al archivo Excel
        db_config: Configuración de conexión a la BD

    Returns:
        Cantidad de registros insertados
    """
    print(f"Leyendo archivo: {file_path}")

    # Leer Excel
    df = pd.read_excel(file_path, header=0)
    print(f"Filas leídas: {len(df)}")

    # Renombrar columnas
    df.columns = ["idx", "Categoria", "Subcategoria", "Item", "TiempoMin", "TiempoMax"]
    df = df.iloc[1:]  # Eliminar fila de encabezado duplicado
    df = df.dropna(subset=["TiempoMin", "TiempoMax"])

    # Procesar categorías
    records = []
    last_cat = None
    last_sub = None

    for _, row in df.iterrows():
        # Obtener valores (usar anterior si es NaN)
        cat = str(row["Categoria"]).strip() if pd.notna(row["Categoria"]) else last_cat
        sub = str(row["Subcategoria"]).strip() if pd.notna(row["Subcategoria"]) else last_sub
        item = str(row["Item"]).strip() if pd.notna(row["Item"]) else None

        # Actualizar últimos valores
        if pd.notna(row["Categoria"]):
            last_cat = cat
        if pd.notna(row["Subcategoria"]):
            last_sub = sub

        # Construir path completo
        parts = [p for p in [cat, sub, item] if p]
        path_completo = ".".join(parts)
        path_normalizado = normalize_path(path_completo)

        records.append(
            (
                cat,
                sub,
                item,
                path_completo,
                path_normalizado,
                int(row["TiempoMin"]),
                int(row["TiempoMax"]),
            )
        )

    print(f"Registros a insertar: {len(records)}")

    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        host=db_config["host"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"],
    )
    cursor = conn.cursor()

    # Limpiar tabla existente
    cursor.execute("DELETE FROM catalogo_tiempos")
    deleted = cursor.rowcount
    print(f"Registros eliminados: {deleted}")

    # Insertar nuevos registros
    records_with_uuid = [(str(uuid.uuid4()),) + r for r in records]

    insert_sql = """
        INSERT INTO catalogo_tiempos (
            id, nivel1, nivel2, nivel3,
            path_completo, path_normalizado,
            tiempo_min, tiempo_max
        ) VALUES %s
    """

    execute_values(cursor, insert_sql, records_with_uuid)
    inserted = len(records)
    print(f"Registros insertados: {inserted}")

    # Commit
    conn.commit()
    cursor.close()
    conn.close()

    return inserted


def main():
    """Función principal del script."""
    # Configuración de la BD
    db_config = {
        "host": "localhost",
        "database": "botcomproject",
        "user": "postgres",
        "password": "postgres",
    }

    # Ruta al archivo Excel
    file_path = r"C:\Bot-Comproject\test_data\catalogo_tiempos.xlsx"

    if not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo {file_path}")
        sys.exit(1)

    try:
        inserted = load_catalog(file_path, db_config)
        print(f"\nCatálogo cargado exitosamente: {inserted} categorías")
    except Exception as e:
        print(f"Error al cargar catálogo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
