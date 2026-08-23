**Proyecto:** BOT-COMProject

**Versión:** 1.3

**Estado:** Definido

---

# 1. Objetivo

Definir los módulos funcionales y componentes de aplicación que componen BOT-COMProject, estableciendo sus responsabilidades, entradas, salidas y relaciones.

La organización deberá mantener una separación clara de responsabilidades y estar alineada con los principios de **Clean Architecture**.

> Un módulo no deberá crearse únicamente por anticipación. Se incorporará cuando exista una necesidad real de agregar archivos, componentes, servicios, modelos, reglas o responsabilidades relacionadas con una funcionalidad.
> 

La V1 deberá permitir cargar un Maestro de Casos, registrar la carga, ejecutar un procesamiento asociado a un responsable, generar resultados, registrar rechazos y exportar los resultados.

---

# 2. Vista General

La V1 estará organizada conceptualmente de la siguiente manera:

```
                         BOT-COMProject
                               │
                               ▼
                        Interfaz Web
                               │
                               ▼
                     Gestión de Archivos
                               │
                               ▼
                            Upload
                               │
                               ▼
                        Excel Service
                               │
                               ▼
                       Gestión de Casos
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
 Case Validator          Case Filter          Case Normalizer
        │                      │
        │                      ▼
        │             Catalog Service
        │                      │
        │              ┌───────┼────────┐
        │              ▼       ▼        ▼
        │           Estados  Tiempos Responsables
        │
        └──────────────────────┐
                               ▼
                    Case Context Builder
                               │
                               ▼
                       Estimation Engine
                               │
                       ┌───────┴───────┐
                       │               │
                       ▼               ▼
               Catalog Service    AI Service
                    Service             │
                       │                 ▼
                       │              Ollama
                       │                 │
                       └────────┬────────┘
                                ▼
                       Estimation Engine
                           Validación
                                │
                                ▼
                       Resultado Procesado
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              Case Repository       Processing Result
                                           │
                                           ▼
                                      Exportación

                         Processing
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             Resultados             Rechazos
```

---

# 3. Gestión de Archivos

## Responsabilidad

Gestionar la recepción y validación inicial del Maestro de Casos proporcionado por el usuario.

## Entrada

```
Archivo Excel (.xlsx)
```

## Salidas

```
Archivo recibido
Archivo validado
Upload registrado
Errores de carga/validación
```

## Funciones

- Recibir el archivo.
- Validar extensión.
- Validar estructura inicial.
- Validar que el archivo pueda ser procesado.
- Registrar la carga como un `Upload`.
- Entregar el archivo validado al `Excel Service`.

Este componente no deberá interpretar las reglas de negocio de los casos.

---

# 4. Upload

## Responsabilidad

Representar una carga concreta del Maestro de Casos dentro del sistema.

Un `Upload` permite identificar el archivo que posteriormente podrá ser utilizado para ejecutar uno o varios procesamientos.

Conceptualmente:

```
Archivo físico
      │
      ▼
    Upload
      │
      ├── nombre del archivo
      ├── estado
      ├── fecha de creación
      └── información de la carga
```

## Funciones

- Identificar una carga concreta.
- Mantener la trazabilidad del archivo recibido.
- Asociar los casos extraídos con la carga correspondiente.
- Permitir que el procesamiento posterior utilice `upload_id`.

El identificador del `Upload` será:

```
upload_id
```

El `Upload` no representa una ejecución de procesamiento.

---

# 5. Excel Service

## Responsabilidad

Extraer y transformar la información necesaria del Maestro de Casos para que pueda ser procesada por el sistema.

## Entrada

```
Archivo Excel validado
```

## Salidas

```
Casos normalizados
Errores de procesamiento
```

## Funciones

- Leer el archivo.
- Identificar encabezados.
- Extraer columnas requeridas.
- Normalizar valores de entrada.
- Identificar `Responsible Name`.
- Extraer la categoría final.
- Extraer el estado.
- Extraer el proyecto.
- Extraer la descripción.
- Extraer la solución.
- Extraer la fecha.
- Asociar los casos al `Upload`.
- Entregar los casos a Gestión de Casos.

El `Excel Service` no deberá decidir si un caso es procesable.

Esa responsabilidad corresponde a Gestión de Casos utilizando las reglas y configuraciones proporcionadas por el **Catalog Service**.

---

# 6. Gestión de Casos

## Responsabilidad

Coordinar la validación y preparación de los casos para continuar el procesamiento.

## Entradas

```
Casos provenientes del Excel Service
Responsable seleccionado
```

## Salidas

```
Casos procesables
Casos no procesables
Motivos de exclusión
```

## Funciones

- Validar información obligatoria.
- Comparar `Responsible Name` con el responsable seleccionado.
- Aplicar reglas de estados.
- Identificar estados procesables.
- Validar categoría final.
- Normalizar información cuando corresponda.
- Organizar los casos.
- Preparar el contexto requerido para la estimación.
- Evitar duplicidad dentro de una ejecución.

Los estados procesables de V1 son:

```
Solucionado
Cerrado
```

La determinación de si un estado es procesable deberá realizarse mediante el **Catalog Service**.

Gestión de Casos no deberá contener directamente una lista codificada de estados procesables.

---

# 7. Case Validator

## Responsabilidad

Verificar que un caso tenga la información mínima necesaria para continuar.

## Validaciones

Puede validar:

- Código del caso.
- Responsable.
- Estado.
- Categoría final.
- Proyecto.
- Fecha.
- Descripción.
- Solución.
- Información necesaria para la estimación.

Si una validación obligatoria falla, el caso deberá ser marcado como no procesable y deberá registrarse el motivo correspondiente.

---

# 8. Case Filter

## Responsabilidad

Determinar qué casos pueden continuar con el procesamiento según las reglas de negocio.

El filtrado contempla principalmente:

```
Responsable seleccionado
        ↓
Estado procesable
        ↓
Información requerida
        ↓
Categoría válida
```

El `Case Filter` no deberá acceder directamente a las estructuras de persistencia de los catálogos.

Cuando necesite información de un catálogo deberá utilizar:

```
Case Filter
     ↓
Catalog Service
```

---

# 9. Case Normalizer

## Responsabilidad

Estandarizar los datos del caso cuando sea necesario para garantizar consistencia durante el procesamiento.

Puede realizar tareas como:

- Eliminar espacios innecesarios.
- Estandarizar formatos.
- Normalizar valores.
- Corregir representaciones inconsistentes.
- Preparar información para los siguientes componentes.

La normalización no deberá alterar el significado de la información original del caso.

La información original deberá conservarse para consulta y trazabilidad.

---

# 10. Organización de Casos

Los casos podrán organizarse internamente para facilitar determinadas operaciones de procesamiento, consulta o presentación.

Los criterios podrán incluir:

- Responsable.
- Proyecto.
- Semana.
- Fecha.

Esta organización **no constituye una regla de negocio de estimación**.

La organización no deberá:

- Modificar las reglas de negocio.
- Determinar el tiempo de un caso.
- Combinar artificialmente varios casos para generar una única estimación.
- Sustituir el procesamiento individual.

Cada caso procesable deberá mantener su propia identidad y su propio resultado.

> V1 no requiere un módulo independiente `Case Grouper`. La organización de casos deberá implementarse como una capacidad interna únicamente cuando exista una necesidad funcional concreta.
> 

---

# 11. Case Context Builder

## Responsabilidad

Construir el contexto necesario para que el `Estimation Engine` pueda procesar cada caso individualmente.

El contexto podrá contener:

```
Código
Descripción
Solución
Proyecto
Categoría final
Estado
```

Posteriormente, el `Estimation Engine` incorporará al contexto el rango de tiempo autorizado obtenido mediante el **Catalog Service**.

El `Case Context Builder` únicamente deberá incluir información necesaria y autorizada.

---

# 12. Catalog Service

## Responsabilidad

Proporcionar acceso centralizado a los catálogos utilizados por el sistema.

El **Catalog Service** será el único servicio autorizado para consultar los catálogos de negocio.

## Catálogos V1

```
Catalog Service
          │
          ├── Catálogo de Estados
          │
          ├── Catálogo de Tiempos
          │
          └── Catálogo de Responsables
```

## Funciones

- Consultar estados.
- Determinar estados procesables.
- Consultar categorías configuradas.
- Obtener rangos de tiempo.
- Consultar responsables disponibles.
- Validar que una configuración esté activa.

## Regla de acceso

Los demás componentes nunca deberán acceder directamente a la persistencia de los catálogos.

Correcto:

```
Componente
     ↓
Catalog Service
     ↓
Catálogo
```

No permitido:

```
Componente
     ↓
Base de datos
     ↓
Tabla del catálogo
```

---

# 13. Case Repository

## Responsabilidad

Persistir y recuperar la información relacionada con los casos.

## Funciones

- Guardar información original de los casos.
- Consultar casos.
- Recuperar casos asociados a un `Upload`.
- Recuperar casos necesarios para una ejecución.
- Persistir información relacionada con resultados cuando corresponda.
- Evitar duplicidades según las reglas definidas por la aplicación.

El `Case Repository` no deberá contener reglas de negocio propias del proceso.

Su responsabilidad será persistir y recuperar información.

---

# 14. Separación entre Información Original y Generada

El sistema deberá mantener conceptualmente separadas:

```
Información original
proveniente del Excel
```

y:

```
Información generada
durante el procesamiento
```

Por ejemplo:

```
Caso original
      │
      ├── Código
      ├── Responsable
      ├── Proyecto
      ├── Categoría
      ├── Estado
      ├── Fecha
      ├── Descripción original
      └── Solución original

Resultado
      │
      ├── Tiempo estimado
      └── Descripción generada
```

La información generada por la IA **nunca deberá reemplazar** la información original del caso.

---

# 15. Processing

## Responsabilidad

Representar una ejecución concreta del procesamiento de casos.

Un `Processing` es una entidad independiente del `Upload` y de los casos individuales.

Conceptualmente:

```
Upload
   │
   ├── Processing 1
   ├── Processing 2
   └── Processing 3
```

Cada ejecución deberá identificarse mediante:

```
processing_id
```

## Relación

```
Upload
   │
   └──< Processing
            │
            ├──< Resultados
            │
            └──< Rechazos
```

Un `Processing` deberá permitir conocer como mínimo:

- Upload utilizado.
- Responsable seleccionado.
- Estado técnico de la ejecución.
- Resumen de casos.
- Resultados generados.
- Casos rechazados.
- Información temporal de la ejecución.

---

# 16. Estados de Processing

Los estados técnicos de `Processing` serán:

```
PENDING
PROCESSING
COMPLETED
FAILED
```

Estos estados representan exclusivamente la ejecución técnica.

No deberán confundirse con los estados originales provenientes de Aranda.

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

# 17. Ejecución del Processing

El procesamiento V1 será iniciado mediante:

```
POST /api/v1/cases/process
```

El flujo conceptual será:

```
Request
   ↓
Validar Upload
   ↓
Validar Responsable
   ↓
Crear Processing
   ↓
Obtener casos
   ↓
Procesar casos individualmente
   ↓
Persistir resultados/rechazos
   ↓
Actualizar Processing
   ↓
COMPLETED
```

La V1 utilizará procesamiento síncrono.

Por tanto, la llamada de procesamiento deberá completar la ejecución antes de devolver el resultado final cuando el volumen de casos pueda procesarse dentro de los límites operativos definidos para V1.

El modelo `Processing` conservará los estados técnicos necesarios para permitir una evolución posterior hacia procesamiento asíncrono sin modificar el concepto de ejecución.

---

# 18. Procesamiento Parcial

El procesamiento deberá permitir que los casos válidos continúen aunque otros sean rechazados.

Ejemplo:

```
120 casos
   │
   ├── 85 procesados
   └── 35 rechazados
```

La existencia de casos rechazados no significa que la ejecución completa haya fallado.

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

# 19. Rechazos

Los casos que no puedan continuar deberán registrarse como rechazos asociados a la ejecución correspondiente.

Conceptualmente:

```
Processing
     │
     └── Rechazos
            │
            ├── case_id
            ├── reason_code
            └── message
```

Cada rechazo deberá poder relacionarse con:

```
processing_id
```

Esto permitirá consultar posteriormente:

```
GET /api/v1/processing/{processing_id}/rejected
```

Los rechazos no deberán eliminar ni modificar la información original del caso.

---

# 20. Códigos de Rechazo

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

# 21. Estimation Engine

## Responsabilidad

Determinar el tiempo estimado de un caso utilizando el rango autorizado por el Catálogo de Tiempos y la información contextual del caso.

## Entradas

```
Caso
Categoría final
Rango de tiempo autorizado
Contexto
```

## Salidas

```
Tiempo recomendado
Tiempo validado
Resultado de estimación
```

## Flujo

```
Categoría final
       ↓
Catalog Service
       ↓
Categoría configurada
       ↓
Rango mínimo/máximo
       ↓
Estimation Engine
       ↓
AI Service
       ↓
Tiempo recomendado
       ↓
Estimation Engine
       ↓
Validación
       ↓
Tiempo estimado
```

## Restricción principal

El tiempo estimado nunca podrá encontrarse fuera del rango autorizado.

```
mínimo ≤ tiempo estimado ≤ máximo
```

La IA propone el tiempo, pero el `Estimation Engine` controla y valida el cumplimiento de la regla.

---

# 22. AI Service

## Responsabilidad

Gestionar la interacción con el modelo de IA local.

## Entradas

```
Contexto del caso
Rango permitido
Información relevante
```

## Salidas

```
Tiempo recomendado
Descripción profesional
```

## Funciones

- Construir la solicitud al modelo.
- Ejecutar inferencia mediante Ollama.
- Procesar la respuesta.
- Validar que la respuesta cumpla el contrato técnico esperado.
- Entregar el resultado al `Estimation Engine`.

## Restricciones

La IA no podrá:

- Crear nuevas reglas.
- Modificar catálogos.
- Cambiar rangos.
- Recomendar tiempos fuera del rango autorizado.
- Sustituir las reglas de negocio.
- Modificar la información original del caso.

La validación de las reglas de negocio relacionadas con el tiempo corresponde al `Estimation Engine`.

---

# 23. Resultado de Procesamiento

Cada caso procesado deberá generar un resultado individual.

```
Caso
    │
    ├── Tiempo estimado
    │
    └── Descripción profesional
```

Los resultados deberán estar asociados a:

```
processing_id
case_id
```

Estos resultados representan la salida principal de la V1.

La información original del caso deberá conservarse independientemente del resultado generado.

---

# 24. Persistencia de Resultados

Los resultados generados durante una ejecución deberán poder recuperarse posteriormente mediante el `processing_id`.

Conceptualmente:

```
Processing
     │
     └── Resultados
            │
            ├── case_id
            ├── tiempo estimado
            └── descripción generada
```

Un resultado deberá pertenecer a una ejecución concreta.

Esto permite diferenciar resultados producidos por diferentes ejecuciones sobre un mismo `Upload`.

---

# 25. Vista Previa

## Responsabilidad

Presentar al usuario los resultados generados antes de su utilización.

La vista podrá mostrar:

| Campo | Información |
| --- | --- |
| Código | Código del caso |
| Responsable | Responsable seleccionado |
| Proyecto | Proyecto |
| Categoría | Categoría final |
| Estado | Estado del caso |
| Tiempo | Tiempo estimado |
| Descripción | Descripción generada |

La Vista Previa no deberá contener lógica de negocio encargada de determinar si un caso es procesable o qué tiempo corresponde.

---

# 26. Exportación

## Responsabilidad

Generar una salida estructurada de los resultados pertenecientes a una ejecución.

## Entrada

```
processing_id
```

## Salida

```
Archivo Excel
```

La exportación permitirá utilizar posteriormente la información para el proceso de registro de horas.

Solo podrán exportarse resultados asociados al `processing_id` solicitado.

La V1 no realizará el registro automático en COMProject.

---

# 27. Integración con COMProject

## Estado

**Fuera del alcance de V1.**

### Responsabilidad futura

Enviar o registrar automáticamente la información aprobada en COMProject.

La arquitectura deberá permitir incorporar esta funcionalidad posteriormente sin modificar significativamente los componentes existentes.

No deberá implementarse este componente en V1 si no existe una necesidad real dentro del alcance definido.

---

# 28. Dependencias

| Componente | Dependencia |
| --- | --- |
| Gestión de Archivos | Ninguna |
| Upload | Gestión de Archivos |
| Excel Service | Gestión de Archivos, Upload |
| Gestión de Casos | Excel Service, Catalog Service, Case Repository |
| Case Validator | Gestión de Casos |
| Case Filter | Gestión de Casos, Catalog Service |
| Case Normalizer | Gestión de Casos |
| Organización de Casos | Gestión de Casos |
| Case Context Builder | Gestión de Casos |
| Catalog Service | Persistencia de catálogos |
| Case Repository | Base de datos |
| Processing | Application Service, Upload |
| Resultados | Processing, Case Repository |
| Rechazos | Processing, Case Repository |
| Estimation Engine | Catalog Service, AI Service |
| AI Service | Ollama |
| Vista Previa | Resultados procesados |
| Exportación | Resultados procesados |
| Integración COMProject | V2 o posterior |

---

# 29. Flujo de Comunicación

```
Usuario
   │
   ▼
Gestión de Archivos
   │
   ▼
Upload
   │
   ▼
Excel Service
   │
   ▼
Application Service
   │
   ▼
Crear Processing
   │
   ▼
Gestión de Casos
   │
   ├──► Case Validator
   │
   ├──► Case Filter ─────────► Catalog Service
   │
   ├──► Case Normalizer
   │
   └──► Case Context Builder
                    │
                    ▼
             Estimation Engine
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
 Catalog Service        AI Service
 Service                      │
          │                   ▼
          │                 Ollama
          │                   │
          └─────────┬─────────┘
                    ▼
             Estimation Engine
                    │
                 Validación
                    │
                    ▼
             Resultado Procesado
                    │
                    ▼
              Processing
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Resultados          Rechazos
          │                   │
          └─────────┬─────────┘
                    ▼
              Case Repository
                    │
                    ▼
              Vista Previa
                    │
                    ▼
                Exportación
```

# 30. Principios de Diseño

Todos los componentes deberán cumplir:

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Comunicación mediante contratos.
- Separación entre lógica de negocio e infraestructura.
- Testabilidad.
- Reutilización.
- Independencia de implementaciones concretas.
- Conservación de la información original.
- Centralización de las reglas de catálogo.
- Trazabilidad de cada ejecución mediante `processing_id`.

---

# 31. Centralización de Catálogos

Los catálogos deberán mantenerse centralizados.

Ningún componente deberá acceder directamente a las tablas o estructuras de persistencia de los catálogos.

El acceso será:

```
Componente
     ↓
Catalog Service
     ↓
Catálogo
```

Nunca:

```
Componente
     ↓
Base de datos del catálogo
```

Esto garantiza que las reglas de acceso y consulta de los catálogos permanezcan centralizadas.

---

# 32. Módulos Futuros

La arquitectura podrá incorporar posteriormente:

- Integración con COMProject.
- Auditoría.
- Historial avanzado de ejecuciones.
- Gestión de usuarios.
- Administración de catálogos desde UI.
- Notificaciones.
- Estadísticas.
- Ejecuciones programadas.
- Integración con otros sistemas ITSM.

Estos componentes no deberán implementarse en V1 si no son necesarios para el flujo definido.

---

# 33. Regla de Creación de Módulos

> **No se deberá crear un módulo únicamente porque esté contemplado como una posible funcionalidad futura.**
> 

Un módulo será creado cuando exista una necesidad real de incorporar:

- Archivos.
- Componentes.
- Servicios.
- Modelos.
- Reglas.
- Responsabilidades relacionadas.

Esta regla busca evitar una arquitectura sobredimensionada y mantener el proyecto organizado únicamente alrededor de las necesidades reales de cada versión.

La existencia conceptual de una capacidad no implica necesariamente que deba existir un módulo independiente.

---

# 34. Regla de Consistencia Documental

El presente documento deberá mantenerse alineado con los demás documentos oficiales del proyecto.

Ningún módulo, responsabilidad, dependencia o flujo definido aquí podrá contradecir las reglas establecidas en:

- Project Charter.
- Business Process Analysis.
- Glosario.
- Catálogo de Estados.
- Catálogo de Tiempos.
- Catálogo de Responsables.
- Case Contract.
- Diseño de Gestión de Casos.
- Estimation Engine.
- AI Service.
- Modelo de Datos.
- Contrato API.

Cuando una nueva decisión modifique el comportamiento de un módulo:

```
Nueva decisión
      ↓
Identificar documentos afectados
      ↓
Actualizar documentos
      ↓
Verificar consistencia
      ↓
Continuar desarrollo
```

Esta regla será obligatoria antes de utilizar la documentación como contexto para **OpenCode**.

---

# 35. Relación entre Upload, Processing y Cases

La relación conceptual de V1 será:

```
Upload
   │
   └──< Cases
   │
   └──< Processing
             │
             ├──< Processing Results
             │
             └──< Processing Rejections
```

Un mismo `Upload` podrá ser utilizado por diferentes ejecuciones.

Por ejemplo:

```
Upload A
   │
   ├── Processing 1
   │       ├── Results
   │       └── Rejections
   │
   └── Processing 2
           ├── Results
           └── Rejections
```

Esto permite mantener la trazabilidad de cada ejecución.

---

# 36. Idempotencia y ejecuciones concurrentes

El procesamiento deberá evitar ejecuciones accidentales duplicadas.

La operación deberá considerar como mínimo:

```
upload_id
+
responsible_id
+
ejecución activa
```

No deberá asumirse que repetir una petición HTTP implica automáticamente crear una nueva ejecución.

Cuando exista una ejecución activa para el mismo contexto, el sistema deberá impedir una nueva ejecución concurrente no intencionada.

La estrategia técnica concreta de idempotencia será responsabilidad de la implementación y deberá respetar el Contrato API.

---

# 37. Flujo Funcional V1

El flujo completo será:

```
1. Consultar responsables
        │
        ▼
2. Usuario selecciona responsable
        │
        ▼
3. Cargar Maestro
        │
        ▼
4. Registrar Upload
        │
        ▼
5. Crear Processing
        │
        ▼
6. Obtener casos
        │
        ▼
7. Filtrar casos del responsable
        │
        ▼
8. Validar estados
        │
        ▼
9. Validar información
        │
        ▼
10. Obtener categoría y rango
        │
        ▼
11. Ejecutar Estimation Engine
        │
        ▼
12. Ejecutar AI Service
        │
        ▼
13. Validar resultado
        │
        ├──────────────► Rechazo
        │
        ▼
14. Persistir resultado
        │
        ▼
15. Completar Processing
        │
        ▼
16. Mostrar resultados
        │
        ▼
17. Revisar rechazados
        │
        ▼
18. Exportar resultados
```

---

# 38. Seguridad V1

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

# 39. Definición V1

La V1 permitirá que el usuario realice el flujo completo:

```
Consultar responsables
      ↓
Seleccionar responsable
      ↓
Cargar Maestro
      ↓
Registrar Upload
      ↓
Procesar casos
      ↓
Crear Processing
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

# 40. Decisiones arquitectónicas V1

La V1 establece las siguientes decisiones:

### DA-01 — Upload

Una carga de archivo será representada mediante un `Upload` identificable por `upload_id`.

### DA-02 — Processing

Una ejecución de procesamiento será una entidad identificable independientemente del archivo y de los casos mediante `processing_id`.

### DA-03 — Trazabilidad

Todo resultado y rechazo deberá poder relacionarse con el `processing_id` que lo produjo.

### DA-04 — Procesamiento individual

Cada caso procesable tendrá su propio resultado.

### DA-05 — Procesamiento parcial

Los casos rechazados no provocarán automáticamente el fallo de toda la ejecución.

### DA-06 — IA

La IA propone resultados; no define ni modifica reglas de negocio.

### DA-07 — Estimación

El `Estimation Engine` controla que el tiempo esté dentro del rango autorizado.

### DA-08 — Catálogos

El acceso a catálogos se realizará exclusivamente mediante `Catalog Service`.

### DA-09 — Datos originales

Los datos originales del caso nunca serán reemplazados por información generada.

### DA-10 — Case Grouper

V1 no requiere un módulo independiente de agrupamiento. La organización de casos será una capacidad interna únicamente cuando exista una necesidad funcional concreta.

### DA-11 — Seguridad

La V1 no implementará autenticación.

### DA-12 — COMProject

La integración automática con COMProject queda fuera del alcance de V1.

---

# 41. Control de versión

| Versión | Estado | Cambios principales |
| --- | --- | --- |
| 1.0 | En construcción | Definición inicial de módulos |
| 1.1 | Definido | Centralización de catálogos, `Catalog Service`, `Case Repository` y regla de creación de módulos |
| 1.2 | Definido | Incorporación de `Case Grouper`, separación entre información original y resultados, precisión de responsabilidades de `AI Service` y `Estimation Engine`, y regla de consistencia documental |
| **1.3** | **Definido** | Incorporación formal de `Upload` y `Processing`, definición de resultados y rechazos asociados a ejecuciones, trazabilidad mediante `processing_id`, aclaración del procesamiento V1, unificación de `Catalog Service` y eliminación de `Case Grouper` como módulo independiente obligatorio |