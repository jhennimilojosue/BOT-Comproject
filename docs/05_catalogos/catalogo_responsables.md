**Proyecto:** BOT-COMProject

**Versión:** 1.0

**Estado:** Definido

**Tipo:** Catálogo de Negocio

---

# 1. Objetivo

El **Catálogo de Responsables** define las personas disponibles para ejecutar el procesamiento de casos en BOT-COMProject.

Su función es proporcionar una fuente centralizada de responsables que puedan ser seleccionados por el usuario antes de iniciar una ejecución.

El catálogo permitirá que el sistema:

- Identifique los responsables habilitados.
- Permita seleccionar un responsable antes del procesamiento.
- Valide que el responsable seleccionado sea válido.
- Relacione los casos del Maestro de Casos mediante el campo `Responsible Name`.
- Mantenga desacoplada la información de los responsables de la lógica del sistema.

---

# 2. Alcance V1

Para la primera versión de BOT-COMProject:

- Existirán **cinco responsables configurados**.
- Los responsables estarán definidos previamente en el catálogo.
- El usuario deberá seleccionar un responsable antes de procesar los casos.
- Solo podrán seleccionarse responsables que se encuentren habilitados.
- El sistema no permitirá crear nuevos responsables desde la interfaz.
- El catálogo será utilizado únicamente para determinar los responsables disponibles para el procesamiento.

---

# 3. Principios

El catálogo deberá cumplir los siguientes principios:

- Fuente única de verdad para los responsables disponibles.
- No duplicar la información en el código fuente.
- Fácil mantenimiento.
- Validación mediante `Catalog Service`.
- Separación entre datos del catálogo y lógica de negocio.
- Posibilidad de evolucionar posteriormente a una fuente de datos persistente.

---

# 4. Estructura del Catálogo

La estructura propuesta para V1 será:

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `id` | Integer | Sí | Identificador único del responsable dentro del catálogo. |
| `nombre` | String | Sí | Nombre del responsable. |
| `activo` | Boolean | Sí | Indica si puede ser seleccionado. |
| `observaciones` | String | No | Información adicional. |

---

# 5. Catálogo Inicial

La V1 contará con cinco responsables.

| ID | Nombre | Activo | Observaciones |
| --- | --- | --- | --- |
| 1 | Responsable 1 | Sí | Responsable habilitado para procesamiento. |
| 2 | Responsable 2 | Sí | Responsable habilitado para procesamiento. |
| 3 | Responsable 3 | Sí | Responsable habilitado para procesamiento. |
| 4 | Responsable 4 | Sí | Responsable habilitado para procesamiento. |
| 5 | Responsable 5 | Sí | Responsable habilitado para procesamiento. |

> Los nombres reales de los cinco responsables deberán incorporarse cuando estén definidos oficialmente.
> 

---

# 6. Relación con el Maestro de Casos

El catálogo se relacionará con la información proveniente del Maestro de Casos mediante el campo:

```
Responsible Name
```

El flujo será:

```
Catálogo de Responsables
          │
          ▼
Responsable seleccionado
          │
          ▼
Case Service
          │
          ▼
Responsible Name
          │
          ▼
Casos correspondientes
```

### Ejemplo

Si el usuario selecciona:

```
Carlos Rodríguez
```

el sistema deberá identificar los casos cuyo:

```
Responsible Name = Carlos Rodríguez
```

---

# 7. Selección del Responsable

La selección del responsable será obligatoria antes de iniciar el procesamiento.

El flujo será:

```
Usuario
   │
   ▼
Consultar responsables activos
   │
   ▼
Mostrar responsables disponibles
   │
   ▼
Usuario selecciona responsable
   │
   ▼
Validar responsable
   │
   ▼
Procesar casos
```

Si no existe un responsable seleccionado, el sistema **no deberá iniciar el procesamiento**.

---

# 8. Responsables Activos e Inactivos

El campo `activo` permitirá controlar la disponibilidad de cada responsable.

### Responsable activo

```
activo = true
```

Puede aparecer en la interfaz y ser seleccionado.

### Responsable inactivo

```
activo = false
```

No deberá aparecer entre las opciones disponibles para una nueva ejecución.

Sin embargo, su registro podrá mantenerse en el catálogo para conservar trazabilidad y evitar eliminar información innecesariamente.

---

# 9. Reglas del Catálogo

### RCR-01 — Responsable obligatorio

Toda ejecución deberá tener un responsable seleccionado antes de iniciar el procesamiento.

### RCR-02 — Responsable válido

El responsable seleccionado deberá existir en el Catálogo de Responsables.

### RCR-03 — Responsable activo

Solo podrán seleccionarse responsables cuyo campo `activo` sea verdadero.

### RCR-04 — Cinco responsables V1

La V1 tendrá cinco responsables configurados inicialmente.

### RCR-05 — Identificación de casos

La relación entre el responsable seleccionado y los casos se realizará mediante el campo `Responsible Name` del Maestro de Casos.

### RCR-06 — Sin selección automática

El sistema no seleccionará automáticamente un responsable.

La selección deberá realizarla el usuario.

### RCR-07 — Sin creación en V1

La V1 no permitirá crear nuevos responsables desde la aplicación.

### RCR-08 — Catálogo centralizado

La información de los responsables deberá consultarse mediante el `Catalog Service`.

Los módulos consumidores no podrán acceder directamente al archivo o estructura de persistencia del catálogo.

### RCR-09 — No modificación durante el procesamiento

El procesamiento de casos no podrá modificar la información del Catálogo de Responsables.

---

# 10. Consulta mediante Catalog Service

El acceso al catálogo seguirá el flujo:

```
Case Service
      │
      ▼
Catalog Service
      │
      ▼
Catálogo de Responsables
      │
      ▼
Responsables activos
```

El `Catalog Service` será responsable de:

- Leer el catálogo.
- Validar su estructura.
- Obtener responsables activos.
- Buscar un responsable específico.
- Validar que un responsable exista.
- Validar que se encuentre activo.

---

# 11. Operaciones Requeridas

El servicio de catálogo deberá permitir conceptualmente las siguientes operaciones:

### Obtener responsables disponibles

```
get_active_responsibles()
```

Retorna los responsables que pueden ser seleccionados.

### Buscar responsable

```
get_responsible(id)
```

Obtiene un responsable específico.

### Validar responsable

```
is_valid_responsible(id)
```

Determina si el responsable existe y está habilitado.

### Buscar por nombre

```
find_responsible_by_name(nombre)
```

Permite relacionar la información del catálogo con `Responsible Name`.

> Los nombres anteriores representan operaciones conceptuales. La definición de los métodos concretos pertenece al diseño técnico y no a este catálogo.
> 

---

# 12. Integración con Gestión de Casos

Gestión de Casos utilizará este catálogo para validar el responsable seleccionado.

El flujo será:

```
Responsable seleccionado
          │
          ▼
Catalog Service
          │
          ├── ¿Existe?
          │       │
          │      Sí
          │       ▼
          ├── ¿Está activo?
          │       │
          │      Sí
          │       ▼
          │
          ▼
    Gestión de Casos
          │
          ▼
Filtrar por Responsible Name
```

Si el responsable no es válido, el procesamiento deberá detenerse antes de comenzar el procesamiento de los casos.

---

# 13. Integración con Frontend

El Frontend no deberá contener una lista de responsables codificada manualmente.

La información deberá obtenerse del backend:

```
Frontend
   │
   ▼
API
   │
   ▼
Catalog Service
   │
   ▼
Responsables activos
```

Esto permitirá modificar los responsables disponibles sin tener que modificar el código del Frontend.

---

# 14. Persistencia

Para V1, el catálogo podrá mantenerse como un archivo dentro de la estructura de catálogos de negocio:

```
catalog_service/
│
├── catalogo_estados.xlsx
├── catalogo_tiempos.xlsx
└── catalogo_responsables.xlsx
```

El acceso al archivo deberá realizarse exclusivamente mediante:

```
Catalog Service
```

Los módulos del sistema no deberán leer directamente el archivo.

---

# 15. Validaciones del Catálogo

Antes de utilizar el catálogo, el `Catalog Service` deberá validar como mínimo:

- Existencia del archivo.
- Estructura esperada.
- Identificador válido.
- Nombre obligatorio.
- Ausencia de identificadores duplicados.
- Ausencia de responsables duplicados.
- Valor válido de `activo`.
- Existencia de los cinco responsables configurados para V1.

Si el catálogo no cumple la estructura requerida, deberá generarse un error de configuración y el sistema no deberá utilizar información incompleta.

---

# 16. Relación con otros documentos

| Documento | Relación |
| --- | --- |
| **Project Charter** | Define que V1 tendrá cinco responsables configurados. |
| **Análisis del Proceso de Negocio** | Define la selección del responsable antes del procesamiento. |
| **Mapa de Módulos** | Define el uso del Catalog Service. |
| **Diseño de Gestión de Casos** | Define el filtrado mediante `Responsible Name`. |
| **Case Contract** | Define la estructura del responsable dentro del caso. |
| **Catálogo de Estados** | Define los estados procesables. |
| **Catálogo de Tiempos** | Define los rangos de estimación. |

---

# 17. Exclusiones V1

El Catálogo de Responsables no contempla:

- Administración de usuarios.
- Login.
- Autenticación.
- Roles.
- Permisos.
- Creación de responsables desde la interfaz.
- Eliminación de responsables desde la interfaz.
- Asignación automática de responsables.
- Integración directa con COMProject.

Estas funcionalidades podrán evaluarse en versiones posteriores.

---

# 18. Evolución Futura

El catálogo podrá evolucionar para incorporar información adicional, por ejemplo:

```
Responsable
    │
    ├── Nombre
    ├── Activo
    ├── Área
    ├── Cargo
    └── Identificador externo
```

También podría migrarse posteriormente desde Excel hacia PostgreSQL sin modificar los módulos consumidores:

```
V1

Case Service
     ↓
Catalog Service
     ↓
Excel
```

```
Futuro

Case Service
     ↓
Catalog Service
     ↓
PostgreSQL
```

La lógica de consumo deberá permanecer desacoplada del origen de los datos.

---

# 19. Definición de V1

La definición oficial del catálogo es:

> **El Catálogo de Responsables de BOT-COMProject V1 contiene los cinco responsables habilitados para ejecutar el procesamiento de casos. El usuario deberá seleccionar uno de ellos antes de iniciar una ejecución, y el sistema utilizará el campo `Responsible Name` del Maestro de Casos para identificar los casos correspondientes.**
>