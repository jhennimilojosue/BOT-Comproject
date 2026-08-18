**Proyecto:** BOT-COMProject

**Versión:** 1.1

**Estado:** Definido

**Tipo:** Catálogo de Negocio

---

# 1. Objetivo

El **Catálogo de Tiempos** define los rangos de tiempo autorizados para las categorías finales de los casos procesados por BOT-COMProject.

Su función es proporcionar una fuente única y centralizada para determinar:

- Qué categorías finales están configuradas.
- Cuál es el tiempo mínimo permitido para cada categoría.
- Cuál es el tiempo máximo permitido.
- Si una configuración se encuentra activa.
- Información adicional relacionada con la configuración.

El catálogo será utilizado por el `Business Catalog Service` y consultado por los componentes que requieran información sobre los rangos autorizados.

> El Catálogo de Tiempos **no calcula, selecciona ni genera el tiempo final de un caso**. Únicamente proporciona el rango autorizado que deberá respetar el proceso de estimación.
> 

---

# 2. Alcance V1

En la V1:

- Cada `final_category` podrá tener una configuración de tiempo.
- Cada configuración tendrá un mínimo y un máximo.
- Solo las configuraciones activas podrán utilizarse durante el procesamiento.
- La categoría utilizada será exclusivamente la **categoría final registrada en el Maestro de Casos**.
- Una categoría sin configuración activa no podrá continuar hacia el `Estimation Engine`.
- Los rangos no podrán ser modificados automáticamente por la IA.
- La aplicación no permitirá crear reglas automáticamente.
- El catálogo será consultado exclusivamente mediante el `Business Catalog Service`.

---

# 3. Principios

El catálogo deberá cumplir:

- Fuente única de verdad para los rangos de tiempo.
- Configuración independiente del código.
- Centralización de reglas.
- Fácil mantenimiento.
- Validación de estructura.
- Bajo acoplamiento.
- Reutilización.
- Trazabilidad de las configuraciones.
- Separación entre configuración y lógica de estimación.
- No sobrescribir información original de los casos.
- No contener información específica de una ejecución.
- No depender de `Processing`.
- No depender de `AIResult`.
- No determinar por sí mismo el tiempo final.

---

# 4. Conceptos

## 4.1 Categoría Final

Es la categoría final registrada originalmente en el Maestro de Casos de Aranda.

Se representa en el sistema mediante:

```
Case.final_category
```

Ejemplo:

```
Configurar punto de red Usuarios y/o proyectos
```

Esta será la única categoría utilizada para consultar el Catálogo de Tiempos.

---

## 4.2 Configuración de Tiempo

Una configuración de tiempo es aquella que:

1. Tiene una categoría final.
2. Tiene un tiempo mínimo.
3. Tiene un tiempo máximo.
4. Se encuentra activa.
5. Tiene un rango válido.

Ejemplo:

```
Categoría:
Configurar punto de red Usuarios y/o proyectos

Mínimo:
30 minutos

Máximo:
40 minutos

Activo:
Sí
```

---

## 4.3 Categoría No Configurada

Una categoría será considerada no configurada cuando:

- No exista en el catálogo.
- Exista pero esté inactiva.
- Su configuración no tenga un rango válido.

Flujo:

```
Case.final_category
        ↓
Business Catalog Service
        ↓
Catálogo de Tiempos
        ↓
No existe configuración activa
        ↓
CATEGORIA_NO_CONFIGURADA
```

El caso no podrá continuar hacia el `Estimation Engine`.

---

# 5. Estructura del Catálogo

La estructura propuesta para V1 será:

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `id` | Integer | Sí | Identificador de la configuración. |
| `final_category` | String | Sí | Categoría final del caso. |
| `minimum_minutes` | Integer | Sí | Tiempo mínimo permitido en minutos. |
| `maximum_minutes` | Integer | Sí | Tiempo máximo permitido en minutos. |
| `active` | Boolean | Sí | Indica si la configuración puede utilizarse. |
| `observations` | String | No | Información adicional sobre la configuración. |

### Nota

Los nombres anteriores representan la estructura lógica del catálogo.

La fuente física utilizada en V1 podrá mantener los nombres definidos para el archivo de negocio, siempre que el `Business Catalog Service` realice la transformación correspondiente.

---

# 6. Catálogo Inicial V1

Las categorías conocidas actualmente y sus rangos son:

| ID | Categoría final | Mínimo | Máximo | Activo |
| --- | --- | --- | --- | --- |
| 1 | Cableado puntos de red en sedes Comware o proyectos clientes | 30 | 60 | Sí |
| 2 | Configurar punto de red Usuarios y/o proyectos | 30 | 40 | Sí |
| 3 | Configurar segmento de red en los enlaces de comunicaciones | 60 | 90 | Sí |

Los valores están expresados en **minutos**.

> Este catálogo deberá ampliarse con las demás categorías oficiales cuando se incorpore el catálogo completo proporcionado por el negocio.
> 

---

# 7. Regla del Rango

Cada configuración deberá cumplir:

```
minimum_minutes ≤ maximum_minutes
```

Ejemplo válido:

```
30 ≤ 60
```

Ejemplo inválido:

```
60 ≤ 30
```

Una configuración con un rango inválido no deberá estar disponible para procesamiento.

---

# 8. Valores de Tiempo

Los tiempos deberán:

```
minimum_minutes > 0
maximum_minutes > 0
```

Por lo tanto, no serán válidos:

```
0
-10
-30
```

Los valores deberán expresarse exclusivamente en **minutos enteros**.

---

# 9. Configuración Activa

Solo una configuración con:

```
active = true
```

podrá ser utilizada durante el procesamiento.

Una configuración inactiva deberá considerarse no disponible.

Ejemplo:

```
final_category
       ↓
Business Catalog Service
       ↓
Configuración encontrada
       ↓
active = false
       ↓
CATEGORIA_NO_CONFIGURADA
```

---

# 10. Unicidad de Categoría

En V1 una categoría final no podrá tener múltiples configuraciones activas simultáneamente.

Debe cumplirse:

```
Una final_category
        ↓
Máximo una configuración activa
```

Ejemplo inválido:

```
Categoría X → 30-60 → Activa
Categoría X → 40-90 → Activa
```

Esto deberá generar un error de configuración:

```
DUPLICATE_ACTIVE_CATEGORY
```

Las configuraciones históricas o inactivas podrán existir en la fuente, siempre que no exista más de una configuración activa para la misma categoría.

---

# 11. Fuente de la Categoría

La consulta deberá utilizar exclusivamente:

```
Case.final_category
```

No deberán utilizarse para buscar el rango:

```
Case.project
Case.status
Case.responsible_name
Case.user_name
Case.case_code
```

ni combinaciones de estos campos.

La categoría final constituye la referencia oficial para consultar el rango.

---

# 12. Flujo de Consulta

La consulta del rango deberá realizarse mediante el `Business Catalog Service`.

```
Case.final_category
        │
        ▼
Business Catalog Service
        │
        ▼
Catálogo de Tiempos
        │
        ├── Configuración activa encontrada
        │          │
        │          ▼
        │    minimum_minutes
        │    maximum_minutes
        │          │
        │          ▼
        │    Estimation Engine
        │
        └── No configurada
                   │
                   ▼
             Rechazar caso
```

---

# 13. Integración con Gestión de Casos

`Gestión de Casos` deberá utilizar el `Business Catalog Service` para verificar que la categoría final del caso tenga una configuración activa.

```
Case.final_category
       │
       ▼
Business Catalog Service
       │
       ▼
¿Configuración activa?
       │
   ┌───┴────┐
   │        │
  Sí        No
   │        │
   ▼        ▼
Continuar  Rechazar
```

Si no existe una configuración activa, el caso deberá registrarse como rechazado con:

```
CATEGORIA_NO_CONFIGURADA
```

### Importante

Gestión de Casos **no deberá calcular el tiempo estimado**.

Su responsabilidad termina en verificar que exista una configuración válida que permita continuar.

---

# 14. Integración con Estimation Engine

El `Estimation Engine` utilizará el rango proporcionado por el `Business Catalog Service`.

```
Case.final_category
       ↓
Business Catalog Service
       ↓
minimum_minutes
maximum_minutes
       ↓
Estimation Engine
       ↓
Tiempo recomendado
       ↓
Validación
       ↓
Estimation
```

El `Estimation Engine` no podrá establecer un rango diferente al definido en el catálogo.

---

# 15. Relación con AI Service

La IA podrá recibir el rango autorizado como parte del contexto necesario para realizar una recomendación.

Ejemplo:

```
{
  "final_category": "Configurar punto de red Usuarios y/o proyectos",
  "minimum_minutes": 30,
  "maximum_minutes": 40
}
```

La IA podrá recomendar:

```
30 ≤ recommended_minutes ≤ 40
```

La IA no podrá:

- Modificar el mínimo.
- Modificar el máximo.
- Crear una categoría.
- Crear un rango.
- Ampliar un rango.
- Reducir un rango.
- Establecer reglas nuevas.

La validación definitiva deberá realizarse fuera del modelo de IA.

---

# 16. Responsabilidad del Business Catalog Service

El `Business Catalog Service` será responsable de:

- Cargar el catálogo.
- Validar su estructura.
- Validar las configuraciones.
- Consultar configuraciones.
- Determinar si una categoría está configurada.
- Obtener el rango autorizado.
- Exponer la información al resto de componentes mediante sus interfaces correspondientes.

No será responsable de:

- Calcular tiempos.
- Generar descripciones.
- Ejecutar IA.
- Procesar casos.
- Crear estimaciones.
- Modificar automáticamente el catálogo.

---

# 17. Operaciones Conceptuales

El `Business Catalog Service` deberá proporcionar conceptualmente operaciones como:

### Obtener configuración

```
get_time_configuration(final_category)
```

Permite obtener la configuración activa asociada a una categoría.

---

### Validar categoría

```
is_category_configured(final_category)
```

Determina si existe una configuración activa y válida.

---

### Obtener rango

```
get_allowed_range(final_category)
```

Retorna conceptualmente:

```
{
  "minimum_minutes": 30,
  "maximum_minutes": 40
}
```

---

### Obtener categorías activas

```
get_active_categories()
```

Retorna las categorías disponibles para procesamiento.

> Estos nombres representan operaciones conceptuales. La definición concreta de clases, interfaces y métodos pertenece al diseño técnico.
> 

---

# 18. Reglas del Catálogo

### RCT-01 — Categoría obligatoria

Toda configuración deberá contener una categoría final.

### RCT-02 — Tiempo mínimo obligatorio

Toda configuración deberá definir un tiempo mínimo.

### RCT-03 — Tiempo máximo obligatorio

Toda configuración deberá definir un tiempo máximo.

### RCT-04 — Rango válido

Toda configuración deberá cumplir:

```
minimum_minutes ≤ maximum_minutes
```

### RCT-05 — Valores positivos

Los tiempos deberán ser mayores que cero.

```
minimum_minutes > 0
maximum_minutes > 0
```

### RCT-06 — Configuración activa

Solo configuraciones activas podrán utilizarse durante el procesamiento.

### RCT-07 — Categoría única activa

Una categoría no deberá tener múltiples configuraciones activas simultáneamente.

### RCT-08 — Categoría final

La búsqueda deberá realizarse exclusivamente utilizando:

```
Case.final_category
```

### RCT-09 — IA limitada

La IA no podrá modificar los rangos definidos en el catálogo.

### RCT-10 — Sin modificación automática

El procesamiento de casos no podrá modificar el catálogo.

### RCT-11 — Catálogo centralizado

El catálogo deberá ser consultado exclusivamente mediante el `Business Catalog Service`.

### RCT-12 — Categoría no configurada

Una categoría sin configuración activa no podrá continuar hacia el `Estimation Engine`.

### RCT-13 — Gestión de Casos no calcula tiempos

Gestión de Casos únicamente valida la disponibilidad de una configuración activa.

### RCT-14 — Estimation Engine respeta el rango

Toda estimación final deberá respetar:

```
minimum_minutes
≤
estimated_minutes
≤
maximum_minutes
```

---

# 19. Validaciones del Catálogo

El `Business Catalog Service` deberá validar como mínimo:

### Estructura

- Existencia de las columnas obligatorias.
- Tipos de datos correctos.
- Registros correctamente formados.

### Categorías

- Categoría no vacía.
- No existencia de duplicados activos.

### Tiempos

- Mínimo definido.
- Máximo definido.
- Valores positivos.
- Mínimo menor o igual al máximo.

### Estado

El campo `active` deberá contener un valor válido:

```
true / false
```

Una configuración que no supere estas validaciones no deberá estar disponible para el procesamiento.

---

# 20. Persistencia

Para V1, el catálogo podrá mantenerse como archivo dentro de:

```
business_catalogs/
│
├── catalogo_estados.xlsx
├── catalogo_tiempos.xlsx
└── catalogo_responsables.xlsx
```

El archivo deberá ser leído únicamente por:

```
Business Catalog Service
```

Los demás módulos no deberán acceder directamente al archivo.

---

# 21. Errores de Configuración

El sistema deberá poder identificar problemas como:

### `CATALOG_NOT_FOUND`

El archivo del catálogo no existe.

### `INVALID_CATALOG_STRUCTURE`

La estructura del catálogo no cumple el contrato.

### `INVALID_TIME_RANGE`

El mínimo es mayor que el máximo o el rango contiene valores inválidos.

### `DUPLICATE_ACTIVE_CATEGORY`

Existe más de una configuración activa para una misma categoría.

### `CATEGORY_NOT_CONFIGURED`

La categoría del caso no tiene configuración activa.

---

# 22. Código de Rechazo de Caso

Cuando una categoría no tenga configuración activa, el código utilizado por el procesamiento del caso deberá ser:

```
CATEGORIA_NO_CONFIGURADA
```

Este código pertenece al conjunto de códigos de rechazo definido por el contrato de API y el modelo de datos.

La diferencia es:

```
CATEGORY_NOT_CONFIGURED
```

→ error interno/configuración del `Business Catalog Service`.

Mientras:

```
CATEGORIA_NO_CONFIGURADA
```

→ rechazo del caso durante una ejecución.

---

# 23. Integración con otros componentes

| Componente | Uso del Catálogo |
| --- | --- |
| Gestión de Casos | Verificar que `final_category` esté configurada. |
| Business Catalog Service | Acceso y validación del catálogo. |
| Estimation Engine | Obtener el rango autorizado. |
| AI Service | Recibir el rango como restricción. |
| Case Context Builder | Incorporar información autorizada al contexto cuando corresponda. |
| Frontend | No deberá consultar directamente el catálogo. |
| Export Service | Puede utilizar información del resultado, pero no deberá modificar el catálogo. |

---

# 24. Reglas Arquitectónicas

### RA-CT-01

Ningún módulo podrá leer directamente:

```
catalogo_tiempos.xlsx
```

### RA-CT-02

Toda consulta deberá realizarse mediante:

```
Business Catalog Service
```

### RA-CT-03

El catálogo será la fuente oficial de los rangos autorizados.

### RA-CT-04

Los rangos no deberán estar codificados directamente en los módulos.

Incorrecto:

```
if final_category == "...":
    minimum = 30
    maximum = 60
```

Correcto:

```
Estimation Engine
       ↓
Business Catalog Service
       ↓
Catálogo de Tiempos
       ↓
Rango autorizado
```

### RA-CT-05

La modificación de un rango no deberá requerir cambios en el código fuente.

---

# 25. Administración del Catálogo en V1

La V1 **no tendrá una interfaz de administración de catálogos**.

Los cambios al catálogo se realizarán sobre la fuente configurada y deberán respetar las validaciones establecidas.

Por ejemplo, modificar:

```
30 - 60
```

a:

```
40 - 60
```

no deberá requerir modificar el código de BOT-COMProject.

---

# 26. Relación con el Modelo de Datos

El Catálogo de Tiempos **no se almacenará como parte de `Case`**.

El `Case` únicamente conserva:

```
final_category
```

Durante el procesamiento:

```
Case.final_category
        ↓
Business Catalog Service
        ↓
Configuración de tiempo
        ↓
Estimation Engine
        ↓
Estimation
```

Los valores del catálogo que sean necesarios para la trazabilidad del resultado deberán quedar registrados en `Estimation`, de acuerdo con el diseño correspondiente del `Estimation Engine`.

> El catálogo continúa siendo la fuente de configuración; `Estimation` representa el resultado concreto de una ejecución.
> 

---

# 27. Evolución Futura

El catálogo podrá evolucionar para soportar:

- Versionado de reglas.
- Vigencia de configuraciones.
- Fecha de inicio.
- Fecha de finalización.
- Auditoría de cambios.
- Administración desde la interfaz.
- Persistencia en PostgreSQL.
- Historial de modificaciones.
- Reglas diferentes por tipo de proyecto.
- Reglas diferentes según otras características del caso.

Por ejemplo:

```
Categoría
Mínimo
Máximo
Activo
Fecha inicio
Fecha fin
Versión
```

Estas funcionalidades no forman parte de V1.

---

# 28. Relación con otros documentos

| Documento | Relación |
| --- | --- |
| **Project Charter** | Define que la estimación debe respetar rangos autorizados. |
| **Análisis del Proceso de Negocio** | Define el uso de la categoría final y el rango autorizado. |
| **Mapa de Módulos** | Define el `Business Catalog Service` como punto central de consulta. |
| **Diseño de Gestión de Casos** | Define que una categoría no configurada no continúa. |
| **Estimation Engine** | Utiliza el rango para determinar el tiempo. |
| **AI Service** | Recibe el rango como restricción y no puede modificarlo. |
| **Case Contract** | Define la categoría final utilizada por el proceso. |
| **Catálogo de Estados** | Define qué estados permiten continuar al caso. |
| **Catálogo de Responsables** | Define los responsables disponibles. |
| **Modelo de Datos** | Define la persistencia de la estimación y su trazabilidad. |
| **API Contract** | Define los códigos de rechazo expuestos por la API. |

---

# 29. Fuente de Verdad

El **Catálogo de Tiempos** es la fuente de verdad para:

```
Categoría Final
        ↓
Rango mínimo
Rango máximo
        ↓
Autorización del tiempo
```

No es fuente de verdad para:

```
Tiempo final
Descripción
Solución
Estado del caso
Responsable
Resultado de IA
```

---

# 30. Definición V1

La definición oficial del Catálogo de Tiempos de BOT-COMProject V1 es:

> **El Catálogo de Tiempos de BOT-COMProject V1 contiene las categorías finales configuradas y sus respectivos rangos mínimo y máximo de tiempo. Estos rangos representan las restricciones oficiales que deberá respetar el Estimation Engine. Gestión de Casos únicamente verifica que la categoría final posea una configuración activa. La IA podrá recomendar un tiempo dentro del rango, pero no podrá modificar, crear ni ampliar las reglas definidas en el catálogo.**
>