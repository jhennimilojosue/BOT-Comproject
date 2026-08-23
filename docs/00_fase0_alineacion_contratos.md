# 📋 FASE 0: ALINEAMIENTO DE CONTRATOS
## BOT-COMProject | Documento de Decisión para 3 Desarrolladores

**Fecha:** 20 de agosto de 2026
**Duración estimada:** 2 días
**Participantes:** Developer 1 (Fundación), Developer 2 (Pipeline), Developer 3 (Inteligencia)

---

## 🎯 OBJETIVO DE LA FASE 0

**Antes de escribir UNA SOLA LÍNEA DE CÓDIGO**, los 3 desarrolladores deben:

1. ✅ Revisar y entender la documentación clave
2. ✅ Acordar interfaces y contratos
3. ✅ Definir estructura del proyecto
4. ✅ Configurar herramientas de desarrollo
5. ✅ Establecer reglas de trabajo

---

## 📚 DOCUMENTACIÓN OBLIGATORIA (Día 1 - Mañana)

### Lectura Requerida (2 horas)

| # | Documento | Ubicación | Propósito |
|---|-----------|-----------|-----------|
| 1 | Project Charter | `docs/01_contexto/01_project_charter.md` | Alcance, objetivos, reglas de negocio |
| 2 | Case Contract | `docs/06_contratos/case_contract.md` | Estructura del caso (CAMPO POR CAMPO) |
| 3 | API Contract | `docs/08_api/contratos_api.md` | 8 endpoints, requests, responses |
| 4 | Catálogo de Estados | `docs/05_catalogos/catalogo_estados.md` | Estados procesables |
| 5 | Catálogo de Tiempos | `docs/05_catalogos/catalogo_tiempos.md` | Rangos de tiempo |
| 6 | Catálogo de Responsables | `docs/05_catalogos/catalogo_responsables.md` | 5 responsables V1 |

### Preguntas Clave para Responder (Grupo)

| # | Pregunta | Fuente | Decisión Necesaria |
|---|----------|--------|-------------------|
| 1 | ¿Campos `description` y `solution` son obligatorios? | Case Contract | Confirmar que SÍ |
| 2 | ¿`registered_at` almacena solo fecha o DateTime? | Case Contract | Confirmar: solo fecha YYYY-MM-DD |
| 3 | ¿Cuáles son los estados procesables? | Catálogo Estados | Confirmar: Solucionado, Cerrado |
| 4 | ¿Cuántos responsables hay en V1? | Catálogo Responsables | Confirmar: 5 |
| 5 | ¿El procesamiento es síncrono? | API Contract | Confirmar: sí, timeout 5 min |

---

## 🔧 DECISIONES TÉCNICAS (Día 1 - Tarde)

### Decisión 1: Estructura del Proyecto

**Pregunta:** ¿Usamos Clean Architecture o una estructura más simple?

**Opción A (Recomendada):** Clean Architecture simplificada
```
backend/
├── app/
│   ├── domain/          (entidades, interfaces)
│   ├── application/     (use cases, services)
│   ├── infrastructure/  (database, excel, ai, catalogs)
│   └── presentation/    (api, schemas)
```

**Opción B:** Estructura por módulos
```
backend/
├── modules/
│   ├── cases/
│   ├── estimation/
│   ├── catalogs/
│   └── api/
```

**Decisión:** _________________

---

### Decisión 2: Herramientas de Desarrollo

| Herramienta | Opción A | Opción B | Decisión |
|-------------|----------|----------|----------|
| Python Version | 3.11 | 3.12 | _____ |
| FastAPI Version | Última estable | Última | _____ |
| SQLAlchemy | 1.4 (legacy) | 2.0 (nuevo) | _____ |
| Migrations | Alembic | Django-style | _____ |
| Testing | pytest | unittest | _____ |
| Frontend | React + Vite | React + CRA | _____ |

---

### Decisión 3: Control de Versiones

| Aspecto | Opción A | Opción B | Decisión |
|---------|----------|----------|----------|
| Branching | Git Flow | GitHub Flow | _____ |
| PR Reviews | 1 approval | 2 approvals | _____ |
| Squash commits | Sí | No | _____ |
| Conventional commits | Sí | No | _____ |

---

### Decisión 4: Infraestructura Local

| Componente | Opción A | Opción B | Decisión |
|------------|----------|----------|----------|
| PostgreSQL | Docker | Local install | _____ |
| Ollama | Local | Docker | _____ |
| Redis (si aplica) | Docker | No usar | _____ |

---

## 🤝 INTERFACES A ACORDAR (Día 2 - Mañana)

### Interface 1: Catalog Service

```python
# TODO los devs deben acordar esta interfaz
class CatalogService(ABC):
    
    @abstractmethod
    def is_processable_status(self, status: str) -> bool:
        """Verifica si un estado permite procesamiento"""
        pass
    
    @abstractmethod
    def is_category_configured(self, category: str) -> bool:
        """Verifica si una categoría tiene configuración de tiempo"""
        pass
    
    @abstractmethod
    def get_time_range(self, category: str) -> Optional[TimeRange]:
        """Obtiene el rango min/max para una categoría"""
        pass
    
    @abstractmethod
    def get_active_responsibles(self) -> List[Responsible]:
        """Retorna responsables activos"""
        pass
    
    @abstractmethod
    def is_valid_responsible(self, responsible_id: UUID) -> bool:
        """Verifica si un responsable es válido y activo"""
        pass
```

**Preguntas para acordar:**
1. ¿Los métodos deben lanzar excepciones o retornar Optional?
2. ¿Los nombres de parámetros son correctos?
3. ¿Falta algún método?

---

### Interface 2: Repository Interfaces

```python
class CaseRepository(ABC):
    
    @abstractmethod
    def save(self, case: Case) -> None:
        pass
    
    @abstractmethod
    def save_batch(self, cases: List[Case]) -> None:
        pass
    
    @abstractmethod
    def find_by_upload(self, upload_id: UUID) -> List[Case]:
        pass
    
    @abstractmethod
    def find_by_code_and_upload(self, code: str, upload_id: UUID) -> Optional[Case]:
        pass
    
    @abstractmethod
    def exists_by_code_and_upload(self, code: str, upload_id: UUID) -> bool:
        pass


class ProcessingRepository(ABC):
    
    @abstractmethod
    def save(self, processing: Processing) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, processing_id: UUID) -> Optional[Processing]:
        pass
    
    @abstractmethod
    def update_status(self, processing_id: UUID, status: str) -> None:
        pass


class ProcessingRejectionRepository(ABC):
    
    @abstractmethod
    def save(self, rejection: ProcessingRejection) -> None:
        pass
    
    @abstractmethod
    def save_batch(self, rejections: List[ProcessingRejection]) -> None:
        pass
    
    @abstractmethod
    def find_by_processing(self, processing_id: UUID) -> List[ProcessingRejection]:
        pass
```

**Preguntas para acordar:**
1. ¿Usamos `save_batch` o solo `save` en loop?
2. ¿Los repos deben retornar List o Iterator?
3. ¿Falta algún método de consulta?

---

### Interface 3: AI Provider

```python
class AIProvider(ABC):
    
    @abstractmethod
    def generate(self, prompt: str, config: AIConfig) -> AIResponse:
        """Genera una respuesta usando el modelo de IA"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verifica que el servicio de IA esté disponible"""
        pass


@dataclass
class AIConfig:
    model: str = "qwen2.5:latest"
    temperature: float = 0.3
    timeout: int = 60
    max_tokens: int = 500


@dataclass
class AIResponse:
    content: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
```

**Preguntas para acordar:**
1. ¿AIConfig debe ser dataclass o Pydantic model?
2. ¿AIResponse debe incluir tokens_used?
3. ¿El timeout va en AIConfig o en el método?

---

### Interface 4: DTOs Inter-módulo

```python
# DTO que Excel Service envía a Gestión de Casos
@dataclass
class ExcelCaseDTO:
    case_code: str
    responsible_name: str
    user_name: Optional[str]
    project: str
    registered_at: str  # YYYY-MM-DD
    status: str
    final_category: str
    description: str
    solution: str


# DTO que Gestión de Casos envía a Estimation Engine
@dataclass
class ProcessableCaseDTO:
    id: UUID
    case_code: str
    responsible_name: str
    project: str
    registered_at: str
    status: str
    final_category: str
    description: str
    solution: str


# DTO que Estimation Engine retorna
@dataclass
class EstimationResultDTO:
    case_id: UUID
    estimated_minutes: int
    minimum_minutes: int
    maximum_minutes: int
    generated_description: str
    status: str  # "VALID" o "REJECTED"
    rejection_reason: Optional[str] = None
```

**Preguntas para acordar:**
1. ¿Los DTOs deben ser dataclass o Pydantic models?
2. ¿Los campos Optional deben tener default None?
3. ¿Falta algún campo en algún DTO?

---

## 🗂️ ESTRUCTURA DEL PROYECTO (Día 2 - Tarde)

### Árbol de Archivos Inicial

```
BOT-COMProject/
├── .gitignore
├── README.md
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── domain/
│   │   │   └── __init__.py
│   │   ├── application/
│   │   │   └── __init__.py
│   │   ├── infrastructure/
│   │   │   └── __init__.py
│   │   └── presentation/
│   │       └── __init__.py
│   └── tests/
│       ├── __init__.py
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── frontend/
│   ├── package.json
│   └── src/
├── catalog_service/
│   ├── catalogo_estados.xlsx
│   ├── catalogo_responsables.xlsx
│   └── catalogo_tiempos.xlsx
└── docs/
```

**Nota:** Solo crear carpetas vacías inicialmente. Los archivos se crean cuando se usen.

---

## 📋 CHECKLIST DE DECISIONES

### Día 1 - Mañana (Lectura)

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Todos leen Project Charter | ☐ |
| 2 | Todos leen Case Contract | ☐ |
| 3 | Todos leen API Contract | ☐ |
| 4 | Todos leen Catálogo de Estados | ☐ |
| 5 | Todos leen Catálogo de Tiempos | ☐ |
| 6 | Todos leen Catálogo de Responsables | ☐ |
| 7 | Responder preguntas clave | ☐ |

### Día 1 - Tarde (Decisiones Técnicas)

| # | Decisión | Responsable | Estado |
|---|----------|-------------|--------|
| 1 | Estructura del proyecto | Todos | ☐ |
| 2 | Python version | Dev 1 | ☐ |
| 3 | SQLAlchemy version | Dev 1 | ☐ |
| 4 | Branching strategy | Dev 3 | ☐ |
| 5 | Infraestructura local | Dev 1 | ☐ |

### Día 2 - Mañana (Interfaces)

| # | Interface | Dev Principal | Estado |
|---|-----------|---------------|--------|
| 1 | Catalog Service | Dev 1 | ☐ |
| 2 | Repository Interfaces | Dev 1 | ☐ |
| 3 | AI Provider | Dev 3 | ☐ |
| 4 | DTOs Inter-módulo | Todos | ☐ |

### Día 2 - Tarde (Configuración)

| # | Tarea | Responsable | Estado |
|---|-------|-------------|--------|
| 1 | Crear repositorio en GitHub | Dev 3 | ☐ |
| 2 | Configurar branches | Dev 3 | ☐ |
| 3 | Crear .gitignore | Dev 1 | ☐ |
| 4 | Crear requirements.txt básico | Dev 1 | ☐ |
| 5 | Crear docker-compose.yml | Dev 1 | ☐ |
| 6 | Crear .env.example | Dev 1 | ☐ |
| 7 | Crear estructura de carpetas vacías | Dev 1 | ☐ |
| 8 | Verificar que Ollama funciona | Dev 3 | ☐ |
| 9 | Verificar que PostgreSQL funciona | Dev 1 | ☐ |

---

## 🚨 REGLAS DE TRABAJO

### Acuerdos Obligatorios

| # | Regla | Descripción |
|---|-------|-------------|
| 1 | **Interfaces after Day 2** | Las interfaces NO cambian después del Día 2 sin acuerdo de los 3 |
| 2 | **PR antes de merge** | Todo código pasa por PR con al menos 1 review |
| 3 | **Tests pasan** | CI debe estar verde antes de merge |
| 4 | **Checkpoints viernes** | Todos asisten a la reunión semanal |
| 5 | **Comunicación** | Si hay bloqueo, avisar inmediatamente en canal compartido |

### Branches

```
main (producción)
└── develop (integración)
    ├── feature/dev1-domain-entities
    ├── feature/dev1-database
    ├── feature/dev1-catalog-service
    ├── feature/dev2-excel-service
    ├── feature/dev2-case-management
    ├── feature/dev3-ai-service
    ├── feature/dev3-estimation-engine
    └── feature/dev3-api
```

### Naming Convention

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Branch feature | `feature/devN-descripcion` | `feature/dev1-domain-entities` |
| Branch bugfix | `bugfix/descripcion` | `bugfix/case-validation-error` |
| Commit | `tipo: descripcion` | `feat: add Case entity` |
| PR | `descripcion` | `Add Case entity and value objects` |

---

## ✅ ENTREGABLES DE LA FASE 0

Al final del Día 2, los 3 desarrolladores deben tener:

| # | Entregable | Responsable | Verificación |
|---|------------|-------------|--------------|
| 1 | Interfaces acordadas | Todos | Documento firmado |
| 2 | Estructura del proyecto definida | Dev 1 | Árbol de archivos |
| 3 | Repositorio creado | Dev 3 | Accesible por los 3 |
| 4 | Branches configurados | Dev 3 | Cada dev tiene su branch |
| 5 | docker-compose.yml | Dev 1 | PostgreSQL funciona |
| 6 | Ollama funcionando | Dev 3 | Modelo qwen2.5:latest descargado |
| 7 | requirements.txt básico | Dev 1 | Pip install funciona |
| 8 | .env.example | Dev 1 | Variables documentadas |

---

## 👥 DISTRIBUCIÓN DE TRABAJO (Fase 1 en adelante)

### Developer 1: "Fundación & Datos"
**Responsable:** Entidades, Base de Datos, Catálogos, Repositorios

| Fase | Tareas |
|------|--------|
| Fase 1 | Domain entities, Database models, Catalog Service, Repositories |
| Fase 2 | Repository implementations, Integration tests |
| Fase 3 | DB optimization, Support |

### Developer 2: "Pipeline de Entrada"
**Responsable:** Archivos, Excel Service, Gestión de Casos

| Fase | Tareas |
|------|--------|
| Fase 1 | File management, Excel Service (7 componentes) |
| Fase 2 | Gestión de Casos (4 componentes), Business rules |
| Fase 3 | Integration tests, Edge cases |

### Developer 3: "Inteligencia & Integración"
**Responsable:** IA, Estimación, Application Layer, API

| Fase | Tareas |
|------|--------|
| Fase 1 | AI Service, Ollama client |
| Fase 2 | Estimation Engine, ProcessCases use case |
| Fase 3 | API endpoints, Schemas, E2E tests |

---

## 📅 TIMELINE

```
Semana 1    Semana 2    Semana 3    Semana 4
    │           │           │           │
    ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│FASE 0-1 │ │FASE 2   │ │FASE 3   │ │FASE 4   │
│Fundación│ │Lógica   │ │API      │ │Frontend │
│+ Alim.  │ │Negocio  │ │+ Integr.│ │+ Export │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

---

## 📞 CANAL DE COMUNICACIÓN

| Herramienta | Uso |
|-------------|-----|
| **Slack/Discord** | Comunicación diaria, preguntas rápidas |
| **GitHub Issues** | Bugs, tareas, documentación |
| **GitHub Projects** | Seguimiento de progreso |
| **Reunión viernes** | Checkpoint semanal |

---

## 📝 REGISTRO DE DECISIONES

| # | Decisión | Fecha | Participantes |
|---|----------|-------|---------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## ✍️ FIRMAS DE ACUERDO

Al firmar este documento, los participantes confirman que han leído, entendido y aceptan las decisiones tomadas en la Fase 0.

| Nombre | Rol | Firma | Fecha |
|--------|-----|-------|-------|
| | Developer 1 (Fundación) | | |
| | Developer 2 (Pipeline) | | |
| | Developer 3 (Inteligencia) | | |
