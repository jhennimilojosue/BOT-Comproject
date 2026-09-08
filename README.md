# BOT-COMProject

Sistema de automatización para el procesamiento de casos provenientes del Maestro de Casos de Aranda y la generación de descripciones y estimaciones de tiempo para su posterior registro en COMProject.

---

## 1. Descripción del proyecto

BOT-COMProject automatiza la preparación semanal de horas de trabajo para COMProject:

1. **Carga del Maestro de Casos**: se sube el archivo Excel exportado de Aranda.
2. **Procesamiento**: los casos se filtran, normalizan y se clasifican contra los catálogos definidos por el negocio.
3. **Generación de descripciones con IA**: cada caso procesable recibe una descripción profesional generada por IA (inicia con "Se realizó").
4. **Estimación de tiempo**: el tiempo se obtiene del catálogo de tiempos (`catalogo_tiempos`, ver `test_data/catalogo_tiempos.xlsx`), no del modelo de IA.
5. **Exportación**: los resultados (descripción IA + tiempo estimado) se exportan a Excel para registrar en COMProject.

El sistema mantiene trazabilidad completa:

```text
Archivo cargado
      ↓
Ejecución
      ↓
Caso original
      ↓
Procesamiento
      ↓
Estimación / Rechazo
```

---

## 2. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Python 3.11+ |
| Base de datos | PostgreSQL 18 + SQLAlchemy 2.0 + Alembic |
| Inteligencia Artificial | Ollama (`qwen2.5-coder:3b`) |
| Procesamiento Excel | openpyxl / pandas |
| Pruebas | pytest |
| Arquitectura | Clean Architecture (domain, application, infrastructure, presentation) |

---

## 3. Estructura del repositorio

```text
Bot-Comproject/
├── backend/              # API FastAPI y toda la lógica
│   ├── app/
│   │   ├── api/          # Routers, schemas, dependencias, WebSocket
│   │   ├── application/  # Casos de uso, DTOs, servicios de aplicación
│   │   ├── domain/       # Entidades, value objects, interfaces
│   │   └── infrastructure/ # BD, Excel, IA (Ollama), catálogos, config
│   ├── alembic/          # Migraciones de base de datos
│   ├── scripts/          # Utilidades (carga de catálogo, pruebas de IA)
│   └── tests/            # Pruebas unitarias e integración
├── catalog_service/      # Carpetas de carga de catálogos
├── docs/                 # Documentación del proyecto
├── test_data/            # Datos de prueba (maestro de casos, catálogos)
└── docker-compose.yml    # PostgreSQL
```

---

## 4. Funcionalidad por módulo

### Backend (Parte 1 — Lógica de programa)
- PostgreSQL, Alembic y modelo de datos (uploads, cases, processings, processings_rejections, estimations, ai_results, catalogo_tiempos).
- `ProcessCasesUseCase`: filtrado de casos según catálogos de estados, responsables y tiempos.
- Carga de casos desde Excel (Maestro de Casos de Aranda). **Cada upload genera su propio `processing_id`** (un processing por archivo).
- Resultados, rechazos y exportación a Excel.

### Backend (Parte 2 — IA)
- Generación de descripciones profesionales con Ollama (`qwen2.5-coder:3b`).
- Estimación de tiempo a partir del catálogo de tiempos (almacenado en PostgreSQL).
- Procesamiento por responsable (endpoint batch): usa el `processing_id` del archivo y **acumula** los resultados de todos los responsables bajo ese mismo processing.
- Catálogo de tiempos persistido en PostgreSQL (tabla `catalogo_tiempos`, 48 categorías).
- WebSocket para progreso en tiempo real.

### Flujo
1. `POST /api/v1/uploads` con el **Maestro de Casos** del usuario → devuelve `upload_id` + `processing_id` (status `pending`, `total_cases`).
2. `POST /api/v1/ai/process-responsible` con `upload_id` + `responsible_name` → procesa **solo los casos de ese responsable** y guarda bajo el `processing_id` del archivo.
3. Consultas: `GET /api/v1/processing/{processing_id}`, `GET /api/v1/ai/results/{processing_id}`, `GET /api/v1/processing/{processing_id}/export`.

---

## 5. Configuración

Copie `.env.example` a `.env` en `backend/`:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/botcomproject

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
OLLAMA_TIMEOUT=60

# Application Configuration
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# File Upload Configuration
MAX_FILE_SIZE_MB=50
```

---

## 6. Puesta en marcha

### Base de datos

```bash
docker compose up -d            # o usar una instancia local de PostgreSQL
```

Ejecutar migraciones desde `backend/`:

```bash
cd backend
python -m alembic upgrade head
```

Cargar el catálogo de tiempos (requiere `backend/.env` configurado):

```bash
python backend/scripts/load_catalog.py
```

### Servidor

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Swagger UI disponible en `http://localhost:8002/docs`.

### Requisito

Ollama debe estar corriendo con el modelo `qwen2.5-coder:3b` descargado:

```bash
ollama pull qwen2.5-coder:3b
```

---

## 7. Endpoints principales

| Método | Endpoint | Propósito |
|--------|----------|-----------|
| `GET` | `/health` | Estado general del sistema |
| `GET` | `/api/v1/uploads` | Lista de cargas de archivos |
| `POST` | `/api/v1/uploads` | Carga un Maestro de Casos (xlsx); genera `upload_id` + `processing_id` del archivo |
| `POST` | `/api/v1/cases/process` | Procesamiento por reglas de negocio (delegado) |
| `GET` | `/api/v1/cases/responsible` | Responsables con conteo de casos |
| `GET` | `/api/v1/cases/responsible/{name}` | Casos de un responsable |
| `GET` | `/api/v1/processing/{id}` | Resultados de un procesamiento |
| `GET` | `/api/v1/processing/{id}/rejected` | Casos rechazados |
| `GET` | `/api/v1/processing/{id}/export` | Exporta resultados a Excel (incluye Descripción IA y Tiempo Estimado) |
| `POST` | `/api/v1/ai/process-responsible` | Procesa todos los casos en catálogo de un responsable (batch, guarda en BD) |
| `POST` | `/api/v1/ai/generate-description` | Genera una descripción con IA (caso individual) |
| `POST` | `/api/v1/ai/estimate-time` | Estima tiempo con IA (caso individual) |
| `GET` | `/api/v1/ai/catalog` | Devuelve el catálogo de tiempos |
| `POST` | `/api/v1/ai/catalog/load` | Carga el catálogo desde Excel |
| `GET` | `/api/v1/ai/results/{processing_id}` | Resultados IA guardados (con resumen por tipo/categoría) |
| `GET` | `/api/v1/ai/health` | Estado del servicio de IA |
| `POST` | `/api/v1/ai/test-process` | Prueba de procesamiento IA (sin guardar en BD) |
| `WS` | `/api/v1/ai/ws/{client_id}` | Progreso en tiempo real |

---

## 8. Documentación

La documentación del proyecto está en [docs/](docs/):

- `docs/00_changelog.md` — registro de correcciones documentales
- `docs/01_contexto/` — proyecto, glosario, arquitectura de módulos
- `docs/02_arquitectura/` — mapa de módulos y arquitectura del sistema
- `docs/03_desarrollo/` — estructura y convenciones
- `docs/04_modulos/` — módulos: procesamiento maestro, estimación, gestión de casos, IA
- `docs/05_catalogos/` — catálogos de estados, responsables y tiempos
- `docs/06_contratos/` — contrato de datos del caso
- `docs/08_api/` — contrato de la API
- `docs/09_agente/` — prompts del agente y reglas de opencode

---