**Proyecto:** BOT-COMProject

**Versión:** 1.2

**Estado:** Definido

**Tipo:** Contrato de datos

---

# 1. Objetivo

Definir la estructura oficial del objeto `Case` utilizado por BOT-COMProject para representar un caso proveniente del Maestro de Casos de Aranda.

Este documento establece:

- Qué información representa un `Case`.
- Qué campos posee.
- Qué campos son obligatorios.
- Qué campos son opcionales.
- El origen de cada campo.
- La diferencia entre información original e información generada.
- Las reglas de normalización permitidas.
- La información utilizada por los módulos posteriores.
- La relación entre `Case`, `Upload` y `Processing`.

Este documento define el **contrato de datos del caso**.

No define:

- Reglas de negocio detalladas.
- Estados procesables.
- Rangos de tiempo.
- Reglas de estimación.
- Comportamiento interno de la IA.
- Persistencia física.
- Endpoints.
- Formato de exportación.

---

# 2. Alcance

El `Case Contract` será utilizado principalmente entre:

```
Excel Service
      ↓
Gestión de Casos
      ↓
Case Repository
      ↓
Estimation Engine
```

También será referencia para:

- Validaciones.
- Persistencia.
- Construcción del contexto para estimación.
- Construcción del contexto autorizado para IA.
- Pruebas unitarias.
- Pruebas de integración.
- Serialización y deserialización.

---

# 3. Concepto de Case

Un `Case` representa la **información original de un caso proveniente del Maestro de Casos de Aranda**.

El `Case` no representa una ejecución.

Tampoco representa:

- Una estimación.
- Una respuesta de IA.
- Un rechazo.
- Un procesamiento.

Conceptualmente:

```
Case
    =
Información original del caso
```

Mientras que:

```
Processing
    =
Ejecución sobre uno o varios casos
```

Y:

```
Estimation
    =
Resultado final de estimación
```

```
AIResult
    =
Resultado generado por IA
```

```
ProcessingRejection
    =
Resultado de rechazo dentro de una ejecución
```

---

# 4. Estructura Conceptual

El objeto lógico de `Case` será:

```
{
  "id": "UUID",
  "upload_id": "UUID",
  "case_code": "INC001245",
  "responsible_name": "Carlos Rodríguez",
  "responsible_id": "UUID",
  "user_name": "Juan Pérez",
  "project": "Hospital Militar",
  "registered_at": "2026-08-10",
  "status": "Solucionado",
  "final_category": "Ingreso de Huella",
  "description": "Descripción original del caso",
  "solution": "Solución registrada en Aranda",
  "created_at": "2026-08-16T14:00:00"
}
```

> `id`, `responsible_id` y `created_at` son información interna del sistema y no provienen directamente del Excel.
> 

---

# 5. Definición de Campos

| Campo | Tipo | Longitud | Obligatorio | Origen | Descripción |
| --- | --- | --- | --- | --- | --- |
| `id` | UUID | 36 | Sí | Sistema | Identificador interno |
| `upload_id` | UUID | 36 | Sí | Sistema | Upload del cual proviene |
| `case_code` | String | 50 | Sí | Excel | Código original del caso |
| `responsible_name` | String | 200 | Sí | Excel | Responsable original de Aranda |
| `responsible_id` | UUID | 36 | No | Sistema | Referencia al catálogo de responsables |
| `user_name` | String | 200 | No | Excel | Usuario asociado |
| `project` | String | 200 | Sí | Excel | Proyecto asociado |
| `registered_at` | DateTime | - | Sí | Excel | Fecha del caso |
| `status` | String | 100 | Sí | Excel | Estado original |
| `final_category` | String | 200 | Sí | Excel | Categoría final |
| `description` | Text | - | Sí | Excel | Descripción original |
| `solution` | Text | - | Sí | Excel | Solución original |
| `created_at` | DateTime | - | Sí | Sistema | Fecha de persistencia |

### 5.1 Formato de fechas

Todos los campos DateTime deberán almacenarse en formato ISO 8601:
- `registered_at`: Solo fecha → `YYYY-MM-DD`
- `created_at`: Fecha y hora → `YYYY-MM-DDTHH:MM:SS`

**Zona horaria:** UTC para todos los campos de tipo DateTime.

---

# 6. Identificador del Case

Existen dos identificadores diferentes.

## 6.1 Identificador interno

```
Case.id
```

Es el identificador único de la entidad dentro del sistema.

No proviene de Aranda.

---

## 6.2 Identificador funcional

```
Case.case_code
```

Representa el código original del caso proveniente de Aranda.

Ejemplo:

```
INC001245
```

El `case_code` permite identificar funcionalmente el caso.

Sin embargo, **no reemplaza a `Case.id` como identificador interno de persistencia**.

---

# 7. Identificación dentro de un Upload

Un caso se identifica dentro de una carga mediante:

```
upload_id
+
case_code
```

Por lo tanto:

```
UNIQUE(upload_id, case_code)
```

Una misma referencia `case_code` puede existir en diferentes `Upload`.

Ejemplo:

```
Upload A + INC001245
Upload B + INC001245
```

Son registros diferentes.

---

# 8. Upload de Origen

Todo `Case` deberá pertenecer a un `Upload`.

La relación será:

```
Upload 1 ───── N Case
```

Mediante:

```
Case.upload_id
```

El `Case` no deberá existir sin un `Upload` de origen.

Esto permite determinar:

```
Case
  ↓
Upload
  ↓
Archivo original
```

---

# 9. Responsable Original

El campo:

```
responsible_name
```

representa exclusivamente el valor original obtenido del Maestro de Casos.

Ejemplo:

```
"Carlos Rodríguez"
```

Este valor deberá conservarse.

No deberá reemplazarse por el nombre proveniente del catálogo.

---

# 10. Referencia al Catálogo de Responsables

El campo:

```
responsible_id
```

representa una referencia interna al catálogo de responsables.

Por lo tanto:

```
responsible_name
        ↓
Dato original de Aranda
```

mientras:

```
responsible_id
        ↓
Referencia interna al catálogo
```

La existencia de `responsible_id` no implica que el responsable haya sido seleccionado para ejecutar un `Processing`.

---

# 11. Responsable del Processing

El responsable seleccionado para ejecutar una operación se representa exclusivamente mediante:

```
Processing.responsible_id
```

Por lo tanto existen dos conceptos:

```
Case.responsible_id
        ↓
Responsable asociado originalmente al caso
```

y:

```
Processing.responsible_id
        ↓
Responsable seleccionado para ejecutar el procesamiento
```

No deberán confundirse ambos conceptos.

---

# 12. Usuario

El campo:

```
user_name
```

representa el usuario asociado al caso en Aranda.

Este campo:

- Forma parte del contexto original.
- Puede ser utilizado por etapas posteriores.
- No determina por sí mismo si el caso es procesable.

El campo podrá ser `NULL`.

---

# 13. Proyecto

El campo:

```
project
```

representa el proyecto asociado al caso.

Ejemplo:

```
Hospital Militar
```

Es información original proveniente de Aranda y deberá conservarse.

---

# 14. Fecha de Registro

El campo:

```
registered_at
```

representa la fecha de registro del caso en el sistema origen.

Debe almacenarse como:

```
DateTime
```

La representación para intercambio podrá utilizar formatos como:

```
YYYY-MM-DD
```

cuando solamente sea necesaria la fecha.

---

# 15. Estado

El campo:

```
status
```

representa exclusivamente el estado original proveniente de Aranda.

Ejemplos:

```
Solucionado
Cerrado
```

El `Case Contract` no determina qué estados son procesables.

La responsabilidad corresponde a:

```
Catalog Service
      ↓
Catálogo de Estados
```

Por lo tanto:

```
Case.status
```

no deberá confundirse con:

```
Processing.status
```

---

# 16. Categoría Final

El campo:

```
final_category
```

representa exclusivamente la categoría final registrada en el Maestro de Casos.

Ejemplo:

```
Ingreso de Huella
```

No representa:

- Categorías anteriores.
- Subcategorías.
- Rangos de tiempo.
- Configuraciones del catálogo.

La configuración asociada a esta categoría pertenece al:

```
Catálogo de Tiempos
```

---

# 17. Categoría Final vs Categoría Configurada

El `Case` contiene:

```
final_category
```

pero no contiene:

```
minimum_minutes
maximum_minutes
```

La relación conceptual es:

```
Case.final_category
        ↓
Catalog Service
        ↓
Catálogo de Tiempos
        ↓
Configuración activa
        ↓
Estimation Engine
```

Por lo tanto, la categoría configurada **no forma parte del Case original**.

---

# 18. Descripción

El campo:

```
description
```

contiene la descripción original registrada en Aranda.

Puede utilizarse como contexto para:

- Gestión de Casos.
- Estimation Engine.
- AI Service.

La información generada posteriormente por IA deberá almacenarse independientemente.

Nunca:

```
AIResult.generated_description
        ↓
Case.description
```

---

# 19. Solución

El campo:

```
solution
```

contiene la solución original registrada en Aranda.

Puede utilizarse como contexto para etapas posteriores.

La IA no podrá modificar ni sobrescribir este valor.

El campo podrá ser `NULL`.

---

# 20. Información Original

La información original del caso comprende:

```
case_code
responsible_name
user_name
project
registered_at
status
final_category
description
solution
```

Estos datos deberán conservarse sin perder su trazabilidad con el origen.

---

# 21. Información Interna del Sistema

El sistema podrá agregar información necesaria para persistencia y trazabilidad:

```
id
upload_id
responsible_id
created_at
```

Estos campos no representan información generada por IA.

---

# 22. Información Generada por el Procesamiento

El resultado del procesamiento **no forma parte de la entidad `Case`**.

Los resultados deberán mantenerse separados mediante:

```
AIResult
Estimation
ProcessingRejection
```

Por ejemplo:

```
Case
 │
 ├── Información original
 │
 └── No contiene:
       ├── tiempo estimado
       └── descripción generada
```

Mientras:

```
Processing
      │
      ├── AIResult
      │
      ├── Estimation
      │
      └── ProcessingRejection
```

---

# 23. Case Normalizado

Antes de aplicar las reglas de negocio, los valores del caso podrán pasar por:

```
Case Normalizer
```

Ejemplo:

```
Original:
"  Carlos Rodríguez  "

Normalizado:
"Carlos Rodríguez"
```

La normalización podrá realizar:

- Eliminación de espacios innecesarios.
- Normalización de texto.
- Normalización de fechas.
- Estandarización de valores vacíos.
- Normalización de nombres.
- Normalización de formatos.

La normalización **no podrá alterar el significado del dato original**.

---

# 24. Conservación del Dato Original

La normalización no deberá interpretarse como autorización para destruir el valor original proveniente de Aranda.

Cuando el sistema necesite conservar una representación normalizada para procesamiento, deberá poder distinguir conceptualmente:

```
Dato original
```

de:

```
Dato normalizado
```

El mecanismo concreto de persistencia de ambas representaciones será responsabilidad del diseño de persistencia y no de este contrato.

---

# 25. Validación del Case

El `Case Validator` deberá comprobar como mínimo la presencia y formato de los campos definidos como obligatorios.

Campos obligatorios:

```
case_code
responsible_name
project
registered_at
status
final_category
description
solution
```

Los campos:

```
user_name
responsible_id
```

podrán ser opcionales según el Modelo de Datos y el contexto de procesamiento.

La validación estructural no determina:

```
¿El estado es procesable?
```

ni:

```
¿La categoría está configurada?
```

Estas decisiones pertenecen a `Catalog Service` y a las reglas de Gestión de Casos.

---

# 26. Case Procesable

El `Case Contract` no determina por sí solo si un caso es procesable.

La determinación corresponde a:

```
Gestión de Casos
       ↓
Catalog Service
       ↓
Reglas de negocio
```

Conceptualmente:

```
Case
 │
 ├── Datos estructuralmente válidos
 │
 ├── Responsable correspondiente
 │
 ├── Estado procesable
 │
 └── Categoría configurada
          │
          ▼
     Caso procesable
```

---

# 27. Relación con Processing

Un `Case` puede participar en múltiples ejecuciones.

```
Case
 │
 ├── Processing 1
 ├── Processing 2
 └── Processing 3
```

Por lo tanto, el `Case` no deberá contener:

```
processing_id
```

La relación se establece mediante las entidades de resultado:

```
Processing
     │
     ├── Estimation
     ├── AIResult
     └── ProcessingRejection
```

Esto permite mantener el mismo caso original y registrar diferentes ejecuciones.

---

# 28. Contexto para Estimation Engine

El `Case Context Builder` podrá construir una representación específica para el `Estimation Engine`.

Ejemplo:

```
{
  "case_code": "INC001245",
  "responsible_name": "Carlos Rodríguez",
  "project": "Hospital Militar",
  "final_category": "Ingreso de Huella",
  "description": "Descripción original",
  "solution": "Solución registrada",
  "status": "Solucionado"
}
```

Este objeto:

```
NO ES un nuevo Case
```

Es únicamente un contexto de procesamiento.

---

# 29. Contexto para AI Service

El `AI Service` no deberá recibir necesariamente toda la entidad `Case`.

El contexto deberá ser construido por el flujo correspondiente y contener únicamente la información autorizada.

Conceptualmente:

```
Case
 ↓
Case Context Builder
 ↓
Contexto autorizado
 ↓
AI Service
 ↓
AIResult
```

El `AI Service` no deberá modificar el `Case`.

---

# 30. Resultado del Procesamiento

Los resultados deberán mantenerse separados del `Case`.

Ejemplo conceptual:

```
Case
 │
 ├── case_code
 ├── description
 └── solution
 │
 ▼
Processing
 │
 ├── AIResult
 │     ├── estimated_minutes
 │     ├── generated_description
 │     └── model_name
 │
 └── Estimation
       ├── estimated_minutes
       ├── minimum_minutes
       ├── maximum_minutes
       └── status
```

Si el caso no puede continuar:

```
Processing
      │
      └── ProcessingRejection
```

---

# 31. Reglas del Contrato

### CC-01 — Identificador interno

Todo `Case` deberá poseer un `id` único.

### CC-02 — Código funcional

Todo `Case` deberá poseer un `case_code`.

### CC-03 — Upload obligatorio

Todo `Case` deberá pertenecer a un `Upload`.

### CC-04 — Responsable original

Todo `Case` deberá conservar `responsible_name` proveniente de Aranda.

### CC-05 — Proyecto obligatorio

Todo `Case` deberá contener `project`.

### CC-06 — Estado obligatorio

Todo `Case` deberá contener `status`.

### CC-07 — Categoría final obligatoria

Todo `Case` deberá contener `final_category`.

### CC-08 — Fecha obligatoria

Todo `Case` deberá contener `registered_at`.

### CC-09 — Responsable de catálogo

`responsible_id` representa una referencia interna y no reemplaza `responsible_name`.

### CC-10 — Identificación por Upload

La unicidad funcional dentro de una carga se determinará mediante:

```
upload_id + case_code
```

### CC-11 — Información original

Los datos provenientes de Aranda deberán conservarse.

### CC-12 — No sobrescritura

La IA no podrá modificar la información original del `Case`.

### CC-13 — Separación de resultados

`AIResult`, `Estimation` y `ProcessingRejection` no forman parte del objeto original `Case`.

### CC-14 — No procesamiento en Case

`Case` no deberá contener `processing_id`.

### CC-15 — Múltiples ejecuciones

Un mismo `Case` podrá participar en diferentes `Processing`.

### CC-16 — Normalización

Los datos podrán normalizarse siempre que no se altere su significado.

### CC-17 — Estado

`Case.status` representa exclusivamente el estado original de Aranda.

### CC-18 — Responsable de ejecución

El responsable seleccionado para una ejecución se representa mediante:

```
Processing.responsible_id
```

### CC-19 — Categoría

`final_category` representa únicamente la categoría final proveniente del Maestro.

### CC-20 — Contrato estable

Los módulos consumidores deberán utilizar este contrato y no depender directamente de la estructura física del Excel.

---

# 32. Dependencias

El contrato será utilizado por:

```
Excel Service
      ↓
Gestión de Casos
      ↓
Case Repository
      ↓
Estimation Engine
```

Y proporcionará información de contexto a:

```
AI Service
```

mediante el flujo definido por los módulos correspondientes.

# 33. Responsabilidades por Componente

| Componente | Responsabilidad |
| --- | --- |
| Excel Service | Extraer información desde Excel |
| Case Normalizer | Normalizar valores |
| Case Validator | Validar estructura |
| Case Filter | Aplicar reglas de procesamiento |
| Catalog Service | Consultar catálogos |
| Case Context Builder | Construir contexto |
| Case Repository | Persistir y recuperar `Case` |
| Estimation Engine | Generar/validar estimación |
| AI Service | Generar resultados de IA |
| Export Service | Presentar/exportar resultados |

---

# 34. Exclusiones

El `Case Contract` no define:

- Estados procesables.
- Rangos de tiempo.
- Reglas de estimación.
- Prompts.
- Reglas internas de IA.
- Catálogo de responsables.
- Persistencia física.
- Endpoints.
- Exportación.
- Integración con COMProject.
- Reglas de rechazo.
- Lógica de procesamiento.

---

# 35. Principios

El contrato deberá cumplir:

- Claridad.
- Estabilidad.
- Consistencia.
- Trazabilidad.
- Independencia del Excel.
- Independencia de la IA.
- Separación entre información original y generada.
- Testabilidad.
- Compatibilidad con Clean Architecture.

---

# 36. Consistencia Documental

Este documento deberá mantenerse alineado con:

| Documento | Relación |
| --- | --- |
| Project Charter | Alcance general |
| Business Process Analysis | Flujo de negocio |
| Catálogo de Estados | Estados procesables |
| Catálogo de Tiempos | Categorías y rangos |
| Catálogo de Responsables | Responsables |
| Mapa de Módulos | Responsabilidades |
| Gestión de Casos | Validación y filtrado |
| Estimation Engine | Estimación |
| AI Service | Procesamiento mediante IA |
| Modelo de Datos | Persistencia |
| API Contract | Exposición de información |

---

# 37. Regla de Evolución

Cualquier modificación a la estructura de `Case` deberá analizar su impacto sobre:

```
Case Contract
      ↓
Excel Service
      ↓
Gestión de Casos
      ↓
Case Repository
      ↓
Estimation Engine
      ↓
AI Service
      ↓
Modelo de Datos
      ↓
API Contract
      ↓
Exportación
```

Ningún módulo podrá modificar unilateralmente el contrato.

---

# 38. Decisiones de la Versión 1.2

### CCC-01 — Case representa información original

`Case` representa el caso proveniente de Aranda y no una ejecución.

### CCC-02 — Identificador interno

El identificador interno será:

```
Case.id
```

### CCC-03 — Identificador funcional

El código de Aranda será:

```
Case.case_code
```

### CCC-04 — Upload obligatorio

Todo caso deberá estar asociado al `Upload` de origen.

### CCC-05 — Responsable original y responsable de ejecución

Se diferencian:

```
Case.responsible_name
Case.responsible_id
Processing.responsible_id
```

### CCC-06 — Separación de resultados

Los resultados generados no forman parte de `Case`.

### CCC-07 — Múltiples ejecuciones

Un mismo `Case` puede participar en múltiples `Processing`.

### CCC-08 — Categoría final

`final_category` representa únicamente la categoría final proveniente de Aranda.

### CCC-09 — Preservación

Los datos originales no podrán ser sobrescritos por la IA.

### CCC-10 — Trazabilidad

Debe ser posible recorrer:

```
Upload
   ↓
Case
   ↓
Processing
   ↓
AIResult / Estimation / ProcessingRejection
```

---

# 39. Control de Versión

| Versión | Estado | Cambios principales |
| --- | --- | --- |
| 1.0 | En construcción | Contrato inicial |
| 1.1 | Definido | Incorporación de validaciones, normalización y contexto |
| **1.2** | **Definido** | Alineación con Modelo de Datos 1.2, separación `Case/Processing`, `Case.id` vs `case_code`, `upload_id`, `responsible_id`, separación de resultados IA/estimación y actualización de campos obligatorios/opcionales |