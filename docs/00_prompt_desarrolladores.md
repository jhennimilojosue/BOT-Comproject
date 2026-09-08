# 🤖 BOT-COMProject - Punto de Entrada del Desarrollador

---

## ⚠️ INSTRUCCIÓN IMPORTANTE

**Debes abrir una conversación con la IA desde la raíz del proyecto:**

```
C:\Bot-Comproject\
```

La IA solo podrá leer la documentación si trabajas desde aquí. Toda la información está en la carpeta `docs/`.

---

## 📋 CÓMO USAR ESTE DOCUMENTO

1. Abre una conversación nueva con la IA **desde la raíz del proyecto**
2. Copia el **PROMPT** correspondiente a tu rol
3. Pégalo en la conversación
4. La IA te dará instrucciones personalizadas
5. Pide ayuda con cada tarea específica

---

# 🎯 PROMPT MAESTRO (Copiar esto para empezar)

```
Bienvenido al equipo de desarrollo de BOT-COMProject. Soy tu asistente de desarrollo y voy a ayudarte a completar las tareas que corresponden a tu rol en el proyecto.

IMPORTANTE: Estamos trabajando dentro del repositorio del proyecto en C:\Bot-Comproject\. Toda la documentación oficial está en la carpeta docs/. Antes de implementar cualquier cosa, debo consultar los documentos relevantes de esa carpeta. NO debo inventar información: si algo no está definido en la documentación, debo preguntar antes de proceder. Debo seguir las reglas de comportamiento definidas en docs/09_agente/opencode.md.

## Identifica mi Rol

Soy Developer [1 / 2 / 3]. Por favor, dame las instrucciones personalizadas para mi rol.

## Contexto del Proyecto

BOT-COMProject automatiza el procesamiento semanal de casos de Aranda para generar:
- Estimaciones de tiempo estándar
- Descripciones profesionales de actividades

Stack tecnológico:
- Backend: FastAPI + Python 3.11
- Database: PostgreSQL + SQLAlchemy 2.0 + Alembic
- AI: Ollama (qwen2.5-coder:3b)
- Frontend: React + Vite
- Testing: pytest
- Arquitectura: Clean Architecture (domain, application, infrastructure, presentation)

Decisiones del equipo (Fase 0):
- Catalog Service lanza excepciones (no retorna None)
- Repositories usan save_batch y retornan List
- AIConfig/AIResponse y DTOs son Pydantic models (no dataclass)
- Campos Optional con default None
- Git Flow, 1 PR approval, squash commits, conventional commits
- PostgreSQL en Docker, Ollama local, sin Redis

Repositorio: La documentación completa está en la carpeta docs/.
```

---

# 👤 DEVELOPER 1 - Fundación & Datos

```
Soy Developer 1 - Fundación & Datos. Mi rol es la base del proyecto: sin mi código, ningún otro desarrollador puede trabajar.

## Mis Módulos
1. Domain Entities - Case, Upload, Processing, ProcessingRejection, Estimation, AIResult
2. Database - SQLAlchemy models, Alembic migrations
3. Catalog Service - Loaders para 3 catálogos Excel
4. Repositories - Implementaciones para cada entidad

## Mis Dependencias
- Ninguna - Puedo empezar inmediatamente
- Los otros devs dependen de MÍ - Debo entregar interfaces antes del Día 4

## Mis Fases
| Fase | Días | Tareas |
|------|------|--------|
| Fase 1 | 3-8 | Domain entities, Database, Catalog Service |
| Fase 2 | 9-14 | Repositories, Integration tests |
| Fase 3 | 15-18 | DB optimization, Support |

## Primera tarea (Día 3)
Crear la entidad Case en backend/app/domain/entities/case.py según el Case Contract.

**Campos del Case Contract:**
- id: UUID (obligatorio, sistema)
- upload_id: UUID (obligatorio, sistema)
- case_code: String(50) (obligatorio, Excel)
- responsible_name: String(200) (obligatorio, Excel)
- responsible_id: UUID (opcional, sistema)
- user_name: String(200) (opcional, Excel)
- project: String(200) (obligatorio, Excel)
- registered_at: DateTime (obligatorio, Excel, formato YYYY-MM-DD)
- status: String(100) (obligatorio, Excel)
- final_category: String(200) (obligatorio, Excel)
- description: Text (obligatorio, Excel)
- solution: Text (obligatorio, Excel)
- created_at: DateTime (obligatorio, sistema)

**Comando rápido:**
"Crea la entidad Case para BOT-COMProject con SQLAlchemy 2.0, incluyendo value objects y validaciones según el Case Contract."

## Documentación Relevante
- docs/06_contratos/case_contract.md
- docs/04_modulos/gestion_casos/modelo_datos_modulo.md
- docs/05_catalogos/*.md

## Reglas Importantes
1. Debo entregar interfaces antes del Día 4
2. Usar Pydantic para modelos (no dataclass)
3. Los Optional deben tener default None
4. Catalog Service debe lanzar excepciones
5. Repositories deben usar save_batch

Por favor, dame las instrucciones para mi rol y la primera tarea a realizar.
```

---

# 👤 DEVELOPER 2 - Pipeline de Entrada

```
Soy Developer 2 - Pipeline de Entrada. Mi rol es procesar datos: tomo el archivo Excel crudo de Aranda, lo valido, normalizo, filtro y preparo para que el Estimation Engine genere estimaciones.

## Mis Módulos
1. File Management - Validación de archivos
2. Excel Service - 7 componentes para procesar .xlsx
3. Case Management - 4 componentes para gestionar casos

## Mis Dependencias
- Necesito las interfaces de Dev 1 (Día 4)
- Necesito los catálogos de Dev 1 (Día 7)
- Dev 3 consume mi output (ProcessableCaseDTO)

## Mis Fases
| Fase | Días | Tareas |
|------|------|--------|
| Fase 1 | 3-8 | File Management, Excel Service |
| Fase 2 | 9-14 | Case Management, Business rules |
| Fase 3 | 15-18 | Integration tests, Edge cases |

## Primera tarea (Día 3)
Crear el File Validator en backend/app/infrastructure/excel/file_validator.py

**Responsabilidades del File Validator:**
- Validar extensión del archivo (solo .xlsx)
- Validar que el archivo sea legible
- Lanzar FileValidationError si falla

**Comando rápido:**
"Crea el File Validator para BOT-COMProject que valide extensión .xlsx y legibilidad, lanzando FileValidationError si falla."

## Mapeo de Columnas Excel
| Columna Física | Campo Interno | Obligatorio |
|----------------|---------------|-------------|
| Codigo Caso | case_code | Sí |
| Responsible Name | responsible_name | Sí |
| Proyecto | project | Sí |
| Fecha | registered_at | Sí |
| Estado | status | Sí |
| Categoria | final_category | Sí |
| Descripcion | description | Sí |
| Solucion | solution | Sí |
| Usuario | user_name | No |

## Los 7 Componentes del Excel Service
1. FileValidator - Valida extensión y legibilidad
2. StructureValidator - Valida columnas requeridas
3. HeaderResolver - Detecta mapeo de columnas
4. ColumnMapper - Mapea columnas físicas a campos internos
5. DataExtractor - Extrae datos del Excel
6. DataNormalizer - Normaliza texto, fechas, tipos
7. CaseMapper - Convierte a ExcelCaseDTO

## Los 4 Componentes de Case Management
1. Case Normalizer - Normaliza texto, fechas, nombres
2. Case Validator - Valida campos obligatorios
3. Case Filter - Filtra por responsable, valida estado y categoría
4. Case Context Builder - Construye contexto para Estimation Engine

## Documentación Relevante
- docs/04_modulos/procesamiento_maestro/procesamiento_maestro.md
- docs/04_modulos/gestion_casos/gestion_casos.md
- docs/04_modulos/gestion_casos/modelo_datos_modulo.md

## Reglas Importantes
1. Esperar las interfaces de Dev 1 antes de implementar
2. Usar pandas para leer Excel (no openpyxl directamente)
3. Los Optional deben tener default None
4. Validar antes de procesar
5. Generar rechazos claros con reason_code y message

Por favor, dame las instrucciones para mi rol y la primera tarea a realizar.
```

---

# 👤 DEVELOPER 3 - Inteligencia & Integración

```
Soy Developer 3 - Inteligencia & Integración. Mi rol es el cerebro del sistema: integro la inteligencia artificial (Ollama), coordino la estimación de tiempo, orquesto todo el flujo y expongo la API al mundo exterior.

## Mis Módulos
1. AI Service - Integración con Ollama
2. Estimation Engine - Coordinación de estimación
3. Application Layer - ProcessCases use case
4. API Endpoints - 8 endpoints REST

## Mis Dependencias
- Necesito las interfaces de Dev 1 (Día 4)
- Necesito el output de Dev 2 (ProcessableCaseDTO)
- Yo orquesto todo al final

## Mis Fases
| Fase | Días | Tareas |
|------|------|--------|
| Fase 1 | 3-8 | AI Service, Ollama client |
| Fase 2 | 9-14 | Estimation Engine, ProcessCases |
| Fase 3 | 15-18 | API endpoints, Schemas, E2E tests |

## Primera tarea (Día 3)
Crear el AI Provider abstraction en backend/app/infrastructure/ai/ai_provider.py

**Responsabilidades del AI Provider:**
- Interfaz abstracta para generar respuestas
- Método generate(prompt, config) -> AIResponse
- Método health_check() -> bool

**Comando rápido:**
"Crea el AI Provider abstraction para BOT-COMProject con interfaz abstracta, AIConfig (Pydantic) y AIResponse (Pydantic)."

## Configuración de IA (Pydantic)
class AIConfig(BaseModel):
    model: str = "qwen2.5-coder:3b"
    temperature: float = 0.3
    timeout: int = 60
    max_tokens: int = 500

class AIResponse(BaseModel):
    content: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None

## Endpoints de la API (registrados en main.py)
| Método | Endpoint | Propósito |
|--------|----------|-----------|
| GET | /health | Estado general del sistema |
| GET | /api/v1/uploads | Lista de uploads cargados |
| POST | /api/v1/uploads | Carga archivo Excel (Maestro de Casos) |
| POST | /api/v1/cases/process | Procesamiento por reglas de negocio |
| GET | /api/v1/cases/responsible | Responsables con conteo de casos |
| GET | /api/v1/cases/responsible/{name} | Casos de un responsable |
| GET | /api/v1/processing/{id} | Consulta resultados |
| GET | /api/v1/processing/{id}/rejected | Consulta rechazados |
| GET | /api/v1/processing/{id}/export | Exporta a Excel (11 columnas, incluye Descripción IA y Tiempo Estimado) |
| POST | /api/v1/ai/process-responsible | Procesa todos los casos en catálogo de un responsable (batch, guarda en BD) |
| POST | /api/v1/ai/catalog/load | Carga el catálogo de tiempos desde Excel |
| GET | /api/v1/ai/catalog | Devuelve el catálogo de tiempos |
| GET | /api/v1/ai/results/{processing_id} | Resultados IA guardados (resumen por tipo/categoría) |
| POST | /api/v1/ai/generate-description | Genera descripción con IA (caso individual) |
| POST | /api/v1/ai/estimate-time | Estima tiempo con IA (caso individual) |
| GET | /api/v1/ai/health | Estado del servicio de IA |
| POST | /api/v1/ai/test-process | Prueba de procesamiento IA sin guardar en BD |
| WS | /api/v1/ai/ws/{client_id} | Progreso en tiempo real |

> Nota: `routers/responsibles.py` (`GET /api/v1/responsibles`) y `routers/cases.py` (`GET /api/v1/cases`, `GET /api/v1/cases/{id}`) existen como stubs pero NO están registrados en `main.py`.

## El Flujo Principal (ProcessCases)
Upload → Excel Service → Case Management → Estimation Engine → AI Service → Results

## Documentación Relevante
- docs/04_modulos/ia_service/ia_service.md
- docs/04_modulos/estimation_engine/estimation_engine.md
- docs/08_api/contratos_api.md
- docs/06_contratos/case_contract.md

## Reglas Importantes
1. Usar Pydantic para AIConfig y AIResponse (no dataclass)
2. El timeout va en AIConfig (no en el método)
3. El procesamiento es síncrono (timeout 5 minutos)
4. Los Optional deben tener default None
5. Seguir el contrato API exactamente

Por favor, dame las instrucciones para mi rol y la primera tarea a realizar.
```

---

# 📋 COMANDOS RÁPIDOS POR TAREA

## Developer 1 - Comandos

```
Necesito crear la entidad Upload para BOT-COMProject. Campos: id (UUID), file_name (String), status (String, default "UPLOADED"), created_at (DateTime). Ayúdame con SQLAlchemy 2.0 y Pydantic.
```

```
Necesito crear el Catalog Service para BOT-COMProject. Debe cargar 3 archivos Excel y tener métodos: is_processable_status, is_category_configured, get_time_range, get_active_responsibles, is_valid_responsible. Debe lanzar excepciones.
```

```
Necesito crear el Case Repository para BOT-COMProject. Métodos: save, save_batch, find_by_upload, find_by_code_and_upload, exists_by_code_and_upload. Con SQLAlchemy 2.0.
```

## Developer 2 - Comandos

```
Necesito crear el File Validator para BOT-COMProject. Debe validar extensión .xlsx y legibilidad, lanzando FileValidationError si falla.
```

```
Necesito crear el Structure Validator para BOT-COMProject. Debe verificar columnas: Codigo Caso, Responsible Name, Proyecto, Fecha, Estado, Categoria, Descripcion, Solucion. Lanzar StructureValidationError con lista de faltantes.
```

```
Necesito crear el Case Filter para BOT-COMProject. Debe filtrar por responsable, validar estado (Solucionado/Cerrado) contra Catalog Service, validar categoría configurada. Generar rechazos con reason_code y message.
```

## Developer 3 - Comandos

```
Necesito crear el Ollama Client para BOT-COMProject. Conectar con Ollama local, enviar prompts, recibir respuestas JSON. Timeout 60s. Lanzar AIServiceError si falla. Con httpx.
```

```
Necesito crear el Estimation Engine para BOT-COMProject. Obtener rango del Catalog Service, enviar contexto a AI Service, validar que estimated_minutes esté entre min y max. Si es válido -> VALID, si no -> REJECTED con reason ESTIMATION_OUT_OF_RANGE.
```

```
Necesito crear el endpoint POST /api/v1/uploads para BOT-COMProject. Recibir multipart/form-data, validar archivo (max 50MB, solo .xlsx), crear Upload, retornar HTTP 201 con id, file_name, status, created_at.
```

---

# 🔄 FLUJO DE TRABAJO

Para cada tarea:

1. **Identificar** tu tarea según rol y fase
2. **Consultar** documentación relevante en `docs/`
3. **Implementar** con ayuda de la IA
4. **Crear tests** con pytest
5. **Commit** con conventional commits (`feat:`, `fix:`, `docs:`)
6. **PR** hacia `develop` con al menos 1 review

---

# 📅 CHECKPOINTS SEMANALES

| Semana | Día | Tema |
|--------|-----|------|
| 1 | 8 | Domain entities + interfaces listas |
| 2 | 14 | Lógica de negocio completa |
| 3 | 18 | API funcional + tests |
| 4 | 22 | MVP completo |

---

# ⚠️ REGLAS GENERALES

1. **Trabajar desde la raíz del proyecto** (`C:\Bot-Comproject\`)
2. **La documentación manda** - El código debe alinearse con `docs/`
3. **No modificar documentación** sin acuerdo del equipo
4. **No crear archivos** que no se usen de inmediato
5. **Interfaces congeladas** después del Día 2
6. **Si hay bloqueo**, avisar inmediatamente
