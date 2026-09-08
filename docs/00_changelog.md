# Changelog de Documentación

Registro de correcciones realizadas en la documentación del proyecto BOT-COMProject.

---

## [2026-09-08] División de horas por área y fecha de solución

- `POST /api/v1/ai/process-responsible` y `GET /api/v1/ai/results/{processing_id}` retornan en `results_by_area`:
  `{ área: { total_hours, by_date: { 'YYYY-MM-DD': { total_hours, cases: [AIResultResponse, ...] } }, sin_fecha: { total_hours, cases: [...] } } }`.
- Cada `AIResultResponse` incluye el campo `fecha_solucion` (YYYY-MM-DD) del caso.
- Nuevo campo `fecha_solucion` en el pipeline del Excel (columna `Fecha de Solución`) y en la tabla `cases`
  (migración alembic `007`, columna `fecha_solucion TIMESTAMP`).
- Archivos: `column_mapper.py`, `structure_validator.py`, `data_extractor.py`, `data_normalizer.py`,
  `case_mapper.py`, `domain/entities/case.py`, `database/models/case.py`, `case_repository.py`,
  `uploads.py`, `api/schemas/ai.py`, `api/routes/ai.py`, `alembic/versions/007_add_fecha_solucion_to_cases.py`.

---

## [2026-09-08] Filtro de estados procesables en el módulo IA

- `POST /api/v1/ai/process-responsible` y `GET/POST test-process` solo generan descripción IA para casos con estado **Cerrado** o **Solucionado**.
- Fuente de verdad: catálogo de estados V1 (`backend/app/infrastructure/catalogs/status_catalog.py`, `PROCESSABLE_STATUSES`).
- Se eliminaron los resultados IA históricos de estados no procesables y se recalculó `processed_cases` de los processings afectados.
- Archivos modificados: `backend/app/api/routes/ai.py`, `docs/00_changelog.md` (este registro).

---

## [2026-08-19] Corrección de inconsistencias documentales

### Unificación de nombre del servicio de catálogos
- Se unificó el nombre a **"Catalog Service"** en toda la documentación.
- Archivos modificados: `03_analisis_proceso_negocio.md`, `modelo_datos.md`, 
  `01_estructura_y_convenciones.md`, `catalogo_tiempos.md`.
- Motivo: El Project Charter (fuente de verdad) usa "Catalog Service".

### Corrección de opcionalidad de campos
- Campos `user_name`, `description`, `solution` cambiados de **OBLIGATORIO** a **OPCIONAL**.
- Archivo modificado: `modelo_datos.md`.
- Motivo: El Case Contract (`case_contract.md`) es la fuente de verdad y los define como opcionales.

### Reorganización de archivos
- **Movido:** `07_persistencia/modelo_datos.md` → `04_modulos/gestion_casos/modelo_datos_modulo.md`
  - Motivo: El archivo contenía el diseño detallado del módulo Gestión de Casos, no un modelo SQL.
- **Renombrado:** `01_contexto/03_analisis_proceso_negocio.md` → `01_contexto/03_arquitectura_modulos.md`
  - Motivo: El archivo contenía la arquitectura de módulos/componentes, no un análisis de proceso de negocio.

### Corrección de referencias rotas
- Referencia `docs/README.md` corregida a `README.md` en `prompt_maestro.md`.

### Actualización de referencias cruzadas
- Actualizadas 7 referencias en `opencode.md` y `prompt_maestro.md` apuntando a las 
  nuevas ubicaciones/nombres de archivos.

---

## [2026-08-20] Segunda ronda de corrección de inconsistencias

### Completar unificación del nombre del servicio de catálogos
- Se completó la unificación a **"Catalog Service"** en los archivos restantes.
- Archivos modificados: `contratos_api.md` (3 ocurrencias), `catalogo_responsables.md` (12 ocurrencias).
- Motivo: Estos archivos habían sido omitidos en la corrección anterior.

### Eliminación de directorio vacío
- **Eliminado:** directorio `07_persistencia/` (vacío después del movimiento de archivos).
- Motivo: El directorio no contenía documentos y generaba referencias rotas.

### Actualización de referencias a directorio eliminado
- Eliminadas referencias a `07_persistencia/` en `opencode.md` y `prompt_maestro.md`.
- Motivo: El directorio ya no existe.

### Renombrar directorio de catálogos
- **Renombrado:** `business_catalogs/` → `catalog_service/` en toda la documentación.
- Archivos modificados: `catalogo_tiempos.md`, `catalogo_responsables.md`, `catalogo_estados.md`, `01_estructura_y_convenciones.md`.
- Motivo: El directorio se llama `catalog_service/` en la estructura final del proyecto.

---

## [2026-08-20] Resolución de inconsistencias documentales

### Contradicción 1: Campo user_name
- Renombrado `user` a `user_name` en `procesamiento_maestro.md`.
- Motivo: Mantener consistencia con el Case Contract (`case_contract.md`).

### Contradicción 2: Campos description y solution obligatorios
- Cambiados `description` y `solution` de **OPCIONAL** a **OBLIGATORIO** en `case_contract.md`.
- Motivo: El procesamiento requiere estos campos para funcionar correctamente.

### Contradicción 3: Códigos de rechazo estandarizados a inglés
- Estandarizados todos los códigos de rechazo a **inglés** en 4 archivos:
  - `contratos_api.md`
  - `03_arquitectura_modulos.md`
  - `gestion_casos.md`
  - `modelo_datos_modulo.md`
- Mapeo de códigos:
  - `DATOS_INCOMPLETOS` → `INCOMPLETE_DATA`
  - `RESPONSABLE_NO_SELECCIONADO` → `RESPONSIBLE_NOT_SELECTED`
  - `RESPONSABLE_NO_VALIDO` → `RESPONSIBLE_INVALID`
  - `ESTADO_NO_PROCESABLE` → `STATUS_NOT_PROCESSABLE`
  - `CATEGORIA_NO_CONFIGURADA` → `CATEGORY_NOT_CONFIGURED`
  - `RANGO_NO_CONFIGURADO` → `TIME_RANGE_NOT_CONFIGURED`
  - `DUPLICADO` → `DUPLICATE`
  - `RESULTADO_INVALIDO` → `INVALID_RESULT`
- Motivo: Estandarización a un solo idioma en toda la documentación.

### Contradicción 4: Aclaración de capas en estructura de rechazo
- Agregada nota en `estimation_engine.md` aclarando que el formato de rechazo es **interno** (entre módulos).
- El formato expuesto a través de la API (definido en `contratos_api.md`) utiliza una estructura diferente.
- Motivo: Aclarar que no es una contradicción sino una diferencia entre capas.

---

## [2026-08-20] Resolución de información faltante

### Mapeo completo de columnas Excel
- Agregada tabla completa con nombres físicos de columnas en `procesamiento_maestro.md`.
- Mapeo: `Codigo Caso` → `case_code`, `Responsible Name` → `responsible_name`, etc.
- Motivo: La implementación del Excel Service requiere saber los nombres exactos de las columnas.

### Formato de fecha y manejo de duplicados
- Agregada sección de formato de fecha (`DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY-MM-DD`) en `procesamiento_maestro.md`.
- Agregada regla para duplicados: se procesa únicamente la primera ocurrencia.
- Motivo: Definir el comportamiento esperado del Excel Service.

### Longitudes máximas de campos
- Agregada columna de longitud en la tabla de campos de `case_contract.md`.
- Longitudes definidas: `case_code` (50), `responsible_name` (200), `project` (200), `status` (100), `final_category` (200).
- Motivo: Necesario para definir esquemas de base de datos y validaciones.

### Formato DateTime
- Agregada sección de formato de fechas en `case_contract.md`.
- Formato: `registered_at` → `YYYY-MM-DD`, `created_at` → `YYYY-MM-DDTHH:MM:SS`.
- Zona horaria: UTC para todos los campos.
- Motivo: Estandarizar el formato de fechas en todo el sistema.

### Parámetros de IA con valores por defecto
- Actualizada sección de parámetros en `ia_service.md`.
- Valores por defecto: `AI_MODEL` (qwen2.5-coder:latest), `AI_TEMPERATURE` (0.3), `AI_TIMEOUT` (60s), `AI_MAX_TOKENS` (500).
- Motivo: Definir valores iniciales para la configuración del servicio de IA.

### Límites de API
- Agregada sección de límites en `contratos_api.md`: `MAX_FILE_SIZE` (50 MB), `ALLOWED_EXTENSIONS` (.xlsx).
- Agregada respuesta HTTP 413 para archivos excesivamente grandes.
- Motivo: Definir restricciones de seguridad y rendimiento.

### Timeout de procesamiento
- Agregada sección de comportamiento en `contratos_api.md`: endpoint síncrono con timeout de 5 minutos.
- Agregada respuesta HTTP 504 para procesamiento que excede el tiempo máximo.
- Motivo: Definir el comportamiento del endpoint principal de procesamiento.

### Paginación
- Agregada tabla de parámetros de paginación con valores por defecto: `page` (1), `page_size` (20).
- Motivo: Formalizar los valores por defecto de paginación.

---

## [2026-08-20] Resolución de inconsistencias documentales (Auditoría completa)

### Problemas Bloqueantes Resueltos

#### B1: Opcionalidad de description y solution
- Cambiados `description` y `solution` de **OPCIONAL** a **OBLIGATORIO** en:
  - `case_contract.md` (líneas 705-714): Movidos de la lista de opcionales a la lista de obligatorios
  - `modelo_datos_modulo.md` (líneas 229-235): Movidos de "campos opcionales" a "campos obligatorios"
  - `modelo_datos_modulo.md` (líneas 1286-1292): Actualizada tabla final de campos
- Motivo: Resolución de contradicción interna en `case_contract.md` donde la tabla de campos los marcaba como obligatorios pero la sección de validación los lista como opcionales.

#### B2: Formato de registered_at
- Corregido formato en `contratos_api.md` (línea 716): Cambiado `"2026-08-14T10:30:00"` por `"2026-08-14"`
- Motivo: Estandarizar a formato `YYYY-MM-DD` (solo fecha) según lo decidido.

### Problemas Importantes Resueltos

#### I1: Campo user vs user_name
- Corregido ejemplo en `procesamiento_maestro.md` (línea 340): Cambiado `"user"` por `"user_name"`
- Motivo: Mantener consistencia con el Case Contract y el modelo de datos.

#### I2: Nombre Business Catalog Service vs Catalog Service
- Actualizado nombre en `03_arquitectura_modulos.md` (líneas 66-67, 978-979): Cambiado `Business Catalog Service` por `Catalog Service`
- Motivo: Estandarizar el nombre del servicio en toda la documentación.

#### I3: Referencias obsoletas a Business Process Analysis
- Actualizada etiqueta en `opencode.md` (línea 537): Cambiado `Reglas del proceso` por `Arquitectura de módulos`
- Actualizada etiqueta en `prompt_maestro.md` (línea 101): Cambiado `Proceso de negocio` por `Arquitectura de módulos`
- Motivo: El archivo `03_arquitectura_modulos.md` contiene arquitectura de módulos, no análisis de proceso de negocio.

#### I4: Reglas MGC duplicadas
- Unificadas reglas MGC en `gestion_casos.md` (líneas 978-1024): Reemplazadas 10 reglas MGC-01 a MGC-10 con referencia a `modelo_datos_modulo.md`
- Motivo: Evitar duplicación de reglas entre documentos. `modelo_datos_modulo.md` es la fuente autoritativa para reglas de negocio.

#### I5: Respuesta API sin campos obligatorios
- Agregados campos `description`, `solution`, `user_name` al ejemplo de respuesta en `contratos_api.md` (líneas 710-716)
- Motivo: La respuesta API debe incluir todos los campos definidos en el Case Contract.

#### I6: Modelo de IA inapropiado
- Corregido modelo por defecto en `ia_service.md` (líneas 498, 506): Cambiado `qwen2.5-coder:latest` por `qwen2.5:latest`
- Motivo: El modelo `qwen2.5-coder` está optimizado para codificación, no para generación de descripciones profesionales.

#### I7: Falta modelo_datos_modulo.md en árbol de archivos
- Agregado `modelo_datos_modulo.md` al árbol de archivos en `opencode.md` (línea 505)
- Motivo: El archivo existe pero no estaba listado en la estructura documental.

#### I8: Numeración de secciones rota
- Corregida numeración en `opencode.md` (línea 73): Cambiado `3.3.1` por `3.1.1`
- Motivo: Error de numeración que saltaba de 3.1 a 3.3.1.

### Mejoras Resueltas

#### M1-M3: Fuentes de verdad incompletas
- Agregadas entradas faltantes en tabla de fuentes de verdad de `opencode.md`:
  - `Modelo de Datos | 04_modulos/gestion_casos/modelo_datos_modulo.md`
  - `Case Contract | 06_contratos/case_contract.md`
  - `API | 08_api/contratos_api.md`
- Motivo: Estos documentos son fuentes autoritativas pero no estaban en la matriz.

### Archivos modificados (10):
1. `docs/06_contratos/case_contract.md`
2. `docs/04_modulos/gestion_casos/modelo_datos_modulo.md`
3. `docs/08_api/contratos_api.md`
4. `docs/04_modulos/procesamiento_maestro/procesamiento_maestro.md`
5. `docs/01_contexto/03_arquitectura_modulos.md`
6. `docs/09_agente/opencode.md`
7. `docs/09_agente/prompt_maestro.md`
8. `docs/04_modulos/ia_service/ia_service.md`
9. `docs/04_modulos/gestion_casos/gestion_casos.md`
10. `docs/00_changelog.md`

---

## [2026-09-04] Actualización documental post-implementación (Parte 1 + Parte 2 IA)

Ronda de actualización de la documentación para reflejar el estado **real** de la implementación (código, endpoints, modelo de IA, base de datos y configuración).

### Cambios de contexto/arquitectura
- **`README.md` (raíz)**: documento actualizado por completo con el estado real del proyecto.
- **`00_prompt_desarrolladores.md`**: actualizado stack tecnológico, modelo de IA, configuración de `AIConfig`, lista de endpoints y reglas.

### Modelo de IA (Parte 2)
- **Modelo configurado:** `qwen2.5-coder:3b` (instalado vía `ollama pull`, funcionando en localhost:11434).
- Actualizado en: `04_modulos/ia_service/ia_service.md` (tabla de parámetros y ejemplo), `00_prompt_desarrolladores.md` (sección de configuración y stack), `00_fase0_alineacion_contratos.md` (criterio de aceptación "Ollama funcionando").
- Motivo: `qwen2.5:latest` / `qwen2.5-coder:latest` no existen localmente y las pruebas reales se ejecutaron con `qwen2.5-coder:3b`.

### Variables de entorno
- `docs/03_desarrollo/01_estructura_y_convenciones.md`: variables actualizadas.
  - `OLLAMA_URL` → `OLLAMA_BASE_URL`.
  - `ENVIRONMENT`, `LOG_LEVEL` → `APP_ENV`, `APP_DEBUG`.
  - Se documenta el nombre real de la base de datos: `botcomproject`.

### Contratos de API y base de datos
- `docs/08_api/contratos_api.md`: inventario de endpoints actualizado con los reales:
  - `/health`, `/api/v1/uploads`, `/api/v1/cases/process`, `/api/v1/cases/responsible`, `/api/v1/processing/{id}`, `/api/v1/processing/{id}/rejected`, `/api/v1/processing/{id}/export`.
  - `/api/v1/ai/process-responsible`, `/api/v1/ai/generate-description`, `/api/v1/ai/estimate-time`, `/api/v1/ai/catalog`, `/api/v1/ai/catalog/load`, `/api/v1/ai/results/{processing_id}`, `/api/v1/ai/health`, WebSocket `/api/v1/ai/ws/{client_id}`.
  - `ai_results` ahora persiste `case_type`, `status`, `final_category`; el catálogo de tiempos vive en la tabla `catalogo_tiempos`.
  - El export a Excel incluye columnas de IA: `Descripción IA`, `Tiempo Estimado (min)`, `Tiempo Estimado (horas)`.
- `backend/DATABASE.md`: agregadas tablas `catalogo_tiempos` y `ai_results` (con campos reales).

### Archivos modificados (8):
1. `README.md` (raíz)
2. `docs/00_changelog.md`
3. `docs/00_prompt_desarrolladores.md`
4. `docs/00_fase0_alineacion_contratos.md`
5. `docs/03_desarrollo/01_estructura_y_convenciones.md`
6. `docs/08_api/contratos_api.md`
7. `docs/04_modulos/ia_service/ia_service.md`
8. `backend/DATABASE.md`

---

## [2026-09-04] Processing por archivo (parte del procesamiento de casos)

### Cambio de modelo de datos operativo
- **Un `processing_id` por archivo:** `POST /api/v1/uploads` ahora crea el `ProcessingModel` del archivo (status `pending`, `total_cases`) y devuelve `upload_id` + `processing_id` (antes solo `upload_id`).
- `POST /api/v1/ai/process-responsible` reutiliza el processing del archivo (ya no crea uno nuevo) y **acumula** los resultados de todos los responsables bajo ese mismo `processing_id`. Solo procesa los casos del responsable indicado.
- Se fijan `started_at` / `completed_at` en el processing (antes nunca se llenaban).
- `GET /api/v1/ai/results/{processing_id}`: `responsible_name` ahora es opcional (el processing es a nivel archivo).

### Herramienta de limpieza
- Nuevo script `backend/scripts/clear_uploads.py`: elimina `ai_results`, `estimations`, `processing_rejections`, `processings`, `cases`, `uploads` y **conserva** `catalogo_tiempos`.
- Se ejecutó para limpiar los datos de prueba existentes (14 uploads, 9 842 casos, 22 processings, 97 resultados).

### Archivos modificados:
1. `backend/app/api/routes/uploads.py`
2. `backend/app/api/schemas/upload.py`
3. `backend/app/api/routes/ai.py`
4. `backend/app/api/schemas/ai.py`
5. `backend/scripts/clear_uploads.py` (nuevo)
6. `README.md`

---

## [2026-09-07] Agrupación de resultados por Área (API)

### Cambio
- Se mapea la columna **`Area`** del Maestro de Casos (opcional) a un nuevo campo `area`.
- Cada resultado de IA (`AIResultResponse`) ahora incluye `area` (obtenido del caso vía el join existente `ai_results.case`).
- `ProcessingSummary` ahora incluye **`by_area`**: dict `{ area: {count, hours} }` (casos sin área van a `Sin área`).
- Las respuestas incluyen **`results_by_area`**: dict `{ área: [AIResultResponse, ...] }` con todos los casos de cada área.
- Aplica a `GET /api/v1/ai/results/{processing_id}` y a la respuesta de `POST /api/v1/ai/process-responsible`.
- **Solo API:** el export a Excel no cambia (los resultados se mostrarán en el frontend).

### Persistencia
- `CaseModel` ganó la columna `area` (String(200), nullable) — migración Alembic `006_add_area_to_cases`.
- La entidad de dominio `Case` y el `SQLAlchemyCaseRepository` (save/save_batch/update/_to_entity) ahora manejan `area`.
- El pipeline de Excel mapea `Area` en `ColumnMapper`, `StructureValidator` (opcional), `DataExtractor` y `ExcelCaseDTO`.

### Archivos modificados:
1. `backend/app/infrastructure/excel/column_mapper.py`
2. `backend/app/infrastructure/excel/structure_validator.py`
3. `backend/app/infrastructure/excel/data_extractor.py`
4. `backend/app/infrastructure/excel/case_mapper.py`
5. `backend/app/domain/entities/case.py`
6. `backend/app/infrastructure/repositories/case_repository.py`
7. `backend/app/infrastructure/database/models/case.py`
8. `backend/alembic/versions/006_add_area_to_cases.py` (nuevo)
9. `backend/app/api/routes/uploads.py`
10. `backend/app/api/schemas/ai.py`
11. `backend/app/api/routes/ai.py`
12. `backend/app/infrastructure/repositories/ai_result_repository.py` (joinedload de `case`)
13. `backend/tests/unit/excel/test_column_mapper.py`
