"""Test directo a Ollama sin base de datos."""
import httpx
import json

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:3b"

cases = [
    {
        "case_code": "001",
        "case_type": "Incidente",
        "final_category": "servidores/bsc/so",
        "description": "El servidor presenta lentitud en la respuesta de los usuarios, el servicio de BSC no responde adecuadamente.",
        "solution": "Se reinició el servicio BSC y se liberó memoria RAM. Se verificó que el servicio quedara operativo.",
    },
    {
        "case_code": "002",
        "case_type": "Incidente",
        "final_category": "servidores/windows/active_directory",
        "description": "No es posible autenticar usuarios en el dominio, los usuarios reportan que no pueden acceder a los recursos compartidos.",
        "solution": "Se verificó el servicio de AD y se reinició el DC. Los usuarios pudieron autenticarse nuevamente.",
    },
    {
        "case_code": "003",
        "case_type": "Requerimiento",
        "final_category": "cableado/estructurado",
        "description": "Se solicita tendido de cableado de red para nuevo puesto de trabajo en el tercer piso.",
        "solution": "Se realizó el tendido de cableado UTP Cat6 y se certificaron los puntos.",
    },
]

prompt_template = """Eres un técnico de soporte TI. Genera una descripción breve y formal de lo realizado para resolver el caso.

Responde SOLO en este formato JSON:
{{"description": "Se realizó [acción breve en pasado]" }}

Caso:
- Tipo: {case_type}
- Categoría: {category}
- Descripción original: {description}
- Solución: {solution}

Descripción:"""

print("=" * 60)
print(f"Probando Ollama con modelo: {MODEL}")
print("=" * 60)

for case in cases:
    prompt = prompt_template.format(
        case_type=case["case_type"],
        category=case["final_category"],
        description=case["description"],
        solution=case["solution"],
    )

    print(f"\nCaso {case['case_code']} ({case['case_type']})")
    print(f"Prompt enviado:")
    print(prompt)
    print("-" * 40)

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 100},
                },
            )
            response.raise_for_status()
            data = response.json()
            ai_content = data.get("response", "")
            eval_count = data.get("eval_count", 0)
            eval_duration_ns = data.get("eval_duration", 0)
            eval_duration_ms = eval_duration_ns / 1_000_000

            print(f"Respuesta IA: {ai_content}")
            print(f"Tokens: {eval_count} | Tiempo: {eval_duration_ms:.0f}ms")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("Test completado")
print("=" * 60)
