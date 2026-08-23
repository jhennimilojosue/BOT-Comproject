**Proyecto:** BOT-COMProject

**Versión:** 1.3

**Estado:** Definido

---

# 1. Objetivo

El módulo **Gestión de Casos** es responsable de administrar y preparar los casos obtenidos del Maestro de Casos para que puedan continuar hacia el proceso de estimación.

Sus responsabilidades principales son:

- Recibir los casos obtenidos desde `Excel Service`.
- Normalizar la información.
- Validar la estructura mínima requerida.
- Filtrar los casos según el responsable seleccionado.
- Validar los estados procesables mediante `Catalog Service`.
- Validar la existencia y configuración activa de la categoría final.
- Identificar casos que no pueden continuar.
- Registrar los motivos de rechazo.
- Evitar duplicidades dentro de una ejecución.
- Construir el contexto requerido por `Estimation Engine`.
- Mantener la trazabilidad entre `Upload`, `Processing` y `Case`.
- Coordinar la persistencia de los casos y resultados mediante repositorios.

El módulo **no calcula tiempos**, **no utiliza directamente la IA** y **no registra información en COMProject**.

Las reglas relacionadas con catálogos deberán consultarse exclusivamente mediante `Catalog Service`.

---

# 2. Responsabilidades

El módulo será responsable de:

1. Recibir los casos procesados por `Excel Service`.
2. Normalizar la información recibida.
3. Validar los datos estructurales obligatorios.
4. Recibir el responsable seleccionado para la ejecución.
5. Validar el responsable mediante `Catalog Service`.
6. Asociar la ejecución con el responsable seleccionado.
7. Filtrar los casos correspondientes al responsable seleccionado.
8. Validar los estados procesables mediante `Catalog Service`.
9. Validar la existencia de una categoría final.
10. Validar mediante `Catalog Service` que la categoría esté configurada y activa.
11. Identificar casos que no puedan continuar.
12. Registrar el motivo correspondiente mediante `ProcessingRejection`.
13. Preparar los casos procesables para `Estimation Engine`.
14. Mantener la trazabilidad con el `Processing` correspondiente.
15. Evitar que un mismo `Case` genere resultados contradictorios dentro de una ejecución.
16. Utilizar `Case Repository` para consultar y persistir información.
17. Participar en la actualización de los contadores de la ejecución.

El módulo **no deberá acceder directamente a PostgreSQL**.

---

# 3. Conceptos principales

Para evitar ambigüedad se establecen los siguientes conceptos.

## 3.1 Case

Representa el caso original obtenido del Maestro de Casos.

```
Case
=
Información original de Aranda
```

El módulo no deberá modificar la información original para representar resultados generados posteriormente.

---

## 3.2 Processing

Representa una ejecución concreta del sistema sobre un `Upload`.

```
Upload
   ↓
Processing
   ↓
Casos de la ejecución
```

Cada ejecución deberá poseer un `processing_id`.

---

## 3.3 Caso candidato

Es un `Case` perteneciente al `Upload` asociado al `Processing` que entra en el ámbito de evaluación de la ejecución.

Un caso candidato todavía no implica que pueda ser procesado.

---

## 3.4 Caso procesable

Es un caso candidato que supera todas las validaciones necesarias para continuar hacia `Estimation Engine`.

---

## 3.5 Caso rechazado

Es un caso candidato que no puede continuar dentro de la ejecución.

El rechazo deberá registrarse mediante:

```
ProcessingRejection
```

El rechazo pertenece al contexto de una ejecución específica.

Por lo tanto:

```
Case
   +
Processing
   ↓
ProcessingRejection
```

---

# 4. Concepto de Categoría

El módulo trabajará exclusivamente con la **categoría final presente en el Excel**.

## 4.1 Categoría final

Es la categoría registrada originalmente en el Maestro de Casos.

Ejemplo:

```
Ingreso de Huella
```

Este valor deberá conservarse en:

```
Case.final_category
```

---

## 4.2 Categoría configurada

Una categoría final será considerada configurada cuando exista una configuración activa en el Catálogo de Tiempos.

```
Categoría final
      ↓
Catalog Service
      ↓
Configuración activa
```

---

## 4.3 Categoría no configurada

Si la categoría no tiene configuración activa:

```
Categoría final
      ↓
Catalog Service
      ↓
Sin configuración activa
      ↓
ProcessingRejection
```

El caso no podrá continuar hacia `Estimation Engine`.

---

# 5. Entradas

## 5.1 Desde Excel Service

El módulo recibirá casos normalizados que contengan, como mínimo:

- Código del caso.
- Responsable original.
- Usuario.
- Proyecto.
- Fecha de registro.
- Estado.
- Categoría final.
- Descripción.
- Solución.

---

## 5.2 Desde la ejecución

El módulo recibirá:

```
upload_id
responsible_id
processing_id
```

Donde:

- `upload_id` identifica el archivo cargado.
- `responsible_id` identifica el responsable seleccionado.
- `processing_id` identifica la ejecución actual.

El `Processing` deberá existir antes de generar resultados asociados a la ejecución.

---

# 6. Salidas

El módulo generará dos resultados principales.

## 6.1 Casos procesables

Casos que cumplen las condiciones necesarias para continuar:

```
Case
 ↓
Validaciones
 ↓
Procesable
 ↓
Estimation Engine
```

---

## 6.2 Casos rechazados

Casos que no pueden continuar:

```
Case
 ↓
Validación
 ↓
No procesable
 ↓
ProcessingRejection
```

Cada rechazo deberá conservar:

- `processing_id`
- `case_id`
- `reason_code`
- `message`
- `created_at`

---

# 7. Flujo general

El flujo será:

```
Upload
   │
   ▼
Excel Service
   │
   ▼
Case Normalizer
   │
   ▼
Case Validator
   │
   ▼
Case Filter
   │
   ├──────────────► Catalog Service
   │
   ▼
Caso procesable / rechazado
   │
   ├──────────────► ProcessingRejection
   │
   ▼
Case Context Builder
   │
   ▼
Estimation Engine
```

La ejecución será representada por:

```
Processing
```

y todos los resultados deberán quedar asociados a ella.

---

# 8. Case Normalizer

## Responsabilidad

Estandarizar los datos recibidos desde `Excel Service`.

## Funciones

- Eliminar espacios innecesarios.
- Normalizar valores de texto.
- Normalizar fechas.
- Estandarizar valores vacíos.
- Normalizar nombres de responsables.
- Normalizar categorías.
- Estandarizar valores necesarios para las comparaciones.

El normalizador **no aplica reglas de negocio**.

### Regla

La normalización no deberá modificar el significado del dato original almacenado en `Case`.

---

# 9. Case Validator

## Responsabilidad

Validar la estructura mínima necesaria del caso.

Deberá verificar:

- Código existente.
- Responsable original existente.
- Proyecto existente.
- Fecha válida.
- Estado definido.
- Categoría final existente.
- Información mínima necesaria para el procesamiento posterior.

Si una validación estructural falla:

```
Case
 ↓
Case Validator
 ↓
ProcessingRejection
```

El `Case Validator` no determinará si un estado o categoría son válidos según negocio.

Estas decisiones corresponden a `Catalog Service`.

---

# 10. Case Filter

## Responsabilidad

Determinar qué casos candidatos pueden continuar dentro del `Processing`.

No deberá contener directamente información de los catálogos.

Su comunicación será:

```
Case Filter
     ↓
Catalog Service
```

---

# 11. Validación del responsable

Antes de procesar los casos deberá existir un responsable seleccionado.

```
Usuario
   ↓
Responsible
   ↓
Processing.responsible_id
```

El responsable deberá:

1. Existir.
2. Estar activo.
3. Ser válido para la ejecución.

La validación deberá realizarse mediante `Catalog Service`.

El responsable seleccionado para la ejecución **no deberá confundirse con el responsable original del caso**.

```
Case.responsible_name
        ↓
Dato original de Aranda
```

mientras:

```
Processing.responsible_id
        ↓
Responsable seleccionado para ejecutar
```

---

# 12. Filtrado por responsable

Una vez validado el responsable:

```
Case.responsible_name
        ↓
Comparación
        ↓
Responsable seleccionado
```

Solo los casos correspondientes al responsable seleccionado podrán continuar como candidatos.

Los casos pertenecientes a otros responsables no deberán ser procesados por esa ejecución.

---

# 13. Validación de estado

Los estados procesables deberán ser determinados mediante `Catalog Service`.

Para V1:

```
Solucionado
Cerrado
```

serán procesables.

Conceptualmente:

```
Estado
  │
  ├── Solucionado ──► Procesable
  │
  ├── Cerrado ──────► Procesable
  │
  └── Otro ─────────► Rechazado
```

La lista no deberá estar codificada directamente en `Case Filter`.

---

# 14. Validación de categoría

El módulo utilizará:

```
Case.final_category
```

para consultar:

```
Catalog Service
```

El servicio determinará si existe una configuración activa.

```
Categoría final
      ↓
Catalog Service
      ↓
¿Configurada?
   ┌──┴──┐
   │     │
  Sí     No
   │     │
   ▼     ▼
Continúa Rechazo
```

El módulo no accederá directamente al Catálogo de Tiempos.

---

# 15. Duplicidad dentro de Processing

Dentro de una misma ejecución:

```
Processing + Case
```

deberá representar un único contexto de procesamiento.

Un caso no deberá generar múltiples resultados finales válidos.

La persistencia deberá proteger esta condición mediante restricciones cuando sea técnicamente viable.

---

# 16. Exclusividad entre procesado y rechazado

Dentro de un mismo `Processing`, un `Case` no podrá tener simultáneamente:

```
Estimation válida
```

y:

```
ProcessingRejection
```

Por lo tanto:

```
Case + Processing
       │
       ├── Estimation
       └── NO Rejection
```

o:

```
Case + Processing
       │
       └── ProcessingRejection
```

pero no ambos.

Esta regla deberá ser garantizada principalmente por la capa de aplicación y reforzada mediante persistencia cuando sea viable.

---

# 17. Procesamiento parcial

Una ejecución podrá contener simultáneamente:

```
Casos procesados
+
Casos rechazados
```

Ejemplo:

```
Processing
   │
   ├── 85 procesados
   └── 35 rechazados
```

Por lo tanto:

```
Processing.status = COMPLETED
```

puede coexistir con:

```
processed_cases = 85
rejected_cases = 35
```

Un rechazo individual no implica un fallo técnico de toda la ejecución.

---

# 18. Contadores de Processing

El módulo deberá participar en la determinación de:

```
total_cases
processed_cases
rejected_cases
```

Cuando la ejecución finalice correctamente:

```
total_cases
=
processed_cases
+
rejected_cases
```

Un fallo técnico global que impida clasificar los casos no deberá convertirse artificialmente en rechazos de negocio.

En dicho escenario:

```
Processing.status = FAILED
```

---

# 19. ProcessingRejection

Los rechazos deberán estar asociados a la ejecución en la cual ocurrieron.

```
Processing
     │
     └── ProcessingRejection
                │
                └── Case
```

Códigos iniciales:

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

La lista definitiva deberá mantenerse alineada con los documentos oficiales de negocio.

---

# 20. Integridad Upload / Processing / Case

Todo caso procesado deberá pertenecer al mismo `Upload` asociado al `Processing`.

Debe cumplirse:

```
Processing.upload_id
        =
Case.upload_id
```

No será válido:

```
Processing A
     │
     └── Case perteneciente a Upload B
```

Esta validación deberá realizarse en la aplicación y reforzarse en persistencia cuando sea técnicamente viable.

---

# 21. Case Context Builder

El `Case Context Builder` construirá la información necesaria para `Estimation Engine`.

Ejemplo:

```
{
  "case_id": "uuid",
  "case_code": "INC001245",
  "responsible": "Carlos Rodríguez",
  "project": "Hospital Militar",
  "category": "Ingreso de Huella",
  "description": "...",
  "solution": "...",
  "status": "Solucionado"
}
```

El contexto deberá incluir únicamente información necesaria para la estimación.

No deberá:

- Calcular tiempos.
- Determinar rangos.
- Generar recomendaciones.
- Consultar Ollama directamente.

---

# 22. Persistencia

La persistencia deberá realizarse mediante repositorios.

```
Gestión de Casos
       │
       ▼
Case Repository
       │
       ▼
PostgreSQL
```

El módulo no accederá directamente a PostgreSQL.

Los repositorios deberán limitarse a operaciones de persistencia y consulta.

No deberán contener reglas de negocio del proceso.

---

# 23. Responsabilidades respecto a las entidades

El módulo deberá mantener la trazabilidad entre:

```
Upload
   ↓
Processing
   ↓
Case
   ↓
ProcessingRejection
```

Los resultados posteriores serán generados por las etapas correspondientes:

```
Case
   ↓
Estimation Engine
   ├── AIResult
   └── Estimation
```

Gestión de Casos no será responsable de generar `AIResult` ni `Estimation`.

---

# 24. Dependencias

### Consume

```
Excel Service
Catalog Service
Case Repository
Processing Repository
Processing Rejection Repository
```

### Entrega información a

```
Estimation Engine
```

### No se comunica directamente con

```
AI Service
COMProject
PostgreSQL
```

---

# 25. Reglas del Módulo

### RGC-01 — Caso inválido

Un caso que no cumpla las validaciones estructurales no podrá continuar.

### RGC-02 — Responsable obligatorio

Debe existir un responsable seleccionado antes de iniciar el procesamiento.

### RGC-03 — Responsable válido

El responsable deberá existir y estar activo.

### RGC-04 — Filtrado por responsable

Solo los casos correspondientes al responsable seleccionado serán candidatos.

### RGC-05 — Estados procesables

Los estados procesables serán determinados por `Catalog Service`.

### RGC-06 — Categoría obligatoria

Todo caso candidato deberá contener categoría final.

### RGC-07 — Categoría configurada

La categoría deberá contar con configuración activa.

### RGC-08 — Catálogos centralizados

El módulo no accederá directamente a los catálogos.

### RGC-09 — No duplicidad

Un `Case` no podrá producir múltiples resultados finales válidos dentro del mismo `Processing`.

### RGC-10 — Sin estimación

Gestión de Casos no calcula tiempos.

### RGC-11 — Sin IA directa

Gestión de Casos no consulta directamente el `AI Service`.

### RGC-12 — Sin COMProject

Gestión de Casos no interactúa directamente con COMProject.

### RGC-13 — Motivo de rechazo

Todo caso rechazado deberá registrar su motivo.

### RGC-14 — Procesamiento parcial

Los rechazos individuales no deberán impedir necesariamente el procesamiento de casos válidos.

### RGC-15 — Integridad de carga

Todo `Case` procesado deberá pertenecer al `Upload` del `Processing`.

### RGC-16 — Exclusividad de resultado

Un `Case + Processing` no podrá tener simultáneamente una estimación final válida y un rechazo.

### RGC-17 — Trazabilidad

Todo rechazo deberá poder determinar:

```
Upload
Processing
Case
Reason
```

### RGC-18 — Contadores

Una ejecución completada deberá cumplir:

```
total_cases
=
processed_cases
+
rejected_cases
```

# 26. Principios de Diseño

El módulo deberá cumplir:

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Inversión de dependencias.
- Separación dominio/infraestructura.
- Testabilidad.
- Validaciones deterministas.
- Reglas de negocio centralizadas.
- No dependencia directa de IA.
- No dependencia directa de COMProject.
- No acceso directo a PostgreSQL.
- Uso de interfaces para dependencias externas.
- Trazabilidad de cada ejecución.

---

# 27. Exclusiones

Gestión de Casos **no será responsable de**:

- Calcular tiempos.
- Consultar Ollama.
- Generar descripciones mediante IA.
- Registrar horas en COMProject.
- Exportar archivos.
- Modificar catálogos.
- Crear reglas de negocio de catálogos.
- Determinar rangos de tiempo.
- Acceder directamente a PostgreSQL.
- Generar `AIResult`.
- Generar `Estimation`.

---

# 28. Evolución futura

Podrá evolucionar para soportar:

- Detección avanzada de duplicados históricos.
- Auditoría.
- Nuevos criterios de filtrado.
- Nuevos tipos de responsables.
- Nuevos estados procesables.
- Nuevas validaciones.
- Reprocesamiento avanzado.
- Historial detallado de resultados.

Estas funcionalidades no forman parte de V1.

No deberán incorporarse entidades o responsabilidades anticipadamente.

---

# 29. Consistencia Documental

Este documento deberá mantenerse alineado con:

| Documento | Relación |
| --- | --- |
| Project Charter | Alcance general |
| Business Process Analysis | Flujo de negocio |
| Glosario | Terminología oficial |
| Catálogo de Estados | Estados procesables |
| Catálogo de Tiempos | Categorías y rangos |
| Catálogo de Responsables | Responsables disponibles |
| Case Contract | Estructura de Case |
| Modelo de Datos | Persistencia |
| Mapa de Módulos | Responsabilidades |
| Estimation Engine | Proceso posterior |
| API Contract | Identificación de Upload/Processing/Results |

---

# 30. Fuente de verdad

Este documento define específicamente:

- Responsabilidades de Gestión de Casos.
- Flujo interno del módulo.
- Validaciones estructurales.
- Uso de catálogos.
- Filtrado.
- Preparación de casos.
- Manejo de rechazos.
- Integración con `Processing`.
- Límites del módulo.

No define:

- Rangos de tiempo.
- Reglas detalladas de estimación.
- Comportamiento interno de IA.
- Estructura de API.
- Persistencia completa.

Estas definiciones pertenecen a sus respectivos documentos.

---

# 31. Decisiones de la versión 1.3

Las reglas de negocio del módulo Gestión de Casos (MGC-01 a MGC-20) están definidas en:

```
04_modulos/gestion_casos/modelo_datos_modulo.md
```

Este documento (`gestion_casos.md`) define el comportamiento del módulo, mientras que `modelo_datos_modulo.md` define las reglas de negocio, el modelo de datos y las validaciones.

```
Upload
   ↓
Processing
   ↓
Case
   ↓
Resultado / Rechazo
```

---

# 32. Control de versión

| Versión | Estado | Cambios |
| --- | --- | --- |
| 1.0 | En construcción | Definición inicial del módulo |
| 1.1 | Definido | Incorporación de filtrado, catálogos y procesamiento parcial |
| 1.2 | Definido | Separación de categorías, uso de Catalog Service y Case Repository |
| **1.3** | **Definido** | Integración explícita con `Processing`, `ProcessingRejection`, trazabilidad `Upload/Processing/Case`, procesamiento parcial, exclusividad procesado/rechazado, contadores y separación entre caso candidato, procesable y rechazado |