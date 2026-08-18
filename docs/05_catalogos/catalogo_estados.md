**Proyecto:** BOT-COMProject

**Versión:** 1.1

**Estado:** Definido

**Tipo:** Catálogo de Negocio

---

# 1. Objetivo

Definir los estados de los casos que pueden ser recibidos desde el Maestro de Casos de Aranda y establecer cuáles de ellos son procesables por BOT-COMProject.

El catálogo constituye la **fuente oficial de configuración de estados** utilizada por el sistema.

Los módulos no deberán definir directamente qué estados son procesables.

La consulta deberá realizarse mediante:

```
Módulo
   ↓
Catalog Service
   ↓
Catálogo de Estados
   ↓
Estado + configuración
```

---

# 2. Responsabilidad

El Catálogo de Estados es responsable de definir:

- Los estados reconocidos por el sistema.
- Si un estado está activo.
- Si un estado permite procesar un caso.
- Las observaciones asociadas al estado.

El catálogo **no procesa casos**.

La decisión de continuar o excluir un caso corresponde a `Gestión de Casos`, utilizando la información proporcionada por `Catalog Service`.

---

# 3. Estructura del Catálogo

Cada registro del catálogo deberá contener como mínimo:

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `estado` | String | Sí | Nombre del estado proveniente de Aranda |
| `activo` | Boolean | Sí | Indica si la configuración está habilitada |
| `procesable` | Boolean | Sí | Indica si los casos en este estado pueden continuar |
| `observaciones` | String | No | Información adicional sobre el estado |

---

# 4. Concepto de Estado Activo

El campo:

```
activo
```

determina si la configuración del estado está actualmente habilitada.

Ejemplo:

```
Solucionado
activo = true
procesable = true
```

Un estado puede existir en el catálogo pero encontrarse deshabilitado:

```
Solucionado
activo = false
procesable = true
```

En este caso, el estado **no deberá considerarse procesable**, debido a que su configuración no está activa.

Por lo tanto:

```
activo = true
+
procesable = true
        ↓
Estado procesable
```

Mientras que:

```
activo = false
        ↓
Estado no disponible
        ↓
No procesable
```

---

# 5. Catálogo Inicial V1

La configuración inicial será:

| Estado | Activo | Procesable | Observaciones |
| --- | --- | --- | --- |
| Solucionado | ✅ | ✅ | Caso listo para procesamiento |
| Cerrado | ✅ | ✅ | Caso finalizado y válido para procesamiento |
| Pendiente | ✅ | ❌ | Espera acciones adicionales |
| Abierto | ✅ | ❌ | Caso en atención |
| Cancelado | ✅ | ❌ | Caso descartado |

Estos valores representan la configuración inicial de V1.

El comportamiento deberá depender del catálogo y no de valores escritos directamente en el código.

---

# 6. Estados Procesables V1

Para la primera versión:

```
Solucionado → Procesable
Cerrado     → Procesable
```

Por lo tanto:

```
Estado recibido
       │
       ▼
Catalog Service
       │
       ▼
Catálogo de Estados
       │
       ├── Solucionado ──► Procesable
       │
       ├── Cerrado ──────► Procesable
       │
       ├── Pendiente ────► No procesable
       │
       ├── Abierto ──────► No procesable
       │
       └── Cancelado ────► No procesable
```

---

# 7. Estado Desconocido

Si el Maestro de Casos contiene un estado que no existe en el catálogo, el sistema deberá considerarlo **no procesable**.

Ejemplo:

```
Estado recibido:

"En espera de aprobación"
```

Si no existe en el catálogo:

```
Estado
   ↓
Catalog Service
   ↓
No encontrado
   ↓
ESTADO_NO_CONFIGURADO
   ↓
No procesable
```

El caso no deberá continuar hacia el `Estimation Engine`.

El sistema deberá conservar el motivo para permitir su revisión.

---

# 8. Estado Inactivo

Si el estado existe en el catálogo pero:

```
activo = false
```

el caso tampoco podrá continuar.

Ejemplo:

```
Estado:
Solucionado

activo:
false

procesable:
true
```

Resultado:

```
NO PROCESABLE
Motivo: ESTADO_NO_ACTIVO
```

La configuración `activo` tiene prioridad sobre `procesable`.

---

# 9. Reglas de Evaluación

La evaluación de un estado deberá seguir el siguiente orden:

```
Estado recibido
       │
       ▼
¿Existe en catálogo?
       │
    ┌──┴──┐
   No     Sí
   │       │
   ▼       ▼
No      ¿Activo?
procesable │
         ┌─┴─┐
        No   Sí
        │     │
        ▼     ▼
       No   ¿Procesable?
       │       │
       │    ┌──┴──┐
       │   No     Sí
       │   │       │
       ▼   ▼       ▼
     No procesable
```

En términos de decisión:

```
Existe
AND
Activo
AND
Procesable
=
Estado procesable
```

---

# 10. Integración con Catalog Service

`Catalog Service` será el único componente autorizado para consultar este catálogo.

La interacción conceptual será:

```
Case Filter
     │
     ▼
Catalog Service
     │
     ▼
Catálogo de Estados
     │
     ▼
Resultado
```

El resultado deberá permitir determinar como mínimo:

```
estado
activo
procesable
```

---

# 11. Responsabilidad de Gestión de Casos

`Gestión de Casos` no deberá contener una lista propia de estados procesables.

No se deberá implementar lógica como:

```
if estado in ["Solucionado", "Cerrado"]:
```

La decisión deberá realizarse mediante `Catalog Service`.

Conceptualmente:

```
Case Filter
     │
     ▼
Catalog Service
     │
     ▼
is_processable("Solucionado")
     │
     ▼
True
```

Esto permite modificar la configuración sin modificar el código de `Gestión de Casos`.

---

# 12. Manejo de Casos No Procesables

Cuando un caso tenga un estado que no permita continuar, el sistema deberá marcarlo como no procesable.

Ejemplos:

```
Caso 1234
Estado: Pendiente
Motivo: ESTADO_NO_PROCESABLE
```

```
Caso 1235
Estado: En espera de aprobación
Motivo: ESTADO_NO_CONFIGURADO
```

```
Caso 1236
Estado: Solucionado
Motivo: ESTADO_NO_ACTIVO
```

Un caso no procesable no deberá bloquear el procesamiento de los demás casos válidos de la misma ejecución.

---

# 13. Códigos de Resultado

Para facilitar la trazabilidad, se establecen los siguientes motivos:

| Código | Significado |
| --- | --- |
| `ESTADO_NO_CONFIGURADO` | El estado no existe en el catálogo |
| `ESTADO_NO_ACTIVO` | El estado existe pero su configuración está inactiva |
| `ESTADO_NO_PROCESABLE` | El estado está activo pero no permite procesamiento |

Estos códigos deberán utilizarse de forma consistente en los módulos que reporten casos no procesables.

---

# 14. Normalización del Estado

El valor recibido desde Excel podrá ser normalizado por `Case Normalizer` antes de consultar el catálogo.

Ejemplo:

```
Excel:

" solucionado "
```

Después de normalización:

```
"Solucionado"
```

La normalización no deberá cambiar el significado del estado.

El catálogo deberá mantener el valor oficial utilizado para las consultas.

---

# 15. Reglas del Catálogo

### CE-001 — Fuente oficial

El Catálogo de Estados es la fuente oficial para determinar la configuración de los estados.

### CE-002 — Acceso centralizado

Los módulos no podrán acceder directamente al archivo o almacenamiento del catálogo.

### CE-003 — Estado activo

Un estado únicamente podrá considerarse disponible cuando `activo = true`.

### CE-004 — Estado procesable

Un estado únicamente podrá considerarse procesable cuando:

```
activo = true
AND
procesable = true
```

### CE-005 — Estado desconocido

Un estado que no exista en el catálogo será considerado no procesable.

### CE-006 — Sin reglas duplicadas

Los módulos consumidores no deberán mantener listas independientes de estados procesables.

### CE-007 — No modificación automática

BOT-COMProject no podrá crear o modificar automáticamente estados del catálogo durante el procesamiento.

### CE-008 — Configuración externa

Cambiar la condición `procesable` de un estado deberá poder realizarse mediante la configuración del catálogo sin modificar la lógica de `Gestión de Casos`.

---

# 16. Responsabilidades

| Componente | Responsabilidad |
| --- | --- |
| Excel Service | Extraer el estado del Excel |
| Case Normalizer | Normalizar el valor |
| Catalog Service | Consultar la configuración |
| Gestión de Casos | Aplicar la decisión al caso |
| Case Filter | Excluir o permitir continuar |
| Estimation Engine | Recibir únicamente casos que ya superaron esta etapa |
| AI Service | No consulta directamente el catálogo |

---

# 17. Exclusiones

El Catálogo de Estados no será responsable de:

- Filtrar casos.
- Procesar casos.
- Determinar tiempos.
- Generar descripciones.
- Consultar Ollama.
- Modificar casos.
- Registrar información en COMProject.
- Crear automáticamente nuevos estados.
- Seleccionar responsables.

---

# 18. Ubicación

La implementación inicial podrá mantener el catálogo como archivo configurable:

```
backend/
│
├── business_catalogs/
│   └── catalogo_estados.xlsx
│
└── application/
    └── services/
        └── catalog_service.py
```

La ubicación física del catálogo es una decisión de infraestructura y no deberá formar parte del contrato funcional.

---

# 19. Evolución Futura

El catálogo podrá incorporar posteriormente:

- Nuevos estados provenientes de Aranda.
- Estados temporalmente inactivos.
- Nuevas configuraciones de procesamiento.
- Información adicional para clasificación.
- Versionamiento de configuraciones.

Estas extensiones no deberán modificar la responsabilidad fundamental del catálogo.

---

# 20. Consistencia Documental

Este documento deberá mantenerse alineado con:

| Documento | Relación |
| --- | --- |
| Project Charter | Define que los estados procesables dependen del catálogo |
| Análisis del Proceso de Negocio | Define la identificación de casos procesables |
| Mapa de Módulos | Define la responsabilidad de `Catalog Service` |
| Diseño de Gestión de Casos | Define cómo se utiliza el catálogo |
| Case Contract | Define el campo `estado` |
| Estimation Engine | Recibe casos que superaron la gestión de casos |
| Modelo de Datos | Deberá representar la configuración del catálogo cuando corresponda |

---

# 21. Regla de Consistencia

Si se modifica la configuración de un estado:

```
Cambio en Catálogo de Estados
          ↓
Validar impacto
          ↓
Actualizar documentación si cambia el comportamiento
          ↓
Actualizar catálogo
          ↓
Ejecutar pruebas
```

La modificación de la configuración de un estado **no debería requerir cambios en el código** mientras la estructura del catálogo y sus reglas permanezcan compatibles.

---

# 22. Definición Oficial V1

La definición oficial del Catálogo de Estados para V1 es:

> **El Catálogo de Estados define los estados reconocidos por BOT-COMProject y determina, mediante las propiedades `activo` y `procesable`, cuáles pueden continuar en el procesamiento. En V1, los estados `Solucionado` y `Cerrado` son procesables. Los estados desconocidos, inactivos o configurados como no procesables no podrán continuar hacia las etapas posteriores del proceso.**
>