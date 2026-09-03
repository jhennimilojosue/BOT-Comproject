"""
Test de procesamiento IA sin base de datos.
Lee el Excel directamente y procesa casos con Ollama.

Uso:
    cd C:\\BOT-Comproject
    .\\backend\\venv\\Scripts\\python.exe -m backend.scripts.test_ai_process
"""

import json
import time
import unicodedata

import httpx
import pandas as pd

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:3b"
EXCEL_PATH = r"C:\BOT-Comproject\test_data\maestro_de_casos.xlsx"
CATALOG_PATH = r"C:\BOT-Comproject\test_data\catalogo_tiempos.xlsx"

RESPONSABLE = "Brayan Jesiet Filot Diaz"


def normalize_text(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("infrastructura", "infraestructura")
    return s


def load_catalog(path: str) -> dict:
    """Carga catálogo desde Excel, retorna {path_normalizado: (min, max)}."""
    df = pd.read_excel(path, header=0)
    df.columns = ["idx", "Categoria", "Subcategoria", "Item", "TiempoMin", "TiempoMax"]
    df = df.iloc[1:]
    df = df.dropna(subset=["TiempoMin", "TiempoMax"])

    catalog = {}
    last_cat = None
    last_sub = None

    for _, row in df.iterrows():
        cat = str(row["Categoria"]).strip() if pd.notna(row["Categoria"]) else last_cat
        sub = str(row["Subcategoria"]).strip() if pd.notna(row["Subcategoria"]) else last_sub
        item = str(row["Item"]).strip() if pd.notna(row["Item"]) else None

        if pd.notna(row["Categoria"]):
            last_cat = cat
        if pd.notna(row["Subcategoria"]):
            last_sub = sub

        parts = [p for p in [cat, sub, item] if p]
        path_completo = ".".join(parts)
        path_norm = normalize_text(path_completo)
        catalog[path_norm] = (int(row["TiempoMin"]), int(row["TiempoMax"]))

    return catalog


def load_cases(path: str, responsable: str) -> list:
    """Lee casos del Excel, filtra por responsable."""
    df = pd.read_excel(path, sheet_name="ASDK_Full_Casos", header=None, skiprows=3)
    headers = df.iloc[0].tolist()
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = headers

    df = df[df["Responsable"].str.strip() == responsable]
    df = df[df["Tipo Caso"].isin(["INCIDENTES", "REQUERIMIENTOS"])]

    cases = []
    for _, row in df.iterrows():
        tipo = "Incidente" if row["Tipo Caso"] == "INCIDENTES" else "Requerimiento"
        cases.append({
            "case_code": str(row["Cod Caso"]),
            "case_type": tipo,
            "category_raw": str(row["Categoria"]).strip(),
            "description": str(row.get("Descripci\u00f3n", "")).strip(),
            "solution": str(row.get("Solucion", "")).strip(),
        })

    return cases


def generate_description(case: dict, catalog: dict) -> dict:
    """Genera descripción con IA para un caso."""
    cat_norm = normalize_text(case["category_raw"])
    time_range = catalog.get(cat_norm)

    if not time_range:
        return {"status": "rejected", "reason": "No está en catálogo"}

    estimated_minutes = (time_range[0] + time_range[1]) // 2

    prompt = f"""Eres un técnico de soporte TI. Genera una descripción breve y formal de lo realizado para resolver el caso.

Responde SOLO en este formato JSON:
{{"description": "Se realizó [acción breve en pasado]" }}

Caso:
- Tipo: {case['case_type']}
- Categoría: {case['category_raw']}
- Descripción original: {case['description']}
- Solución: {case['solution']}

Descripción:"""

    try:
        start = time.time()
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 100},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.time() - start) * 1000

            ai_content = data.get("response", "")
            tokens = data.get("eval_count", 0)

            if ai_content:
                try:
                    parsed = json.loads(ai_content)
                    desc = parsed.get("description", ai_content)
                except json.JSONDecodeError:
                    desc = ai_content
            else:
                desc = "Sin descripción generada"

            return {
                "status": "processed",
                "generated_description": desc,
                "time_range": f"{time_range[0]}-{time_range[1]} min",
                "estimated_minutes": estimated_minutes,
                "latency_ms": round(latency_ms),
                "tokens": tokens,
            }

    except Exception as e:
        return {"status": "error", "reason": str(e)}


def main():
    print("=" * 70)
    print(f"TEST DE PROCESAMIENTO IA SIN BASE DE DATOS")
    print(f"Modelo: {MODEL} | Responsable: {RESPONSABLE}")
    print("=" * 70)

    print("\n1. Cargando catálogo de tiempos...")
    catalog = load_catalog(CATALOG_PATH)
    print(f"   {len(catalog)} categorías cargadas")

    print("\n2. Cargando casos del Excel...")
    cases = load_cases(EXCEL_PATH, RESPONSABLE)
    print(f"   {len(cases)} casos encontrados para '{RESPONSABLE}'")

    # Filtrar solo los que están en catálogo
    processable = []
    rejected = []
    for c in cases:
        cat_norm = normalize_text(c["category_raw"])
        if cat_norm in catalog:
            processable.append(c)
        else:
            rejected.append(c)

    print(f"\n3. Filtrado:")
    print(f"   {len(processable)} casos en catálogo (se procesarán)")
    print(f"   {len(rejected)} casos NO en catálogo (se omiten)")

    if rejected:
        print(f"\n   Casos omitidos:")
        for r in rejected[:10]:
            print(f"     - {r['case_code']}: {r['category_raw']}")
        if len(rejected) > 10:
            print(f"     ... y {len(rejected) - 10} más")

    print(f"\n4. Procesando {len(processable)} casos con IA...")
    print("-" * 70)

    results = {"processed": 0, "rejected": 0, "errors": 0}
    all_results = []

    for i, case in enumerate(processable, 1):
        print(f"\n  [{i}/{len(processable)}] Caso {case['case_code']} ({case['case_type']})")
        print(f"    Categoría: {case['category_raw']}")

        result = generate_description(case, catalog)
        result["case_code"] = case["case_code"]
        result["case_type"] = case["case_type"]
        result["category"] = case["category_raw"]
        result["original_description"] = case["description"]
        result["solution"] = case["solution"]
        all_results.append(result)

        if result["status"] == "processed":
            results["processed"] += 1
            print(f"    Descripción: {result['generated_description']}")
            print(f"    Tiempo: {result['time_range']} ({result['estimated_minutes']} min promedio)")
            print(f"    Tokens: {result['tokens']} | Latencia: {result['latency_ms']}ms")
        elif result["status"] == "rejected":
            results["rejected"] += 1
            print(f"    Omitido: {result['reason']}")
        else:
            results["errors"] += 1
            print(f"    Error: {result['reason']}")

    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"  Procesados:  {results['processed']}")
    print(f"  Rechazados:  {results['rejected']}")
    print(f"  Errores:     {results['errors']}")
    print(f"  Total:       {len(processable)}")

    # Guardar resultados en JSON
    output_path = r"C:\BOT-Comproject\test_data\test_ai_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n  Resultados guardados en: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
