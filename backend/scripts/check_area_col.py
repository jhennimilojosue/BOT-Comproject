"""Check Area column recognition in maestro_de_casos_09.xlsx"""
import pandas as pd
import unicodedata

CHARACTER_NORMALIZATION = {
    "\xf3": "ó", "\xf1": "ñ", "\xed": "í", "\xe1": "á", "\xe9": "é", "\xfa": "ú",
}

REQUIRED_COLUMNS = {"Cod Caso", "Tipo Caso", "Responsable", "Fecha de Registro", "Estado", "Categoria", "Descripción", "Solucion"}
COLUMN_MAPPING = {
    "Cod Caso": "case_code", "Tipo Caso": "case_type", "Responsable": "responsible_name",
    "Fecha de Registro": "registered_at", "Estado": "status", "Categoria": "final_category",
    "Descripción": "description", "Solucion": "solution", "Usuario": "user_name",
    "Area": "area", "Fecha de Solución": "fecha_solucion",
}

def norm(name):
    n = name.strip()
    for corrupted, correct in CHARACTER_NORMALIZATION.items():
        n = n.replace(corrupted, correct)
    return n

df = pd.read_excel(r"C:\BOT-Comproject\test_data\maestro_de_casos_09.xlsx", header=None, nrows=10)

best_row = None
best_matches = 0
for i in range(min(10, len(df))):
    row_vals = set(norm(str(v)) for v in df.iloc[i].dropna().astype(str))
    matches = len(row_vals & REQUIRED_COLUMNS)
    print(f"  Row {i}: {matches} matches, vals={sorted(row_vals)[:8]}")
    if matches > best_matches:
        best_matches = matches
        best_row = i

print(f"\nHeader row: {best_row}, matches: {best_matches}/{len(REQUIRED_COLUMNS)}")

if best_row is not None:
    headers = [norm(str(h)) for h in df.iloc[best_row]]
    print(f"Total headers: {len(headers)}")

    # Check all headers
    for i, h in enumerate(headers):
        marker = " <-- AREA" if "area" in h.lower() else ""
        print(f"  [{i:2d}] {repr(h)}{marker}")

    # Check get_mapping
    df_columns = set(headers)
    mapping = {k: v for k, v in COLUMN_MAPPING.items() if k in df_columns}
    print(f"\nMapped fields: {list(mapping.values())}")
    area_mapped = "area" in mapping.values()
    print(f"Area mapped: {area_mapped}")
    unrecognized = sorted(df_columns - set(COLUMN_MAPPING.keys()))
    print(f"Unrecognized: {unrecognized[:15]}")
    print(f"Missing required: {REQUIRED_COLUMNS - df_columns}")
