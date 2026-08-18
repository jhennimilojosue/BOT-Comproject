**Proyecto:** BOT-COMProject

**Versión:** 1.3

**Estado:** Definido / Cerrado V1

**Tipo:** Diseño de módulo

---

# 1. Objetivo

Definir el funcionamiento interno del módulo **Gestión de Casos**, responsable de recibir, normalizar, validar, filtrar y preparar los casos provenientes del Maestro de Casos de Aranda para su posterior procesamiento.

El módulo garantiza que únicamente los casos que cumplan las condiciones definidas por el negocio continúen hacia:

```
Case
  ↓
Estimation Engine
  ↓
AI Service
```

El módulo no es responsable de:

- Estimar tiempos.
- Generar descripciones profesionales mediante IA.
- Ejecutar prompts.
- Acceder directamente a PostgreSQL.
- Comunicarse directamente con COMProject.
- Exponer endpoints HTTP.
- Implementar la lógica interna del `Estimation Engine`.
- Implementar la lógica interna del `AI Service`.

---

# 2. Alcance

Gestión de Casos comprende las siguientes responsabilidades:

```
Entrada de Cases
       ↓
Normalización
       ↓
Validación estructural
       ↓
Filtrado por responsable
       ↓
Validación de estado
       ↓
Validación de categoría
       ↓
Control de duplicidad
       ↓
Clasificación
    ┌──┴──┐
    ↓     ↓
Procesable  Rechazado
```

El módulo será utilizado durante una ejecución representada por:

```
Processing
```

---

# 3. Posición dentro de la arquitectura

```
                    Frontend
                       │
                       ▼
                  API / Backend
                       │
                       ▼
              Application Service
                       │
                       ▼
             Gestión de Casos
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Normalizer      Validator        Filter
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Case procesable
                       │
                       ▼
              Estimation Engine
                       │
                       ▼
                  AI Service
```

Gestión de Casos forma parte de la capa de aplicación/dominio y no deberá contener detalles propios de infraestructura.

---

# 4. Entrada

La entrada principal será un conjunto de objetos `Case` provenientes del `Excel Service`.

El módulo **no dependerá directamente de la estructura del Excel**.

Flujo:

```
Maestro Aranda
      ↓
Excel Service
      ↓
Case Contract
      ↓
Gestión de Casos
```

El Excel Service será responsable de transformar la información del archivo al contrato `Case`.

---

# 5. Contrato Case utilizado por el módulo

El módulo trabajará con el siguiente modelo canónico:

```
{
  "case_code": "INC001245",
  "responsible_name": "Carlos Rodríguez",
  "user_name": "Juan Pérez",
  "project": "Hospital Militar",
  "registered_at": "2026-08-10T14:30:00",
  "status": "Solucionado",
  "final_category": "Ingreso de Huella",
  "description": "Descripción original del caso",
  "solution": "Solución registrada en Aranda"
}
```

Los nombres definidos aquí serán los nombres oficiales utilizados internamente.

---

# 6. Componentes internos

El módulo estará compuesto por:

```
Case Management
│
├── Case Normalizer
│
├── Case Validator
│
├── Case Filter
│
└── Case Context Builder
```

Cada componente tendrá una responsabilidad específica.

---

# 7. Case Normalizer

## 7.1 Responsabilidad

Normalizar los valores del `Case` antes de ejecutar las validaciones correspondientes.

Podrá realizar:

- Eliminación de espacios innecesarios.
- Normalización de textos.
- Normalización de fechas.
- Normalización de valores vacíos.
- Normalización de formatos.
- Conversión a tipos internos definidos por el contrato.

Ejemplo:

```
"  Carlos Rodríguez  "
          ↓
"Carlos Rodríguez"
```

---

## 7.2 Restricción

La normalización no podrá cambiar el significado del dato.

No podrá:

```
Modificar descripción
Modificar solución
Modificar categoría
Modificar estado
```

para intentar hacer que un caso sea procesable.

La normalización únicamente corrige representación y formato.

---

# 8. Case Validator

## 8.1 Responsabilidad

Validar que el `Case` cumpla el contrato definido antes de continuar con el procesamiento.

Los campos obligatorios serán:

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

Todos deberán contener información válida.

---

# 9. Validaciones del Case Validator

Como mínimo deberá comprobar:

### Identificación

```
case_code
```

No puede estar vacío.

### Responsable original

```
responsible_name
```

No puede estar vacío.

### Usuario

```
user_name
```

No puede estar vacío.

### Proyecto

```
project
```

No puede estar vacío.

### Fecha

```
registered_at
```

Debe contener una fecha/hora válida.

Formato conceptual:

```
ISO 8601 DateTime
```

Ejemplo:

```
2026-08-10T14:30:00
```

### Estado

```
status
```

No puede estar vacío.

### Categoría

```
final_category
```

No puede estar vacía.

### Descripción

```
description
```

No puede estar vacía.

### Solución

```
solution
```

No puede estar vacía.

---

# 10. Resultado de validación

El `Case Validator` deberá producir conceptualmente:

```
ValidationResult
│
├── valid = true
│
└── errors = []
```

o:

```
ValidationResult
│
├── valid = false
│
└── errors
      ├── field
      ├── code
      └── message
```

Un `Case` inválido no podrá continuar hacia las siguientes validaciones de negocio.

---

# 11. Responsable seleccionado

El responsable seleccionado por el usuario **no forma parte del Case**.

Existen dos conceptos diferentes:

### Responsable original

```
Case.responsible_name
```

Representa el responsable registrado en Aranda.

### Responsable seleccionado

```
Processing.responsible_id
```

Representa la persona seleccionada para ejecutar el procesamiento.

Por lo tanto:

```
Case
└── responsible_name
        ↓
Responsable original
```

y:

```
Processing
└── responsible_id
        ↓
Responsable seleccionado
```

No deberán mezclarse ambos conceptos.

---

# 12. Filtrado por responsable

Una vez validada la estructura del `Case`, se realizará la comparación:

```
Processing.responsible_id
          ↓
Responsible.name
          ↓
Case.responsible_name
```

Conceptualmente:

```
Responsable seleccionado
          │
          ▼
Carlos Rodríguez
          │
          ▼
Case.responsible_name
          │
     ┌────┴────┐
     │         │
   Igual    Diferente
     │         │
     ▼         ▼
Continúa    No candidato
```

Los casos pertenecientes a otro responsable no deberán ser enviados al `Estimation Engine`.

---

# 13. Responsable inválido

La validación de que el responsable seleccionado:

- Existe.
- Está activo.
- Puede ser utilizado.

corresponde al `Business Catalog Service`/servicio de aplicación antes de ejecutar Gestión de Casos.

Por lo tanto, Gestión de Casos recibe un responsable válido para la ejecución.

---

# 14. Estado del Case

El módulo no deberá mantener una lista independiente de estados procesables.

Deberá consultar:

```
Business Catalog Service
        ↓
Catálogo de Estados
```

La fuente de verdad será el catálogo correspondiente.

Para V1, según la definición actual:

```
Solucionado
Cerrado
```

son estados procesables.

---

# 15. Validación del estado

El flujo será:

```
Case.status
      ↓
Business Catalog Service
      ↓
Catálogo de Estados
      ↓
¿Estado procesable?
```

Si:

```
Sí
 ↓
Continúa
```

Si:

```
No
 ↓
ProcessingRejection
```

con:

```
reason_code = ESTADO_NO_PROCESABLE
```

---

# 16. Categoría final

El módulo utilizará exclusivamente:

```
Case.final_category
```

La categoría representa la categoría final registrada en Aranda.

No deberán utilizarse:

```
Categoría anterior
Subcategoría
Categoría inferida
Categoría generada por IA
```

---

# 17. Validación de categoría

Gestión de Casos consultará:

```
Business Catalog Service
        ↓
Catálogo de Tiempos
```

para comprobar que exista una configuración válida para:

```
Case.final_category
```

Si no existe:

```
CATEGORIA_NO_CONFIGURADA
```

Si existe:

```
Continúa
```

---

# 18. Control de duplicidad

El módulo deberá considerar la existencia de duplicidades.

Dentro de un mismo `Upload`, el identificador funcional será:

```
upload_id
+
case_code
```

La persistencia deberá protegerlo mediante:

```
UNIQUE(upload_id, case_code)
```

definido en el Modelo de Datos.

Gestión de Casos no deberá procesar múltiples representaciones del mismo caso dentro de la misma carga.

---

# 19. Clasificación

Una vez completadas las validaciones:

```
Case
 │
 ├── Validación estructural
 │
 ├── Responsable
 │
 ├── Estado
 │
 ├── Categoría
 │
 └── Duplicidad
 │
 ▼
Clasificación
```

El resultado será:

```
PROCESABLE
```

o:

```
RECHAZADO
```

---

# 20. Caso procesable

Un `Case` será procesable cuando:

```
Datos válidos
      AND
Responsable correspondiente
      AND
Estado procesable
      AND
Categoría configurada
      AND
No duplicado
```

Resultado:

```
Case
  ↓
Procesable
  ↓
Estimation Engine
```

Gestión de Casos **no determinará todavía el tiempo**.

---

# 21. Caso rechazado

Cuando un caso no pueda continuar, se deberá generar información suficiente para registrar:

```
ProcessingRejection
```

Ejemplo:

```
{
  "case_id": "UUID",
  "reason_code": "CATEGORIA_NO_CONFIGURADA",
  "message": "La categoría no posee una configuración activa."
}
```

---

# 22. Códigos de rechazo

Los códigos iniciales serán:

```
DATOS_INCOMPLETOS
RESPONSABLE_NO_SELECCIONADO
RESPONSABLE_NO_VALIDO
ESTADO_NO_PROCESABLE
CATEGORIA_NO_CONFIGURADA
RANGO_NO_CONFIGURADO
DUPLICADO
RESULTADO_INVALIDO
```

Sin embargo, Gestión de Casos utilizará principalmente los relacionados con su propia responsabilidad:

```
DATOS_INCOMPLETOS
ESTADO_NO_PROCESABLE
CATEGORIA_NO_CONFIGURADA
DUPLICADO
```

Los demás códigos pertenecen a otras etapas del procesamiento.

---

# 23. Procesamiento parcial

La existencia de casos rechazados **no deberá detener la ejecución completa**.

Ejemplo:

```
120 Cases
   │
   ├── 85 procesables
   └── 35 rechazados
```

Resultado:

```
Processing
status = COMPLETED
```

con:

```
processed_cases = 85
rejected_cases = 35
```

---

# 24. Case Context Builder

Para los casos procesables, el módulo podrá construir un contexto específico para las etapas posteriores.

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

- No reemplaza al `Case`.
- No es un nuevo `Case`.
- No modifica el caso original.
- No representa el resultado final.
- Es específico para el procesamiento posterior.

---

# 25. Información original

La información proveniente de Aranda deberá permanecer intacta.

```
Case
├── description
├── solution
├── status
├── final_category
└── ...
```

La información generada posteriormente será independiente:

```
AIResult
├── estimated_minutes
└── generated_description
```

Por lo tanto:

```
AIResult.generated_description
             X
             ↓
Case.description
```

Nunca se deberá sobrescribir la descripción original.

---

# 26. Separación de responsabilidades

Gestión de Casos:

```
VALIDA
FILTRA
CLASIFICA
PREPARA
```

No:

```
ESTIMA
GENERA IA
EXPORTA
INTEGRA COMPROJECT
```

La separación será:

```
Gestión de Casos
        ↓
"¿Puede procesarse?"
        ↓
Estimation Engine
        ↓
"¿Cuánto tiempo?"
        ↓
AI Service
        ↓
"¿Qué descripción profesional?"
```

---

# 27. Dependencias

Gestión de Casos dependerá conceptualmente de:

```
Case Contract
     │
     ▼
Gestión de Casos
     │
     ├── Business Catalog Service
     │      ├── Catálogo de Estados
     │      └── Catálogo de Tiempos
     │
     ├── Case Repository
     │
     └── Case Context Builder
```

El catálogo de responsables será utilizado para validar el responsable de ejecución, principalmente desde la capa de aplicación.

---

# 28. Persistencia

Gestión de Casos no accederá directamente a PostgreSQL.

Incorrecto:

```
Case Management
      ↓
SQLAlchemy
      ↓
PostgreSQL
```

Correcto:

```
Case Management
      ↓
Repository
      ↓
SQLAlchemy
      ↓
PostgreSQL
```

Esto mantiene la separación definida en el Modelo de Datos.

---

# 29. Integridad Upload / Case / Processing

Todo caso procesado deberá pertenecer al mismo `Upload` de la ejecución.

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
      └── Case de Upload B
```

Esta integridad deberá validarse en la aplicación y protegerse mediante persistencia cuando técnicamente sea posible.

---

# 30. Exclusividad de procesamiento

Dentro de un mismo:

```
Processing + Case
```

un caso no podrá ser simultáneamente:

```
Procesado
```

y:

```
Rechazado
```

Debe cumplirse uno de los dos estados:

```
Case
 │
 └── Estimation válida
```

o:

```
Case
 │
 └── ProcessingRejection
```

pero no ambos.

# 31. Relación con Estimation Engine

Gestión de Casos termina cuando entrega los casos procesables.

```
Gestión de Casos
        │
        ▼
Case procesable
        │
        ▼
Estimation Engine
```

No deberá calcular:

```
estimated_minutes
minimum_minutes
maximum_minutes
```

aunque puede entregar al `Estimation Engine` la categoría necesaria para que este consulte la configuración correspondiente.

---

# 32. Relación con AI Service

Gestión de Casos prepara el contexto necesario.

```
Case
 ↓
Case Context Builder
 ↓
Context
 ↓
AI Service
```

El `AI Service` será responsable de producir:

```
AIResult
```

Gestión de Casos no deberá conocer:

- Prompt.
- Modelo.
- Temperatura.
- Ollama.
- Configuración del LLM.
- Formato interno de inferencia.

---

# 33. Reglas del módulo

### MGC-01 — Independencia del Excel

Gestión de Casos trabajará con `Case` y no directamente con estructuras del Excel.

### MGC-02 — Validación

Todo `Case` deberá ser validado antes de continuar.

### MGC-03 — Campos obligatorios

Los campos definidos en el Case Contract deberán estar presentes y ser válidos.

### MGC-04 — Responsable original

`Case.responsible_name` representa exclusivamente el responsable registrado en Aranda.

### MGC-05 — Responsable de ejecución

El responsable seleccionado pertenece a `Processing.responsible_id`.

### MGC-06 — Filtrado

Solo los casos correspondientes al responsable seleccionado podrán continuar.

### MGC-07 — Estados

La condición de estado procesable deberá consultarse mediante el catálogo oficial.

### MGC-08 — Estados V1

`Solucionado` y `Cerrado` son procesables en V1.

### MGC-09 — Categoría

Solo se utilizará `final_category`.

### MGC-10 — Categoría configurada

Una categoría sin configuración válida provocará rechazo.

### MGC-11 — Duplicidad

No deberá procesarse más de una representación del mismo `case_code` dentro del mismo `Upload`.

### MGC-12 — Información original

Los datos originales no podrán modificarse para hacer procesable un caso.

### MGC-13 — Rechazos

Todo rechazo deberá conservar código y mensaje.

### MGC-14 — Procesamiento parcial

Los rechazos no deberán impedir procesar casos válidos.

### MGC-15 — Sin estimación

Gestión de Casos no calculará tiempos.

### MGC-16 — Sin IA

Gestión de Casos no ejecutará IA.

### MGC-17 — Sin COMProject

Gestión de Casos no interactuará con COMProject.

### MGC-18 — Sin acceso directo a BD

Gestión de Casos utilizará repositorios.

### MGC-19 — Contexto

El contexto generado para etapas posteriores no reemplazará al `Case`.

### MGC-20 — Trazabilidad

Todo resultado posterior deberá poder relacionarse con el `Case` y `Processing` correspondientes.

---

# 34. Flujo definitivo del módulo

```
                    Case
                      │
                      ▼
              Case Normalizer
                      │
                      ▼
              Case Validator
                      │
              ┌───────┴───────┐
              │               │
            Inválido          Válido
              │               │
              ▼               ▼
          Rechazado      Responsable
                              │
                       ┌──────┴──────┐
                       │             │
                    No coincide   Coincide
                       │             │
                       ▼             ▼
                    Excluir       Estado
                                      │
                               ┌──────┴──────┐
                               │             │
                           No procesable  Procesable
                               │             │
                               ▼             ▼
                            Rechazo       Categoría
                                             │
                                      ┌──────┴──────┐
                                      │             │
                                 No configurada  Configurada
                                      │             │
                                      ▼             ▼
                                   Rechazo       Duplicidad
                                                     │
                                              ┌──────┴──────┐
                                              │             │
                                           Duplicado    No duplicado
                                              │             │
                                              ▼             ▼
                                           Rechazo      PROCESABLE
                                                           │
                                                           ▼
                                                 Case Context Builder
                                                           │
                                                           ▼
                                                  Estimation Engine
```

---

# 35. Contrato de salida

El módulo conceptualmente producirá:

```
{
  "processable_cases": [],
  "rejected_cases": []
}
```

Los `processable_cases` continuarán hacia el `Estimation Engine`.

Los `rejected_cases` serán utilizados para generar los `ProcessingRejection`.

---

# 36. Pruebas mínimas

El módulo deberá contar como mínimo con pruebas para:

### Validación

```
Case válido
Case sin case_code
Case sin responsible_name
Case sin user_name
Case sin project
Case sin registered_at
Case sin status
Case sin final_category
Case sin description
Case sin solution
```

### Responsable

```
Responsable coincide
Responsable diferente
```

### Estado

```
Estado procesable
Estado no procesable
```

### Categoría

```
Categoría configurada
Categoría no configurada
```

### Duplicidad

```
Case único
Case duplicado dentro de Upload
Mismo case_code en diferentes Upload
```

### Resultado

```
Caso procesable
Caso rechazado
Procesamiento parcial
```

---

# 37. Matriz de responsabilidades

| Acción | Gestión de Casos | Catalog Service | Estimation Engine | AI Service |
| --- | --- | --- | --- | --- |
| Validar estructura Case | ✅ |  |  |  |
| Normalizar Case | ✅ |  |  |  |
| Filtrar responsable | ✅ | Consulta |  |  |
| Validar estado | Consulta | ✅ |  |  |
| Validar categoría | Consulta | ✅ |  |  |
| Determinar rango |  | Consulta | ✅ |  |
| Calcular estimación |  |  | ✅ |  |
| Generar descripción |  |  |  | ✅ |
| Validar salida IA |  |  | ✅ |  |
| Generar AIResult |  |  |  | ✅ |

---

# 38. Fuente de verdad

Este documento define exclusivamente:

- Responsabilidad de Gestión de Casos.
- Componentes internos.
- Flujo.
- Validaciones.
- Filtrado.
- Clasificación.
- Dependencias.
- Salidas.
- Reglas del módulo.
- Pruebas mínimas.

No define:

- Rangos de tiempo.
- Algoritmo de estimación.
- Prompts.
- Modelos de IA.
- Endpoints.
- Estructura física de PostgreSQL.
- Interfaz gráfica.
- Integración con COMProject.

---

# 39. Consistencia con los documentos actuales

Con las decisiones que acabamos de tomar, el contrato queda unificado así:

| Concepto | Definición V1 |
| --- | --- |
| Identificador funcional | `case_code` |
| Responsable original | `responsible_name` |
| Usuario | `user_name` |
| Proyecto | `project` |
| Fecha | `registered_at` |
| Tipo fecha | `DateTime` |
| Estado | `status` |
| Categoría | `final_category` |
| Descripción | `description` |
| Solución | `solution` |
| Responsable seleccionado | `Processing.responsible_id` |
| Ejecución | `Processing` |
| Resultado IA | `AIResult` |
| Resultado final | `Estimation` |
| Rechazo | `ProcessingRejection` |

Y los tres campos que estaban en discusión quedan definitivamente:

```
user_name       → OBLIGATORIO
description     → OBLIGATORIO
solution        → OBLIGATORIO
```

Además:

```
registered_at → DateTime
```

---

# 40. Estado de cierre

Con estas decisiones, considero **cerrado el Diseño del Módulo de Gestión de Casos V1**.

La cadena de documentos queda coherente en este punto:

```
Case Contract
       │
       ▼
Gestión de Casos
       │
       ├── Business Catalog Service
       │
       ▼
Case procesable / rechazado
       │
       ▼
Estimation Engine
       │
       ▼
AI Service
       │
       ▼
Estimation
```