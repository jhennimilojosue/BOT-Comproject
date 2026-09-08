**Versión:** 1.0

**Estado:** Definido

**Tipo:** Documento técnico de implementación

---

# 1. Objetivo

Este documento define la estructura física del proyecto **BOT-COMProject** y las convenciones que deberán seguirse durante su desarrollo.

Su objetivo es garantizar que:

- La estructura del código sea consistente.
- Los módulos mantengan sus responsabilidades.
- Los archivos se ubiquen en lugares predecibles.
- Las dependencias respeten la arquitectura definida.
- El código pueda ser mantenido y probado fácilmente.
- OpenCode pueda utilizar una estructura clara como referencia para generar código.

> Este documento define **cómo organizar y nombrar el código**, pero no modifica las reglas de negocio definidas en otros documentos.
> 

---

# 2. Alcance

Las convenciones definidas aplican principalmente al backend de V1.

La estructura contempla:

```
Backend
Frontend
Tests
Configuración
Documentación
Catálogos
```

La integración automática con COMProject no será implementada en V1.

---

# 3. Principios

La estructura deberá respetar:

- Clean Architecture.
- Responsabilidad única.
- Separación de responsabilidades.
- Bajo acoplamiento.
- Alta cohesión.
- Inversión de dependencias.
- Testabilidad.
- Convenciones consistentes.
- Evitar módulos innecesarios.

---

# 4. Estructura General del Proyecto

La estructura inicial será:

```
BOT-COMProject/
│
├── backend/
│
├── frontend/
│
├── catalog_service/
│
├── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

La estructura podrá evolucionar cuando exista una necesidad real.

---

# 5. Estructura del Backend

El backend seguirá la arquitectura:

```
backend/
│
├── app/
│   │
│   ├── api/
│   │
│   ├── application/
│   │
│   ├── domain/
│   │
│   ├── infrastructure/
│   │
│   └── main.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# 6. Capa API

La capa `api` será responsable de exponer la funcionalidad del sistema mediante HTTP.

```
backend/app/api/
│
├── routes/
│
├── schemas/
│
└── dependencies/
```

---

## 6.1 Routes

Contendrá únicamente los endpoints.

Ejemplo:

```
api/
└── routes/
    ├── cases.py
    ├── uploads.py
    └── results.py
```

Los endpoints deberán:

- Recibir solicitudes.
- Validar entrada mediante schemas.
- Invocar casos de uso.
- Transformar respuestas.
- Retornar respuestas HTTP.

No deberán contener lógica de negocio compleja.

---

# 7. Schemas

Los schemas representan los contratos de entrada y salida de la API.

```
api/
└── schemas/
    ├── case.py
    ├── process.py
    └── result.py
```

Se utilizará **Pydantic**.

Ejemplo conceptual:

```
ProcessCasesRequest
ProcessCasesResponse
CaseResponse
ProcessingResultResponse
```

Los schemas de API no deberán utilizarse como entidades de dominio.

---

# 8. Dependencies

Contendrá dependencias necesarias para construir los casos de uso.

Ejemplo:

```
api/
└── dependencies/
    ├── services.py
    └── repositories.py
```

Su responsabilidad será conectar la API con la capa de aplicación.

---

# 9. Capa Application

La capa `application` contiene los casos de uso y la orquestación del sistema.

```
application/
│
├── use_cases/
│
├── services/
│
└── dto/
```

---

# 10. Use Cases

Los casos de uso representan acciones completas del sistema.

Ejemplo:

```
application/
└── use_cases/
    ├── process_cases.py
    ├── upload_cases.py
    └── get_results.py
```

El principal caso de uso de V1 será:

```
ProcessCases
```

Este coordinará el procesamiento completo.

Conceptualmente:

```
ProcessCases
     │
     ├── Case Service
     ├── Catalog Service
     ├── Case Repository
     ├── Estimation Engine
     └── AI Service
```

---

# 11. Application Services

Los servicios de aplicación coordinarán funcionalidades que no correspondan directamente a una entidad.

Ejemplo:

```
application/
└── services/
    ├── case_processing_service.py
    └── result_service.py
```

No deberán convertirse en contenedores de toda la lógica del sistema.

---

# 12. DTO

Los DTO representan información que se transporta entre capas.

```
application/
└── dto/
    ├── case_dto.py
    ├── estimation_dto.py
    └── processing_result_dto.py
```

Los DTO no deberán contener lógica de negocio compleja.

---

# 13. Capa Domain

El dominio representa los conceptos centrales de BOT-COMProject.

```
domain/
│
├── cases/
├── estimation/
├── catalogs/
├── results/
└── common/
```

---

# 14. Domain — Cases

```
domain/
└── cases/
    ├── entities/
    ├── value_objects/
    ├── services/
    ├── repositories/
    └── exceptions/
```

Aquí estarán los conceptos relacionados con los casos.

Ejemplo:

```
Case
CaseStatus
CaseCategory
Responsible
```

---

# 15. Domain — Entities

Las entidades representan objetos con identidad dentro del dominio.

Ejemplo:

```
domain/cases/entities/case.py
```

La entidad `Case` deberá representar la información definida en el **Case Contract**.

No deberá contener:

- Código SQL.
- Consultas PostgreSQL.
- Código de Pandas.
- Llamadas a Ollama.
- Código HTTP.

---

# 16. Domain — Value Objects

Los Value Objects representan conceptos cuyo valor define su identidad.

Ejemplos potenciales:

```
CaseCode
Category
ResponsibleName
TimeRange
EstimatedTime
```

Se crearán únicamente cuando aporten valor real al dominio.

---

# 17. Domain — Services

Los servicios de dominio contendrán lógica de negocio que no pertenezca naturalmente a una entidad.

Ejemplos potenciales:

```
case_filter.py
case_validation.py
```

No deberán contener acceso a infraestructura.

---

# 18. Domain — Repositories

Aquí se definirán las interfaces de los repositorios.

Ejemplo:

```
domain/
└── cases/
    └── repositories/
        └── case_repository.py
```

La interfaz representa el contrato:

```
CaseRepository
```

La implementación concreta estará en Infrastructure.

---

# 19. Domain — Exceptions

Las excepciones de negocio estarán separadas de las excepciones de infraestructura.

Ejemplo:

```
domain/cases/exceptions/
├── invalid_case.py
├── invalid_status.py
└── category_not_configured.py
```

---

# 20. Estimation Domain

Los conceptos relacionados con la estimación estarán separados de la gestión de casos.

```
domain/
└── estimation/
    ├── entities/
    ├── services/
    ├── value_objects/
    └── exceptions/
```

Aquí deberá mantenerse la lógica relacionada con:

- Rango permitido.
- Tiempo estimado.
- Validación del tiempo.

---

# 21. Catalog Domain

Los conceptos relacionados con catálogos estarán organizados en:

```
domain/
└── catalogs/
    ├── entities/
    ├── repositories/
    └── services/
```

Los catálogos definidos para V1 son:

```
Estados
Tiempos
Responsables
```

---

# 22. Results Domain

Los resultados generados por el procesamiento estarán representados en:

```
domain/
└── results/
    ├── entities/
    └── value_objects/
```

El resultado principal será conceptualmente:

```
Case
+
Estimated Time
+
Professional Description
```

---

# 23. Capa Infrastructure

Infrastructure contiene las implementaciones concretas de tecnologías externas.

```
infrastructure/
│
├── database/
├── excel/
├── ai/
├── catalogs/
└── repositories/
```

---

# 24. Database

```
infrastructure/
└── database/
    ├── connection.py
    ├── models/
    └── migrations/
```

Aquí se manejará:

- PostgreSQL.
- SQLAlchemy.
- Conexiones.
- Modelos de persistencia.
- Migraciones.

La capa de dominio no deberá importar estas implementaciones.

---

# 25. Repositories

Las implementaciones concretas estarán en Infrastructure.

Ejemplo:

```
infrastructure/
└── repositories/
    └── case_repository.py
```

La relación será:

```
Domain
   │
   ▼
CaseRepository Interface
   ▲
   │
Infrastructure
   │
   ▼
SQLAlchemyCaseRepository
```

---

# 26. Excel Infrastructure

La lectura concreta del Excel estará en:

```
infrastructure/
└── excel/
    ├── excel_reader.py
    ├── excel_parser.py
    └── excel_validator.py
```

Se utilizará:

```
Pandas
```

La infraestructura Excel no deberá contener reglas de estimación.

---

# 27. AI Infrastructure

La comunicación con Ollama estará encapsulada.

```
infrastructure/
└── ai/
    ├── ollama_client.py
    ├── ai_provider.py
    └── prompts/
```

Conceptualmente:

```
Application / Domain
        ↓
AI Service Contract
        ↓
AI Provider
        ↓
Ollama
```

Esto permitirá cambiar posteriormente el proveedor o modelo.

---

# 28. Catálogos

Los archivos de los catálogos estarán separados del código:

```
catalog_service/
│
├── catalogo_estados.xlsx
├── catalogo_tiempos.xlsx
├── catalogo_responsables.xlsx
└── README.md
```

El código no deberá leer estos archivos directamente desde otros módulos.

El acceso será mediante:

```
Catalog Service
```

---

# 29. Catalog Infrastructure

Las implementaciones para cargar los catálogos estarán en:

```
infrastructure/
└── catalogs/
    ├── catalog_loader.py
    ├── state_catalog.py
    ├── time_catalog.py
    └── responsible_catalog.py
```

Estas implementaciones estarán detrás del contrato definido por la aplicación/dominio.

---

# 30. Tests

Las pruebas estarán separadas según su nivel.

```
tests/
│
├── unit/
├── integration/
└── e2e/
```

# 31. Unit Tests

Las pruebas unitarias deberán validar componentes aislados.

Ejemplo:

```
tests/unit/
├── domain/
│   ├── cases/
│   └── estimation/
│
└── application/
```

Casos importantes:

- Validación de casos.
- Filtrado.
- Estados.
- Categorías.
- Rangos.
- Estimación.
- Validación de resultados.

---

# 32. Integration Tests

Validarán la interacción entre componentes reales.

Ejemplo:

```
tests/integration/
├── repositories/
├── catalogs/
├── excel/
└── ai/
```

Podrán utilizar:

- PostgreSQL de pruebas.
- Archivos Excel de prueba.
- Ollama configurado para pruebas.

---

# 33. End-to-End Tests

Validarán el flujo completo.

```
tests/e2e/
└── test_process_cases.py
```

El flujo deberá validar:

```
Excel
 ↓
Responsable
 ↓
Casos
 ↓
Catálogos
 ↓
Estimación
 ↓
IA
 ↓
Resultado
```

---

# 34. Convenciones de Nombres

## Archivos

Se utilizará:

```
snake_case
```

Ejemplo:

```
case_service.py
case_repository.py
process_cases.py
```

---

## Clases

Se utilizará:

```
PascalCase
```

Ejemplo:

```
Case
CaseService
CaseRepository
EstimationEngine
```

---

## Funciones y métodos

Se utilizará:

```
snake_case
```

Ejemplo:

```
process_cases()
validate_case()
get_time_range()
```

---

## Variables

Se utilizará:

```
snake_case
```

Ejemplo:

```
case_data
selected_responsible
estimated_time
```

---

## Constantes

Se utilizará:

```
UPPER_SNAKE_CASE
```

Ejemplo:

```
MAX_PROCESSING_TIME
DEFAULT_TIMEOUT
```

Las reglas configurables de negocio no deberán convertirse en constantes si pertenecen a un catálogo.

---

# 35. Convenciones de Python

El backend utilizará Python.

Se deberá mantener:

- Type hints.
- Docstrings cuando aporten contexto.
- Funciones pequeñas.
- Clases con responsabilidad única.
- Validación mediante Pydantic cuando corresponda.
- Código asincrónico cuando sea necesario.
- Manejo explícito de excepciones.

---

# 36. Tipado

Se deberá utilizar tipado explícito.

Ejemplo conceptual:

```
def validate_case(case: Case) -> ValidationResult:
    ...
```

Se evitará:

```
def validate_case(case):
    ...
```

cuando el tipo pueda definirse claramente.

---

# 37. Imports

Los imports deberán mantenerse organizados.

Orden conceptual:

```
1. Librerías estándar
2. Librerías externas
3. Módulos internos
```

No deberán existir imports circulares.

---

# 38. Manejo de Excepciones

No se deberán utilizar excepciones genéricas como mecanismo principal de control de flujo.

Evitar:

```
except Exception:
    ...
```

sin una razón específica.

Las excepciones deberán representar situaciones conocidas.

Ejemplo:

```
CategoryNotConfiguredError
InvalidCaseError
CatalogNotFoundError
AIResponseInvalidError
```

---

# 39. Logs

El sistema deberá utilizar logging estructurado para registrar eventos relevantes.

Se deberán registrar, cuando corresponda:

- Inicio de procesamiento.
- Fin de procesamiento.
- Archivo procesado.
- Casos procesados.
- Casos rechazados.
- Errores.
- Errores de IA.
- Errores de infraestructura.

No se deberán registrar datos sensibles innecesarios.

---

# 40. Configuración

La configuración deberá estar separada del código.

Ejemplo:

```
.env
```

Variables potenciales:

```
DATABASE_URL
OLLAMA_BASE_URL
OLLAMA_MODEL
OLLAMA_TIMEOUT
APP_ENV
APP_DEBUG
```

> Nota: el nombre real de la base de datos es `botcomproject` (ver `backend/.env.example`).

El archivo `.env` real no deberá almacenarse en Git.

Se deberá proporcionar:

```
.env.example
```

---

# 41. API

Los endpoints deberán utilizar versionamiento.

Ejemplo:

```
/api/v1/cases/process
```

Las rutas deberán utilizar nombres consistentes y orientados a recursos.

La API no deberá contener reglas de negocio.

---

# 42. Dependencias

La dirección de dependencias deberá respetar:

```
API
 ↓
Application
 ↓
Domain
```

Infrastructure implementará las interfaces necesarias:

```
Infrastructure
      ↑
Domain
```

El dominio nunca deberá depender directamente de Infrastructure.

---

# 43. Regla de Acceso a Base de Datos

Ningún componente de:

```
API
Application
Domain
```

deberá ejecutar directamente:

```
SQL
```

El acceso deberá realizarse mediante repositorios.

---

# 44. Regla de Acceso a Catálogos

Ningún módulo consumidor podrá realizar:

```
Excel
 ↓
Lectura directa de catálogo
```

El acceso deberá ser:

```
Módulo
   ↓
Catalog Service
   ↓
Catálogo
```

---

# 45. Regla de Acceso a IA

Ningún endpoint deberá comunicarse directamente con Ollama.

Incorrecto:

```
API
 ↓
Ollama
```

Correcto:

```
API
 ↓
Application
 ↓
AI Service
 ↓
AI Provider
 ↓
Ollama
```

---

# 46. Regla de Responsabilidad de los Endpoints

Un endpoint deberá actuar como adaptador.

Ejemplo:

```
POST /api/v1/cases/process
```

deberá:

```
Recibir solicitud
      ↓
Validar entrada
      ↓
Invocar Use Case
      ↓
Transformar resultado
      ↓
Responder
```

No deberá:

```
Leer Excel
Consultar PostgreSQL
Consultar catálogos
Llamar Ollama
Calcular tiempos
```

directamente.

---

# 47. Convención para Servicios

Los servicios deberán tener una única responsabilidad.

Ejemplos válidos:

```
CaseService
CatalogService
AIService
EstimationEngine
```

Se deberán evitar servicios genéricos como:

```
SystemService
GeneralService
UtilsService
```

cuando no exista una responsabilidad clara.

---

# 48. Convención para Repositorios

Los repositorios deberán representar una abstracción de persistencia.

Ejemplo:

```
CaseRepository
```

No deberán contener reglas de negocio.

Incorrecto:

```
case_repository.process_business_rules()
```

Correcto:

```
case_repository.save(case)
```

---

# 49. Convención para DTOs

Los DTO deberán utilizar nombres que indiquen claramente su propósito.

Ejemplos:

```
ProcessCasesRequest
ProcessCasesResponse
CaseDTO
EstimationDTO
ProcessingResultDTO
```

No deberán mezclarse con las entidades de dominio.

---

# 50. Convención para Tests

Los nombres de los tests deberán describir el comportamiento esperado.

Ejemplo:

```
test_should_reject_case_when_status_is_not_processable()
```

En lugar de:

```
test_case_1()
```

Los tests deberán seguir el patrón:

```
Arrange
Act
Assert
```

---

# 51. Calidad del Código

Todo código nuevo deberá cumplir como mínimo:

- Formato consistente.
- Tipado.
- Tests cuando corresponda.
- Sin código muerto.
- Sin imports innecesarios.
- Sin lógica duplicada.
- Sin credenciales en código.
- Sin reglas de negocio ocultas.

---

# 52. Git

La estructura deberá utilizar control de versiones.

Los commits deberán ser descriptivos.

Ejemplos:

```
feat: add case validator
feat: implement estimation engine
fix: validate processable status
test: add case filter tests
docs: update case contract
```

---

# 53. Regla de Documentación

Cuando una implementación modifique una decisión arquitectónica o de negocio:

```
Cambio
 ↓
Identificar documento afectado
 ↓
Actualizar documento
 ↓
Actualizar versión
 ↓
Implementar
```

El código no deberá convertirse en la única fuente de verdad de una regla de negocio.

---

# 54. Regla para OpenCode

OpenCode deberá utilizar como fuente de contexto:

```
Project Charter
Análisis del Proceso de Negocio
Glosario
Mapa de Módulos
Diseño de Gestión de Casos
Estimation Engine
AI Service
Case Contract
Catálogo de Estados
Catálogo de Responsables
Catálogo de Tiempos
Arquitectura del Sistema
Estructura y Convenciones del Proyecto
```

Antes de generar código, deberá respetar las decisiones establecidas en dichos documentos.

Si existe una contradicción entre documentos, **no deberá asumir una solución silenciosamente**.

Deberá identificarse la contradicción y actualizar primero la documentación correspondiente.

---

# 55. Regla de Creación de Archivos

No se deberán crear archivos únicamente porque una estructura futura los contemple.

Un archivo deberá crearse cuando exista una responsabilidad real que lo justifique.

Esto evita:

```
Archivos vacíos
Clases innecesarias
Servicios genéricos
Módulos artificiales
```

---

# 56. Regla de Creación de Módulos

Antes de crear un nuevo módulo deberá existir una necesidad funcional o técnica real.

La creación deberá justificarse por:

- Nueva responsabilidad.
- Nuevo dominio.
- Nuevo componente.
- Nueva integración.
- Necesidad de aislamiento.

---

# 57. Estructura Inicial Recomendada

La estructura inicial de V1 podrá comenzar de la siguiente manera:

```
BOT-COMProject/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   ├── schemas/
│   │   │   └── dependencies/
│   │   │
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   ├── services/
│   │   │   └── dto/
│   │   │
│   │   ├── domain/
│   │   │   ├── cases/
│   │   │   ├── estimation/
│   │   │   ├── catalogs/
│   │   │   └── results/
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   ├── excel/
│   │   │   ├── ai/
│   │   │   ├── catalogs/
│   │   │   └── repositories/
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│
├── catalog_service/
│   ├── catalogo_estados.xlsx
│   ├── catalogo_tiempos.xlsx
│   ├── catalogo_responsables.xlsx
│   └── README.md
│
├── docs/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

> Esta estructura es la estructura inicial. No significa que todos los directorios deban contener archivos desde el primer commit.
> 

---

# 58. Reglas de No Implementación

No deberán implementarse en V1:

```
Authentication
JWT
Users
Roles
Permissions
Sessions
COMProject Integration
Automatic Rule Creation
Automatic Catalog Modification
```

Aunque algunos puedan aparecer en estructuras futuras, no deberán generar código innecesario en V1.

---

# 59. Criterios de Cumplimiento

La estructura se considerará correctamente implementada cuando:

- Las capas estén claramente separadas.
- Los endpoints no contengan lógica de negocio.
- Los repositorios abstraigan la persistencia.
- Los catálogos sean accedidos mediante `Catalog Service`.
- Ollama esté encapsulado mediante `AI Service`.
- Las entidades de dominio no dependan de infraestructura.
- Existan pruebas separadas por nivel.
- Los nombres sigan las convenciones definidas.
- No existan módulos creados únicamente por anticipación.
- OpenCode pueda identificar claramente dónde debe implementar cada responsabilidad.

---

# 60. Relación con Otros Documentos

| Documento | Relación |
| --- | --- |
| Project Charter | Define alcance y V1 |
| Análisis del Proceso | Define flujo del negocio |
| Mapa de Módulos | Define módulos |
| Arquitectura del Sistema | Define organización arquitectónica |
| Diseño Gestión de Casos | Define comportamiento del módulo |
| Estimation Engine | Define estimación |
| AI Service | Define interacción con IA |
| Case Contract | Define estructura del caso |
| Catálogo Estados | Define estados |
| Catálogo Responsables | Define responsables |
| Catálogo Tiempos | Define rangos |
| Estructura y Convenciones | Define organización física y estándares |

---

# 61. Regla de Consistencia

Este documento no podrá contradecir la arquitectura ni las reglas de negocio establecidas.

Cuando se detecte una contradicción:

```
Contradicción
      ↓
Identificar documento origen
      ↓
Determinar decisión correcta
      ↓
Actualizar documentos afectados
      ↓
Actualizar versiones
      ↓
Continuar implementación
```

---

# 62. Estado

La **Estructura y Convenciones del Proyecto V1** queda definida como referencia para la implementación.

Su objetivo principal es evitar que durante el desarrollo se tomen decisiones arbitrarias sobre:

- Ubicación de archivos.
- Nombres.
- Dependencias.
- Capas.
- Servicios.
- Repositorios.
- Tests.
- Integraciones.