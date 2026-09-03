"""
Revisa los casos procesables (en catálogo) por responsable desde la BD.
"""

import unicodedata

import psycopg2


def normalize_path(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("  ", " ")
    s = s.replace("infrastructura", "infraestructura")
    return s


def main():
    conn = psycopg2.connect(
        "postgresql://postgres:postgres@localhost:5432/bot_comproject"
    )
    cur = conn.cursor()

    # Cargar catálogo normalizado -> (min,max)
    cur.execute("SELECT path_normalizado, tiempo_min, tiempo_max FROM catalogo_tiempos")
    catalog = {}
    for p, mn, mx in cur.fetchall():
        catalog[p] = (mn, mx)

    # Cargar todos los casos
    cur.execute(
        "SELECT case_code, responsible_name, final_category, case_type "
        "FROM cases WHERE case_type IN ('Incidente','Requerimiento') "
        "ORDER BY responsible_name"
    )
    rows = cur.fetchall()

    # Agrupar por responsable
    from collections import defaultdict

    per_responsable = defaultdict(lambda: {"total": 0, "processable": 0, "not_in_catalog": 0})

    for case_code, responsible, category, case_type in rows:
        info = per_responsable[responsible]
        info["total"] += 1

        cat_norm = normalize_path(category)
        matched = False

        if cat_norm in catalog:
            matched = True
        else:
            for key in catalog:
                if key in cat_norm or cat_norm in key:
                    matched = True
                    break

        if matched:
            info["processable"] += 1
        else:
            info["not_in_catalog"] += 1

    print("=" * 70)
    print("CASOS PROCESABLES (EN CATALOGO) POR RESPONSABLE")
    print("=" * 70)
    print(f"{'Responsable':<45}{'Total':>8}{'Proc.':>8}{'No cat':>8}")
    print("-" * 70)

    for resp in sorted(per_responsable.keys()):
        info = per_responsable[resp]
        if info["processable"] > 0:
            print(f"{resp:<45}{info['total']:>8}{info['processable']:>8}{info['not_in_catalog']:>8}")

    print("-" * 70)

    conn.close()


if __name__ == "__main__":
    main()
