**Proyecto:** BOT-COMProject

**Versión:** 1.2

**Estado:** Definido

**Tipo:** Contrato técnico

---

# 1. Objetivo

Definir el contrato de comunicación entre el Frontend y el Backend de **BOT-COMProject V1**.

Este documento establece:

- Endpoints disponibles.
- Métodos HTTP.
- Parámetros.
- Estructura de solicitudes.
- Estructura de respuestas.
- Códigos HTTP.
- Formato de errores.
- Convenciones de API.
- Responsabilidades de cada endpoint.
- Identificación de ejecuciones de procesamiento.

El documento **no define la implementación interna** de los servicios.

---

# 2. Alcance

La API V1 permitirá:

```
Consultar responsables
        ↓
Cargar Maestro de Casos
        ↓
Procesar casos
        ↓
Consultar ejecución
        ↓
Consultar resultados
        ↓
Consultar errores/rechazos
        ↓
Exportar resultados
```

La API no realizará directamente:

- Comunicación con COMProject.
- Comunicación directa con Ollama desde el frontend.
- Acceso directo a PostgreSQL.
- Acceso directo a los catálogos.
- Implementación de reglas de negocio.

---

# 3. Base URL

La API utilizará:

```
/api/v1
```

Ejemplo:

```
http://localhost:8000/api/v1
```

La URL definitiva del entorno deberá manejarse mediante configuración.

---

# 4. Formato

Las respuestas utilizarán:

```
application/json
```

Excepto endpoints que específicamente devuelvan archivos.

---

# 5. Convenciones Generales

## 5.1 Versionamiento

La versión estará incluida en la URL:

```
/api/v1
```

---

## 5.2 Identificadores

Las entidades persistentes utilizarán UUID.

Ejemplo:

```
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 5.3 Fechas

Las fechas deberán utilizar ISO 8601.

Ejemplo:

```
2026-08-15T20:30:00
```

Cuando corresponda, deberá incluirse información de zona horaria.

---

## 5.4 Campos

Los nombres de los campos utilizarán:

```
snake_case
```

Ejemplo:

```
{
  "case_code": "INC001245",
  "responsible_name": "Carlos Rodríguez"
}
```

---

# 6. Endpoints V1

La API estará compuesta actualmente por los siguientes endpoints (estado real de la implementación):

| Método | Endpoint | Responsabilidad |
| --- | --- | --- |
| `GET` | `/health` | Estado general del sistema |
| `GET` | `/uploads` | Listar uploads cargados |
| `POST` | `/uploads` | Cargar Maestro de Casos |
| `POST` | `/cases/process` | Ejecutar procesamiento |
| `GET` | `/cases/responsible` | Responsables con conteo de casos |
| `GET` | `/cases/responsible/{name}` | Casos de un responsable |
| `GET` | `/processing/{processing_id}` | Consultar ejecución y resultados |
| `GET` | `/processing/{processing_id}/rejected` | Consultar casos rechazados |
| `GET` | `/processing/{processing_id}/export` | Exportar resultados a Excel (11 columnas, incluye Descripción IA y Tiempo Estimado) |
| `POST` | `/ai/process-responsible` | Procesar todos los casos en catálogo de un responsable (batch, guarda en BD) |
| `POST` | `/ai/generate-description` | Generar descripción profesional con IA |
| `POST` | `/ai/estimate-time` | Estimar tiempo con IA |
| `GET` | `/ai/catalog` | Consultar el catálogo de tiempos |
| `POST` | `/ai/catalog/load` | Cargar catálogo de tiempos desde Excel |
| `GET` | `/ai/results/{processing_id}` | Consultar resultados IA guardados |
| `GET` | `/ai/health` | Estado del servicio de IA |
| `POST` | `/ai/test-process` | Prueba de procesamiento IA sin guardar en BD |
| `WS` | `/ai/ws/{client_id}` | Progreso en tiempo real |

> Nota: el catálogo de tiempos se almacena en la tabla `catalogo_tiempos` de PostgreSQL. Las descripciones de IA persisten en `ai_results` junto con `case_type`, `status` y `final_category` (ver `backend/DATABASE.md`).
>
> Nota: `POST /uploads` crea un processing por archivo y devuelve `upload_id` + `processing_id`. Los resultados de IA de todos los responsables se acumulan bajo ese mismo `processing_id`.
>
> Nota: los resultados de IA (`GET /ai/results/{processing_id}` y la respuesta de `POST /ai/process-responsible`) incluyen el campo `area` y `fecha_solucion` por resultado, el resumen `summary.by_area` (desglose `{ area: {count, hours} }`) y `results_by_area` con la estructura `{ área: { total_hours, by_date: { 'YYYY-MM-DD': { total_hours, cases: [resultado, ...] } }, sin_fecha: { total_hours, cases: [...] } } }` (los casos por área/por fecha de solución; casos sin área van a `Sin área` y sin fecha a `sin_fecha`).
>
> Nota: `GET /ai/results/{processing_id}` también retorna `semanas_disponibles` (semanas lunes→domingo derivadas de `fecha_solucion`, con `count` y `total_hours`) y `total_results_all` (total sin filtro de rango). El filtro por rango `fecha_inicio`/`fecha_fin` se aplica sobre `fecha_solucion`.
>
> Nota: `ai_results` tiene restricción `UNIQUE(processing_id, case_id)` (migración `010`). El repositorio `SQLAlchemyAIResultRepository.save()` es idempotente (upsert por `processing_id` + `case_id`), por lo que reprocesar un responsable no genera filas duplicadas. `processed_cases` del processing se recalcula desde la BD (`count_by_processing`) en lugar de acumular.
>
> Stubs no registrados en `main.py`: `GET /responsibles` (`routers/responsibles.py`), `GET /cases` y `GET /cases/{case_id}` (`routers/cases.py`).

---

# 6.1 Frontend (SPA React + Vite)

El frontend es una SPA de 3 pasos (`frontend/src/App.jsx`) que consume la API V1 a través del proxy de Vite (`/api` → `http://localhost:8002`):

| Paso | Página | Endpoints |
|------|--------|-----------|
| 1. Carga | `UploadPage.jsx` | `POST /api/v1/uploads` (multipart) |
| 2. Responsable | `ResponsiblePage.jsx` | `GET /api/v1/cases/responsible?upload_id=` |
| 3. Reporte | `ResultsPage.jsx` | `POST /api/v1/ai/process-responsible` → `GET /api/v1/ai/results/{processing_id}` |

Funcionalidades del reporte (en memoria, no persisten):
- Selector de semana (desde `semanas_disponibles`).
- Filtros por número de caso, cliente y área.
- Edición de la descripción generada por caso (solo sesión).
- Tabla de detalle con caso, cliente, tipo, área, fecha de solución, descripción, tiempo y acción.

---

# 7. Obtener Responsables

## Endpoint

```
GET /api/v1/responsibles
```

## Responsabilidad

Obtener los responsables disponibles para la V1.

La información deberá ser proporcionada mediante el `Catalog Service`.

El frontend no deberá conocer directamente dónde se almacenan los responsables.

---

## Response

### HTTP 200

```
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Carlos Rodríguez"
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "name": "Juan Pérez"
    }
  ],
  "total": 2
}
```

Solo deberán retornar responsables configurados como activos.

---

# 8. Carga del Maestro de Casos

## Endpoint

```
POST /api/v1/uploads
```

## Responsabilidad

Recibir el archivo Excel exportado desde Aranda y registrar la carga.

El endpoint **no deberá ejecutar el procesamiento completo de los casos**.

Flujo:

```
Recibir archivo
      ↓
Validar archivo
      ↓
Registrar Upload
      ↓
Retornar upload_id
```

---

## Request

Content-Type:

```
multipart/form-data
```

Campo:

```
file
```

Ejemplo:

```
file = ASDK_Full_Caso.xlsx
```

---

## Response

### HTTP 201

```
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "ASDK_Full_Caso.xlsx",
  "status": "UPLOADED",
  "created_at": "2026-08-15T20:30:00"
}
```

El `id` retornado corresponde al `upload_id` utilizado posteriormente para iniciar el procesamiento.

### 8.1 Límites

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `MAX_FILE_SIZE` | 50 MB | Tamaño máximo del archivo |
| `ALLOWED_EXTENSIONS` | `.xlsx` | Extensiones permitidas |

Si el archivo excede el tamaño máximo, el sistema retornará:

```
HTTP 413
{
  "error": "FILE_TOO_LARGE",
  "message": "El archivo excede el tamaño máximo permitido (50 MB)"
}
```

---

# 9. Procesar Casos

Este será el endpoint principal de la V1.

## Endpoint

```
POST /api/v1/cases/process
```

## Responsabilidad

Crear una ejecución de procesamiento para los casos pertenecientes al `Upload` y al responsable seleccionado.

El frontend realizará una única llamada.

El backend coordinará:

```
Process Cases
      │
      ├── Excel / Cases
      ├── Catalog Service
      ├── Case Repository
      ├── Estimation Engine
      └── AI Service
```

---

# 10. Request

```
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "responsible_id": "650e8400-e29b-41d4-a716-446655440001"
}
```

### Campos

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `upload_id` | UUID | Sí | Archivo que será procesado |
| `responsible_id` | UUID | Sí | Responsable seleccionado |

---

# 11. Validaciones Iniciales

Antes de crear la ejecución se deberá validar:

```
upload_id válido
       ↓
Upload existente
       ↓
Upload disponible para procesamiento
       ↓
responsible_id válido
       ↓
Responsable activo
       ↓
Crear Processing
       ↓
Iniciar procesamiento
```

Las reglas específicas de filtrado de casos no deberán estar dentro del endpoint.

---

# 12. Processing

Cada llamada válida a:

```
POST /cases/process
```

representará una **ejecución concreta del procesamiento**.

La ejecución será identificada mediante:

```
processing_id
```

Conceptualmente:

```
Upload
   │
   ├── Processing 1
   ├── Processing 2
   └── Processing 3
```

Esto permite conservar la trazabilidad de cada ejecución.

> El `processing_id` representa la ejecución del proceso, no un caso individual.
> 

---

# 13. Estados del Processing

Los estados técnicos serán:

```
PENDING
PROCESSING
COMPLETED
FAILED
```

Estos estados no representan los estados de los casos provenientes de Aranda.

Ejemplo:

```
Processing.status
        ↓
COMPLETED

Case.status
        ↓
Solucionado
```

Son conceptos diferentes.

---

# 14. Response de Procesamiento

### HTTP 200

```
{
  "processing_id": "750e8400-e29b-41d4-a716-446655440002",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "responsible_id": "650e8400-e29b-41d4-a716-446655440001",
  "status": "COMPLETED",
  "summary": {
    "total_cases": 120,
    "processed_cases": 85,
    "rejected_cases": 35
  }
}
```

El `processing_id` deberá poder utilizarse posteriormente para consultar:

```
GET /processing/{processing_id}
```

o:

```
GET /processing/{processing_id}/rejected
```

### 9.1 Comportamiento

El endpoint `POST /cases/process` funcionará de manera **síncrona**.

El tiempo máximo de respuesta será de **5 minutos** (300 segundos).

Si el procesamiento excede este tiempo, el sistema retornará:

```
HTTP 504
{
  "error": "PROCESSING_TIMEOUT",
  "message": "El procesamiento excedió el tiempo máximo permitido"
}
```

---

# 15. Procesamiento Parcial

El procesamiento deberá permitir que los casos válidos continúen aunque otros casos sean rechazados.

Ejemplo:

```
120 casos
   │
   ├── 85 procesados
   └── 35 rechazados
```

La existencia de casos rechazados **no significa que la ejecución completa haya fallado**.

Por ejemplo:

```
Processing.status = COMPLETED
```

puede coexistir con:

```
processed_cases = 85
rejected_cases = 35
```

---

# 16. Flujo Interno

```
POST /cases/process
          │
          ▼
      Application
          │
          ▼
   Crear Processing
          │
          ▼
   Obtener casos del Upload
          │
          ▼
   Filtrar responsable
          │
          ▼
   Validar estado
          │
          ▼
   Validar información
          │
          ▼
   Consultar categoría
          │
          ▼
   Obtener rango
          │
          ▼
  Estimation Engine
          │
          ▼
      AI Service
          │
          ▼
     Validar resultado
          │
          ▼
       Persistir
          │
          ▼
   Actualizar Processing
```

---

# 17. Consultar Processing

## Endpoint

```
GET /api/v1/processing/{processing_id}
```

## Responsabilidad

Obtener información de una ejecución concreta y sus resultados procesados.

---

## Response

### HTTP 200

```
{
  "processing_id": "750e8400-e29b-41d4-a716-446655440002",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "responsible_id": "650e8400-e29b-41d4-a716-446655440001",
  "status": "COMPLETED",
  "summary": {
    "total_cases": 120,
    "processed_cases": 85,
    "rejected_cases": 35
  },
  "results": [
    {
      "case_id": "850e8400-e29b-41d4-a716-446655440003",
      "case_code": "INC001245",
      "responsible_name": "Carlos Rodríguez",
      "project": "Hospital Militar",
      "final_category": "Ingreso de Huella",
      "estimated_minutes": 45,
      "description": "Se realizó la configuración..."
    }
  ]
}
```

---

# 18. Consultar Casos Rechazados

## Endpoint

```
GET /api/v1/processing/{processing_id}/rejected
```

## Responsabilidad

Obtener los casos que no pudieron continuar durante una ejecución.

---

## Response

```
{
  "items": [
    {
      "case_id": "950e8400-e29b-41d4-a716-446655440004",
      "case_code": "INC001246",
      "reason_code": "CATEGORIA_NO_CONFIGURADA",
      "message": "La categoría no posee una configuración activa."
    },
    {
      "case_id": "950e8400-e29b-41d4-a716-446655440005",
      "case_code": "INC001247",
      "reason_code": "ESTADO_NO_PROCESABLE",
      "message": "El estado del caso no es procesable."
    }
  ],
  "total": 2
}
```

---

# 19. Códigos de Rechazo

Los códigos deberán ser estandarizados.

Inicialmente:

```
INCOMPLETE_DATA
RESPONSIBLE_NOT_SELECTED
RESPONSIBLE_INVALID
STATUS_NOT_PROCESSABLE
CATEGORY_NOT_CONFIGURED
TIME_RANGE_NOT_CONFIGURED
DUPLICATE
INVALID_RESULT
```

La lista deberá mantenerse alineada con:

- Gestión de Casos.
- Catálogo de Estados.
- Catálogo de Tiempos.
- Estimation Engine.
- AI Service.

---

# 20. Consultar Casos

## Endpoint

```
GET /api/v1/cases
```

## Responsabilidad

Consultar casos almacenados.

---

## Parámetros opcionales

```
upload_id
responsible_id
status
page
page_size
```

### 20.1 Paginación

| Parámetro | Tipo | Obligatorio | Valor por Defecto | Descripción |
|-----------|------|-------------|-------------------|-------------|
| `page` | Integer | No | `1` | Número de página |
| `page_size` | Integer | No | `20` | Registros por página |

`status` representa exclusivamente el **estado original proveniente de Aranda**.

Ejemplo:

```
GET /api/v1/cases?upload_id=...&responsible_id=...&status=Solucionado
```

---

## Response

```
{
  "items": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440003",
      "case_code": "INC001245",
      "responsible_name": "Carlos Rodríguez",
      "user_name": "Juan Pérez",
      "project": "Hospital Militar",
      "status": "Solucionado",
      "final_category": "Ingreso de Huella",
      "registered_at": "2026-08-14",
      "description": "Problema con el registro de huella.",
      "solution": "Se realizó la configuración correspondiente."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

---

# 21. Consultar Caso

## Endpoint

```
GET /api/v1/cases/{case_id}
```

## Response

```
{
  "id": "850e8400-e29b-41d4-a716-446655440003",
  "case_code": "INC001245",
  "responsible_name": "Carlos Rodríguez",
  "project": "Hospital Militar",
  "status": "Solucionado",
  "final_category": "Ingreso de Huella",
  "description": "Descripción original...",
  "solution": "Solución original...",
  "registered_at": "2026-08-14T10:30:00"
}
```

La información original del caso no deberá ser reemplazada por información generada por IA.

---

# 22. Exportar Resultados

## Endpoint

```
GET /api/v1/processing/{processing_id}/export
```

## Responsabilidad

Generar el archivo correspondiente a los resultados de una ejecución.

La API devolverá un archivo.

Content-Type:

```
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

El archivo deberá contener como mínimo:

```
Código
Responsable
Proyecto
Categoría
Estado
Tiempo estimado
Descripción
```

Solo podrán exportarse resultados pertenecientes al `processing_id` solicitado.

---

# 23. Errores

Todas las respuestas de error deberán utilizar una estructura uniforme.

```
{
  "error": {
    "code": "UPLOAD_NOT_FOUND",
    "message": "El archivo solicitado no existe.",
    "details": null
  }
}
```

---

# 24. Códigos HTTP

| Código | Uso |
| --- | --- |
| `200` | Operación exitosa |
| `201` | Recurso creado |
| `400` | Solicitud inválida |
| `404` | Recurso no encontrado |
| `409` | Conflicto |
| `422` | Error de validación |
| `500` | Error interno |
| `503` | Servicio temporalmente no disponible |

---

# 25. Errores de Validación

### HTTP 422

```
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La solicitud contiene datos inválidos.",
    "details": [
      {
        "field": "responsible_id",
        "message": "El campo es obligatorio."
      }
    ]
  }
}
```

---

# 26. Responsabilidad del Backend

El backend será responsable de:

- Validar solicitudes.
- Validar entidades.
- Ejecutar reglas de negocio.
- Crear y controlar ejecuciones de procesamiento.
- Orquestar servicios.
- Consultar repositorios.
- Consultar catálogos mediante `Catalog Service`.
- Ejecutar `Estimation Engine`.
- Ejecutar `AI Service`.
- Persistir resultados.
- Generar exportaciones.
- Generar respuestas.

---

# 27. Responsabilidad del Frontend

El frontend será responsable de:

- Consultar responsables.
- Cargar el archivo.
- Permitir seleccionar un responsable.
- Ejecutar el procesamiento.
- Consultar el resultado.
- Mostrar casos procesados.
- Mostrar casos rechazados.
- Permitir revisión.
- Solicitar exportación.

El frontend **no deberá implementar reglas de negocio**.

---

# 28. Restricciones Arquitectónicas

### API-01

Los endpoints no deberán contener reglas de negocio complejas.

### API-02

Los endpoints deberán delegar la lógica a servicios de aplicación.

### API-03

El frontend no podrá comunicarse directamente con:

```
PostgreSQL
Ollama
Catalog Files
Repositories
```

### API-04

El frontend no deberá comunicarse directamente con el servidor Ollama; toda interacción con IA se realiza a través de los endpoints `/api/v1/ai/*` del backend.

### API-05

El procesamiento se iniciará mediante:

```
POST /api/v1/cases/process
```

### API-06

Los catálogos deberán consultarse mediante `Catalog Service`.

### API-07

Cada ejecución deberá estar identificada mediante `processing_id`.

### API-08

Los resultados de una ejecución deberán poder relacionarse con su `processing_id`.

### API-09

El estado técnico de `Processing` no deberá confundirse con el estado original del caso.

---

# 29. Idempotencia

La operación:

```
POST /api/v1/cases/process
```

deberá evitar procesamientos accidentales duplicados.

La estrategia de idempotencia deberá considerar como mínimo:

```
upload_id
+
responsible_id
+
ejecución activa
```

No deberá asumirse que repetir una petición HTTP implica automáticamente crear una nueva ejecución.

La implementación deberá impedir ejecuciones concurrentes no intencionadas para el mismo contexto cuando exista una ejecución activa.

---

# 30. Flujo API V1

El flujo esperado será:

```
1. GET /responsibles
        │
        ▼
2. Usuario selecciona responsable
        │
        ▼
3. POST /uploads
        │
        ▼
4. POST /cases/process
        │
        ▼
5. GET /processing/{processing_id}
        │
        ▼
6. Usuario revisa resultados
        │
        ├──────────────► GET /processing/{id}/rejected
        │
        ▼
7. GET /processing/{id}/export
```

---

# 31. Seguridad V1

La V1 no implementará autenticación.

Quedan fuera:

```
JWT
Login
Usuarios
Roles
Permisos
Sesiones
```

La seguridad de infraestructura deberá manejarse independientemente de la lógica funcional.

---

# 32. Documentación Automática

La API deberá generar documentación mediante:

```
OpenAPI
```

La implementación deberá mantener sincronizados:

```
API Contract
      ↓
Pydantic Schemas
      ↓
FastAPI Endpoints
      ↓
OpenAPI
```

---

# 33. Pruebas del Contrato

Cada endpoint deberá contar como mínimo con pruebas para:

### Caso exitoso

```
Request válido
     ↓
Response esperado
```

### Validación

```
Request inválido
     ↓
HTTP 422
```

### Recurso inexistente

```
ID inexistente
     ↓
HTTP 404
```

### Conflicto

```
Operación incompatible
     ↓
HTTP 409
```

### Error interno

```
Error inesperado
     ↓
HTTP 500
```

Los endpoints críticos deberán tener pruebas adicionales:

```
POST /uploads
POST /cases/process
GET /processing/{processing_id}
GET /processing/{processing_id}/rejected
GET /processing/{processing_id}/export
```

---

# 34. Fuente de Verdad

Este documento define exclusivamente:

- Contratos HTTP.
- Requests.
- Responses.
- Códigos HTTP.
- Convenciones de API.
- Responsabilidades de comunicación.
- Identificación de ejecuciones mediante `processing_id`.

No deberá utilizarse este documento para definir reglas internas de negocio.

Las reglas deberán consultarse en:

```
Business Process Analysis
        ↓
Catálogo de Estados
        ↓
Catálogo de Responsables
        ↓
Catálogo de Tiempos
        ↓
Gestión de Casos
        ↓
Estimation Engine
        ↓
AI Service
```

---

# 35. Regla de Consistencia

Cuando se modifique un endpoint:

```
Cambio de API
      ↓
Actualizar API Contract
      ↓
Revisar Frontend
      ↓
Revisar Application Services
      ↓
Revisar modelos Pydantic
      ↓
Revisar Modelo de Datos
      ↓
Revisar pruebas
      ↓
Verificar documentación OpenAPI
```

Cuando el cambio afecte:

```
processing_id
Processing
Persistencia
```

también deberá revisarse obligatoriamente el **Modelo de Datos**.

---

# 36. Definición V1

La API V1 permitirá que el usuario realice el flujo completo:

```
Consultar responsables
      ↓
Seleccionar responsable
      ↓
Cargar Maestro
      ↓
Procesar casos
      ↓
Consultar ejecución
      ↓
Revisar resultados
      ↓
Revisar rechazados
      ↓
Exportar resultados
```

La API no realizará integración automática con COMProject.

---

# 37. Decisiones derivadas de la versión 1.1

La versión 1.1 introduce una decisión importante:

> **Una ejecución de procesamiento es una entidad identificable independientemente del archivo y de los casos.**
> 

Conceptualmente:

```
Upload
   │
   └──────< Processing
                 │
                 ├──────< resultados
                 │
                 └──────< rechazados
```

Esto permite:

- Identificar exactamente qué ejecución produjo un resultado.
- Diferenciar múltiples ejecuciones sobre un mismo archivo.
- Consultar resultados posteriormente.
- Mantener trazabilidad.
- Preparar el sistema para reprocesamiento futuro.