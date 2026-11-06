**Versión:** 1.2

**Estado:** Definido

**Tipo:** MVP / V1

**Documento:** Project Charter

---

# 1. Información General

## Nombre del Proyecto

**BOT-COMProject**

## Tipo de Proyecto

Sistema de automatización de procesos mediante reglas de negocio e Inteligencia Artificial local.

## Propósito

Automatizar el procesamiento semanal de los casos registrados en Aranda para generar una propuesta estandarizada de tiempo y descripción de las actividades realizadas, facilitando posteriormente su registro en COMProject.

## Integrantes

| Integrante | Rol |
| --- | --- |
| Integrante 1 | Arquitecto de Software |
| Integrante 2 | Backend Developer & IA |
| Integrante 3 | Frontend Developer |

---

# 2. Descripción del Proyecto

BOT-COMProject es un sistema diseñado para automatizar parte del proceso semanal de preparación de horas de trabajo para COMProject a partir del maestro de casos exportado desde Aranda.

El sistema permitirá cargar el maestro de casos, seleccionar el responsable cuyos casos serán procesados y analizar únicamente los casos que cumplan las condiciones establecidas por las reglas de negocio.

Para cada caso procesable, el sistema utilizará **únicamente la categoría final** registrada en el maestro de casos para consultar un rango de tiempo previamente definido en un catálogo centralizado.

El **Estimation Engine** será responsable de coordinar el proceso de estimación. Consultará el rango autorizado mediante el `Catalog Service`, solicitará al `AI Service` una recomendación y posteriormente validará que dicha recomendación se encuentre dentro del rango permitido.

La Inteligencia Artificial **no define ni modifica las reglas de negocio**. Su función será generar una recomendación basada en el contexto proporcionado y generar una descripción profesional de la actividad realizada.

La V1 finalizará cuando el sistema haya procesado los casos y generado:

- Caso.
- Responsable.
- Proyecto.
- Categoría.
- Tiempo estimado.
- Descripción profesional.
- Información necesaria para una posterior exportación o integración.

La integración automática con COMProject queda fuera del alcance de la primera versión.

---

# 3. Problema del Negocio

Actualmente, el registro semanal de horas en COMProject requiere un proceso manual en el que el responsable debe revisar los casos gestionados durante la semana y preparar la información necesaria para reportar el trabajo realizado.

El proceso puede implicar:

- Descargar el maestro de casos desde Aranda.
- Revisar los casos de la semana.
- Identificar los casos correspondientes al responsable.
- Revisar el estado de cada caso.
- Identificar el proyecto.
- Revisar la categoría final.
- Determinar el tiempo aproximado dedicado.
- Redactar una descripción de la actividad.
- Preparar la información para COMProject.

Este procedimiento consume tiempo y puede generar diferencias en la forma en que cada persona estima y describe sus actividades.

---

# 4. Justificación

BOT-COMProject busca reducir el trabajo manual mediante la automatización del procesamiento de los casos y la centralización de las reglas utilizadas para determinar los tiempos.

Los principales beneficios esperados son:

- Reducción del tiempo dedicado al procesamiento semanal.
- Disminución de errores manuales.
- Estandarización de las descripciones.
- Mayor consistencia en la asignación de tiempos.
- Centralización de reglas de negocio.
- Trazabilidad del procesamiento.
- Arquitectura preparada para futuras integraciones.
- Posibilidad de incorporar posteriormente la integración directa con COMProject.

---

# 5. Objetivo General

Desarrollar un sistema capaz de procesar los casos registrados en el maestro de Aranda, identificar los casos correspondientes a un responsable seleccionado, determinar los casos procesables y generar para cada uno una estimación de tiempo y una descripción profesional utilizando reglas de negocio e Inteligencia Artificial local.

---

# 6. Objetivos Específicos

- Procesar el archivo maestro de casos de Aranda.
- Validar la estructura y consistencia del archivo.
- Extraer únicamente la información requerida por el sistema.
- Permitir seleccionar uno de los responsables de los cuatro grupos de trabajo configurados.
- Identificar los casos correspondientes al responsable seleccionado.
- Procesar únicamente los estados definidos como procesables.
- Utilizar únicamente la categoría final del caso.
- Consultar el rango de tiempo correspondiente a la categoría.
- Utilizar el Estimation Engine para obtener una recomendación de tiempo.
- Validar que la recomendación se encuentre dentro del rango autorizado.
- Generar una descripción profesional mediante IA local.
- Presentar los resultados para revisión.
- Permitir la exportación de los resultados.
- Mantener la arquitectura preparada para una futura integración con COMProject.

---

# 7. Alcance V1

## 7.1 Gestión del archivo

La primera versión permitirá:

- Importar el maestro de casos de Aranda.
- Validar el formato del archivo.
- Identificar las columnas requeridas.
- Extraer la información necesaria.
- Procesar la información mediante el `Excel Service`.
- Registrar el archivo procesado.

---

## 7.2 Selección del responsable

El sistema tendrá un catálogo de **cuatro grupos de trabajo con sus responsables**.

El usuario deberá seleccionar uno antes de iniciar el procesamiento.

El responsable seleccionado se utilizará para filtrar los casos mediante el campo `Responsible Name` presente en el maestro de casos.

Flujo:

```
Responsible Catalog
        ↓
Responsable seleccionado
        ↓
Case.responsible_name
        ↓
Casos correspondientes
```

El `Responsible Catalog` será considerado un catálogo del sistema y su acceso deberá realizarse exclusivamente mediante el `Catalog Service`.

---

## 7.3 Gestión de casos

El sistema permitirá:

- Almacenar los casos.
- Filtrar casos por responsable.
- Validar estados.
- Identificar proyectos.
- Identificar la categoría final.
- Consultar la información original del caso.
- Preparar los casos para el proceso de estimación.

---

## 7.4 Estimación

El sistema utilizará un catálogo centralizado de categorías y rangos de tiempo.

Ejemplo:

```
Cableado puntos de red en sedes Comware o proyectos clientes
30 - 60 minutos

Configurar punto de red Usuarios y/o proyectos
30 - 40 minutos

Configurar segmento de red en los enlaces de comunicaciones
60 - 90 minutos
```

El proceso será:

```
Caso
 ↓
Categoría final
 ↓
Catalog Service
 ↓
Rango autorizado
 ↓
Estimation Engine
 ↓
AI Service
 ↓
Tiempo recomendado
 ↓
Estimation Engine
 ↓
Validación del rango
```

La recomendación deberá cumplir:

```
mínimo ≤ tiempo recomendado ≤ máximo
```

---

## 7.5 Descripción

El `AI Service` generará una descripción profesional utilizando la información disponible del caso.

La descripción generada por IA no deberá reemplazar ni modificar los datos originales provenientes del Excel.

---

## 7.6 Resultado

El sistema mostrará como mínimo:

```
Caso
Responsable
Proyecto
Categoría
Estado
Tiempo estimado
Descripción generada
```

---

## 7.7 Exportación

La V1 podrá generar un archivo con los resultados procesados para su utilización posterior.

La exportación no implica una integración automática con COMProject.

---

# 8. Fuera del Alcance de V1

La primera versión **no realizará**:

- Registro automático en COMProject.
- Modificación de información en Aranda.
- Creación de casos en Aranda.
- Resolución automática de incidentes.
- Administración de usuarios.
- Login.
- JWT.
- Roles.
- Permisos.
- Gestión de sesiones.
- Creación automática de nuevas reglas de negocio.
- Asignación de tiempos fuera de los rangos autorizados.
- Selección automática del responsable.
- Modificación de las reglas del catálogo mediante IA.

La integración directa con COMProject será considerada para una versión posterior.

---

# 9. Flujo General del Sistema

```
                         Inicio
                           │
                           ▼
                  Cargar maestro Excel
                           │
                           ▼
                     Excel Service
                           │
                           ▼
                 Validar estructura
                           │
                           ▼
                  Guardar información
                           │
                           ▼
               Seleccionar responsable
                           │
                           ▼
                    Procesar casos
                           │
                           ▼
             Filtrar por Responsible Name
                           │
                           ▼
                Validar estado del caso
                    │             │
                    │             │
               Procesable    No procesable
                    │             │
                    ▼             ▼
                Continuar       Ignorar
                    │
                    ▼
             Obtener categoría final
                    │
                    ▼
               Catalog Service
                    │
                    ▼
            Obtener rango autorizado
                    │
                    ▼
             Estimation Engine
                    │
                    ▼
                 AI Service
                 │         │
                 ▼         ▼
        Tiempo recomendado  Descripción
                 │         │
                 └────┬────┘
                      ▼
             Validar resultado
                      │
                      ▼
             Guardar resultado
                      │
                      ▼
              Mostrar resultados
                      │
                      ▼
                   Exportar
                      │
                      ▼
                     Fin
```

---

# 10. Orquestación del Proceso

El botón **"Procesar casos"** será la operación principal del sistema.

El frontend no realizará llamadas independientes para cada servicio.

El backend será responsable de orquestar el proceso completo.

Endpoint de aplicación:

```
POST /api/v1/cases/process
```

Este endpoint iniciará el caso de uso y coordinará internamente los servicios necesarios.

Conceptualmente:

```
Case Service
    │
    ├── Excel / datos procesados
    │
    ├── Catalog Service
    │
    ├── Case Repository
    │
    ├── Estimation Engine
    │       │
    │       ├── Catalog Service
    │       └── AI Service
    │
    └── Resultado
```

Los servicios internos no tendrán endpoints HTTP independientes para el frontend.

---

# 11. Reglas de Negocio Principales

## RN-001 — Estados procesables

Solo se procesarán casos cuyo estado esté definido como procesable en el **Catálogo de Estados**.

Actualmente:

```
Solucionado → Procesable
Cerrado     → Procesable
```

Los demás estados serán considerados no procesables.

---

## RN-002 — Responsable seleccionado

Antes de procesar los casos deberá seleccionarse uno de los responsables de los grupos de trabajo configurados.

---

## RN-003 — Responsible Name

El responsable asociado a cada caso será obtenido del campo:

```
Responsible Name
```

del maestro de casos.

---

## RN-004 — Filtrado por responsable

Solo se procesarán los casos cuyo `responsible_name` corresponda al responsable seleccionado.

---

## RN-005 — Categoría final

Para determinar el tiempo se utilizará **únicamente la categoría final registrada en el maestro de casos**.

No se utilizarán las subcategorías anteriores para determinar el tiempo.

---

## RN-006 — Categoría configurada

Toda categoría procesable deberá contar con una configuración válida en el **Catálogo de Tiempos**.

---

## RN-007 — Rango de tiempo

Cada categoría tendrá un rango de tiempo previamente definido por la organización.

Ejemplo:

```
30 - 60 minutos
```

---

## RN-008 — Estimación dentro del rango

El `Estimation Engine` deberá validar que toda recomendación de tiempo generada por el `AI Service` se encuentre dentro del rango establecido para la categoría.

```
mínimo ≤ recomendación ≤ máximo
```

Una recomendación fuera del rango no podrá convertirse en un resultado válido.

---

## RN-009 — Acceso centralizado a catálogos

Todos los catálogos de negocio serán administrados mediante un único `Catalog Service`.

Los demás módulos no podrán acceder directamente a las tablas o mecanismos de persistencia de los catálogos.

El flujo autorizado será:

```
Módulo
   ↓
Catalog Service
   ↓
Catálogo
```

---

## RN-010 — Información original

Los datos originales provenientes del Excel no deberán ser reemplazados por información generada por la IA.

La información generada deberá almacenarse como resultado derivado del procesamiento.

---

## RN-011 — IA local

La generación mediante IA se realizará utilizando **Ollama** y un modelo local configurado por el proyecto.

La IA:

- No define reglas de negocio.
- No modifica los catálogos.
- No establece rangos de tiempo.
- No puede generar tiempos válidos fuera del rango autorizado.
- Genera recomendaciones y contenido basado en el contexto proporcionado.

---

## RN-012 — Procesamiento completo

El usuario no deberá ejecutar manualmente cada etapa.

Al seleccionar el responsable y presionar **"Procesar casos"**, el backend deberá ejecutar el flujo completo.

---

## RN-013 — V1

La primera versión termina después de generar y almacenar:

```
Caso
+
Tiempo
+
Descripción
```

La integración automática con COMProject no forma parte de V1.

---

# 12. Arquitectura Conceptual

BOT-COMProject utilizará **Clean Architecture**.

La arquitectura conceptual será:

```
Frontend
    │
    ▼
API
    │
    ▼
Application
    │
    ├── Case Service
    ├── Excel Service
    ├── Catalog Service
    ├── Estimation Engine
    └── AI Service
            │
            ▼
          Ollama

    │
    ▼
Repositories
    │
    ▼
PostgreSQL
```

Los módulos deberán mantener responsabilidades independientes y evitar acoplamiento innecesario.

El acceso a los catálogos deberá realizarse exclusivamente mediante `Catalog Service`.

---

# 13. Módulos Principales

| Módulo | Responsabilidad |
| --- | --- |
| Excel Service | Extraer, validar y normalizar la información requerida del maestro. |
| Case Service | Orquestar el caso de uso y gestionar el procesamiento de casos. |
| Case Repository | Persistir y consultar la información de los casos. |
| Catalog Service | Consultar los catálogos y aplicar las reglas centralizadas asociadas a ellos. |
| Estimation Engine | Obtener el rango autorizado, solicitar una recomendación al AI Service y validar el resultado. |
| AI Service | Interactuar con Ollama para generar recomendaciones y descripciones profesionales. |
| Export Service | Generar archivos con los resultados procesados. |
| Frontend | Permitir la interacción del usuario y visualizar los resultados. |

La integración con COMProject se considera una capacidad futura.

---

# 14. Catálogos del Sistema

Los catálogos constituyen información controlada por el negocio y deberán mantenerse centralizados.

En V1 se contemplan:

```
Catalog Service
     │
     ├── State Catalog
     │
     ├── Time Catalog
     │
     └── Responsible Catalog
```

### State Catalog

Define qué estados de los casos son procesables.

Actualmente:

```
Solucionado → Procesable
Cerrado     → Procesable
```

### Time Catalog

Define el rango mínimo y máximo permitido para cada categoría final.

### Responsible Catalog

Contiene los responsables de los grupos de trabajo que pueden ser seleccionados para una ejecución.

Ningún módulo deberá consultar directamente estos catálogos fuera del `Catalog Service`.

---

# 15. Modelo de Datos Conceptual

Las principales entidades de V1 serán:

```
Upload
Case
Estimation
AI Result
Responsible Catalog
State Catalog
Time Catalog
```

No existirán las entidades:

```
User
Session
Role
Permission
```

en la primera versión.

---

# 16. Organización del Equipo

| Rol | Responsabilidades |
| --- | --- |
| **Arquitecto de Software** | Arquitectura, documentación, modelo de datos, contratos, estándares, reglas de arquitectura, revisión técnica y coordinación técnica. |
| **Backend Developer & IA** | Backend, servicios de aplicación, repositories, procesamiento Excel, reglas de negocio, Estimation Engine e integración con Ollama. |
| **Frontend Developer** | Interfaz, selección de responsable, carga de Excel, visualización de casos, resultados, consumo de API y experiencia de usuario. |

Todos los integrantes deberán respetar los documentos y reglas definidos para el proyecto.

Los documentos deberán considerarse de manera conjunta y mantenerse consistentes entre sí. Ningún documento técnico deberá contradecir una regla definida como oficial en el proyecto.

---

# 17. Tecnologías

| Capa | Tecnología |
| --- | --- |
| Backend | FastAPI |
| Frontend | React |
| Base de Datos | PostgreSQL |
| IA Local | Ollama |
| Procesamiento Excel | Pandas |
| ORM | SQLAlchemy |
| Validación | Pydantic |

### Autenticación

**No aplica para V1.**

JWT queda fuera del alcance de la primera versión.

---

# 18. Metodología de Desarrollo

El proyecto se desarrollará bajo un enfoque iterativo e incremental.

Cada módulo deberá desarrollarse respetando:

- Clean Architecture.
- Principio de responsabilidad única.
- Separación de responsabilidades.
- Pruebas unitarias.
- Pruebas de integración cuando corresponda.
- Code Review.
- Convenciones de código.
- Control de versiones.
- Documentación técnica.

La documentación será considerada fuente de verdad para la implementación.

Los documentos del proyecto deberán mantenerse **consistentes entre sí**. Una modificación de una regla oficial deberá evaluarse sobre todos los documentos afectados antes de considerarse definitiva.

---

# 19. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Cambios en estructura del Excel | Validación de estructura y parser desacoplado. |
| Categorías sin configuración | Validación mediante Catalog Service. |
| Estados desconocidos | Catálogo centralizado. |
| Nombres inconsistentes en Responsible Name | Normalización definida como regla. |
| Respuestas inconsistentes de IA | Validación mediante Estimation Engine y AI Service. |
| Información incompleta | Validaciones antes del procesamiento. |
| Cambios futuros en COMProject | Integración desacoplada. |
| Crecimiento de reglas | Catálogos centralizados. |
| Dependencia del modelo local | Contrato de IA y validaciones. |

---

# 20. Criterios de Éxito de V1

La primera versión será considerada exitosa cuando:

- El sistema pueda cargar correctamente el maestro de casos.
- El sistema valide la estructura del Excel.
- Se puedan seleccionar los responsables de los grupos de trabajo configurados.
- El sistema filtre correctamente los casos del responsable seleccionado.
- `Solucionado` y `Cerrado` sean procesados correctamente.
- Los demás estados sean excluidos.
- Se utilice únicamente la categoría final.
- Las categorías consulten correctamente su rango de tiempo.
- Las estimaciones permanezcan dentro de los rangos autorizados.
- La IA genere descripciones profesionales.
- La información original del caso permanezca intacta.
- Los resultados puedan visualizarse en la interfaz.
- Los resultados puedan exportarse.
- El proceso completo pueda ejecutarse mediante una única operación de procesamiento.
- La arquitectura mantenga separación clara entre módulos.
- Los catálogos sean consultados exclusivamente mediante `Catalog Service`.
- No sea necesario modificar manualmente el código para cambiar un rango de tiempo del catálogo.

---

# 21. Criterios de No Éxito

El sistema no deberá considerarse correctamente implementado si:

- Procesa casos en estados no permitidos.
- Permite tiempos fuera del rango configurado.
- Permite procesar casos de un responsable diferente al seleccionado.
- Utiliza subcategorías para determinar tiempos.
- Permite que la IA modifique las reglas del catálogo.
- Los módulos acceden directamente a catálogos sin utilizar `Catalog Service`.
- La lógica de negocio está implementada directamente dentro de los endpoints.
- La IA se expone directamente al frontend.
- Se requiere modificar código para cambiar una regla de catálogo.
- La información original del Excel es reemplazada por información generada por IA.
- Un módulo asume responsabilidades pertenecientes a otro módulo.

---

# 22. Evolución Futura

Una vez finalizada V1, podrán evaluarse:

```
V2
 │
 ├── Integración automática con COMProject
 ├── Autenticación
 ├── Usuarios
 ├── Roles y permisos
 ├── Automatización completa
 └── Nuevas fuentes de información
```

Estas funcionalidades no deberán introducirse en V1 sin una modificación formal del alcance.

---

# 23. Definición Oficial de V1

> **BOT-COMProject V1 será un sistema que recibe un maestro de casos de Aranda, permite seleccionar uno de los responsables de los grupos de trabajo configurados, identifica sus casos procesables según el Catálogo de Estados, utiliza únicamente la categoría final de cada caso para consultar mediante el Catalog Service el rango de tiempo autorizado, utiliza el Estimation Engine para solicitar y validar una recomendación de tiempo mediante el AI Service y genera una descripción profesional. Finalmente presenta y permite exportar los resultados, sin realizar todavía el registro automático en COMProject.**
>