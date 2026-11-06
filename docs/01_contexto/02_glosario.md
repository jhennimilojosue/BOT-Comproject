**Versión:** 1.1

**Estado:** Definido

---

# 1. Términos del Negocio

## Aranda

Plataforma de gestión de servicios (ITSM) utilizada para registrar, gestionar y realizar seguimiento a los casos atendidos por los analistas.

BOT-COMProject utilizará el maestro de casos exportado desde Aranda como fuente de información para el procesamiento.

---

## COMProject

Plataforma utilizada por la organización para registrar las horas de trabajo dedicadas a los diferentes proyectos.

En BOT-COMProject representa el **sistema destino de una futura integración**.

> En V1 el sistema no realizará el registro automático directamente en COMProject.
> 

---

## Caso

Registro individual proveniente de Aranda que representa una solicitud, incidente, requerimiento o actividad atendida.

Un caso puede contener información como:

- Código del caso.
- Responsable.
- Proyecto.
- Categoría.
- Estado.
- Descripción.
- Solución.
- Fecha de registro.
- Información relacionada con SLA.

---

## Responsable

Persona seleccionada por el usuario para realizar el procesamiento de un conjunto de casos.

Los responsables disponibles para V1 corresponden a los cuatro grupos de trabajo configurados en el sistema.

La selección del responsable se realiza antes de iniciar el procesamiento.

---

## Responsible Name

Campo del maestro de casos de Aranda que contiene el nombre de la persona asociada al caso.

El sistema utilizará este campo para determinar si un caso pertenece al responsable seleccionado.

Ejemplo:

```
Responsible Name = Juan Pérez
```

---

## Caso Procesable

Caso que cumple las condiciones necesarias para continuar con el flujo de procesamiento.

En V1, un caso será procesable cuando:

1. Pertenezca al responsable seleccionado.
2. Su estado esté definido como procesable.
3. Contenga una categoría válida.
4. La categoría tenga una configuración de tiempo en el catálogo correspondiente.

---

## Caso Solucionado

Caso cuyo estado en Aranda corresponde a:

```
Solucionado
```

Este estado está definido como procesable en V1.

---

## Caso Cerrado

Caso cuyo estado en Aranda corresponde a:

```
Cerrado
```

Para BOT-COMProject V1, este estado tiene la misma consideración funcional que `Solucionado` y también es procesable.

---

## Estado

Situación actual de un caso registrada en Aranda.

Los estados son administrados mediante el **Catálogo de Estados**.

En V1:

```
Solucionado → Procesable
Cerrado     → Procesable
```

Los demás estados no son procesables salvo que sean configurados posteriormente como tales.

---

## Proyecto

Área, cliente o proyecto al cual pertenece un caso registrado en Aranda.

Ejemplos:

- Proyecto Hospital Militar.
- Proyecto La Previsora.
- ICETEX.
- Service Desk.

---

## Categoría

Clasificación final asignada a un caso en Aranda.

La categoría constituye el criterio principal utilizado para consultar el rango de tiempo aplicable al caso.

---

## Categoría Final

Categoría que aparece como resultado final de la clasificación del caso en el maestro de Aranda.

BOT-COMProject V1 utilizará **únicamente la categoría final** para determinar el rango de tiempo.

Las categorías o subcategorías anteriores no serán utilizadas para la estimación.

---

## Actividad

Trabajo realizado por un responsable durante la atención de un caso.

Puede incluir actividades como:

- Configuración.
- Instalación.
- Soporte.
- Mantenimiento.
- Creación o modificación de configuraciones.
- Atención de incidentes.

---

## Registro de Horas

Proceso mediante el cual se reporta el tiempo dedicado a las actividades realizadas para un proyecto.

En BOT-COMProject V1, el sistema **prepara la información necesaria para este registro**, pero no realiza todavía el registro automático en COMProject.

---

# 2. Términos del Sistema

## BOT-COMProject

Sistema de automatización encargado de procesar información proveniente del maestro de casos de Aranda y generar una propuesta de tiempo y descripción profesional para cada caso procesable.

---

## Maestro de Casos

Archivo Excel exportado desde Aranda que contiene la información de los casos registrados durante un período determinado.

Para V1, el archivo de referencia es:

```
ASDK_Full_Caso.xlsx
```

---

## Upload

Registro correspondiente a un archivo maestro cargado al sistema.

Permite identificar y controlar el archivo utilizado durante un proceso de procesamiento.

---

## Catálogo

Conjunto centralizado de información y reglas configurables utilizadas por el sistema para tomar decisiones de negocio.

Los catálogos son consultados exclusivamente mediante el `Catalog Service`.

---

## Catálogo de Estados

Catálogo que define los estados de los casos y determina cuáles pueden ser procesados por BOT-COMProject.

---

## Catálogo de Tiempos

Catálogo que contiene el rango de tiempo autorizado para cada categoría final.

Como mínimo, cada configuración contiene:

- Categoría.
- Tiempo mínimo.
- Tiempo máximo.
- Estado activo/inactivo.

Ejemplo:

```
Categoría:
Ingreso de Huella

Tiempo mínimo:
30 minutos

Tiempo máximo:
60 minutos
```

El Catálogo de Tiempos constituye la **fuente oficial de los rangos permitidos**.

---

## Catálogo de Responsables

Catálogo que contiene las personas disponibles para ser seleccionadas como responsables del procesamiento.

En V1 contiene cuatro grupos de trabajo con sus respectivos responsables.

---

## Catalog Service

Servicio interno responsable de proporcionar acceso centralizado a los catálogos del sistema.

Es el **único servicio autorizado para consultar los catálogos de negocio**.

Los demás componentes no deberán acceder directamente a las estructuras de persistencia de los catálogos.

---

## Excel Service

Servicio encargado de procesar el maestro de casos.

Sus responsabilidades principales incluyen:

- Leer el archivo.
- Identificar la estructura.
- Validar columnas requeridas.
- Extraer la información necesaria.
- Normalizar los datos cuando corresponda.
- Entregar los casos al flujo de procesamiento.

---

## Parser de Excel

Componente interno encargado de interpretar técnicamente el archivo Excel y convertir sus datos en estructuras utilizables por el sistema.

El Parser forma parte del procesamiento realizado por el `Excel Service`.

---

## Case Service

Servicio responsable de gestionar y orquestar el procesamiento de los casos.

Coordina componentes como:

```
Case Repository
Catalog Service
Estimation Engine
AI Service
```

El `Case Service` no debe contener directamente toda la lógica especializada de cada componente.

---

## Case Repository

Componente responsable de almacenar y consultar la información de los casos en la base de datos.

---

## Estimation Engine

Componente encargado de determinar el tiempo estimado para un caso respetando el rango definido por el Catálogo de Tiempos.

Su flujo conceptual es:

```
Categoría Final
       ↓
Catalog Service
       ↓
Rango permitido
       ↓
Estimation Engine
       ↓
IA / lógica de estimación
       ↓
Tiempo estimado
       ↓
Validación del rango
```

El `Estimation Engine` **no puede generar ni aceptar un tiempo fuera del rango autorizado**.

---

## AI Service

Servicio interno responsable de interactuar con el modelo de Inteligencia Artificial local.

Sus principales responsabilidades son:

- Preparar la información necesaria para la IA.
- Solicitar la generación de contenido.
- Procesar la respuesta.
- Validar la estructura de la respuesta.
- Entregar el resultado al flujo de aplicación.

El `AI Service` no define las reglas de negocio.

---

## Vista Previa

Pantalla en la que el usuario puede revisar los resultados generados por el sistema antes de utilizarlos para el reporte de horas.

Puede mostrar información como:

- Caso.
- Responsable.
- Proyecto.
- Categoría.
- Estado.
- Tiempo estimado.
- Descripción generada.

---

## Exportación

Proceso mediante el cual BOT-COMProject genera un archivo con los resultados procesados.

La exportación permite utilizar la información posteriormente para el registro de horas.

---

# 3. Términos de Inteligencia Artificial

## Inteligencia Artificial (IA)

Modelo de lenguaje utilizado por BOT-COMProject para generar una recomendación de tiempo y una descripción profesional del caso.

En V1 se ejecutará localmente mediante Ollama.

La IA **no define ni modifica las reglas de negocio**.

---

## Ollama

Plataforma utilizada para ejecutar localmente el modelo de Inteligencia Artificial utilizado por BOT-COMProject.

---

## Modelo de IA

Modelo de lenguaje ejecutado mediante Ollama que recibe información contextual del caso y genera los resultados solicitados por el sistema.

---

## Tiempo Estimado

Tiempo finalmente determinado por el sistema para un caso.

Debe cumplir obligatoriamente:

```
Tiempo mínimo ≤ Tiempo estimado ≤ Tiempo máximo
```

El tiempo estimado debe corresponder al rango definido para la categoría del caso.

---

## Tiempo Recomendado

Valor de tiempo propuesto por la IA durante el proceso de estimación.

El valor recomendado deberá ser validado por el `Estimation Engine` antes de convertirse en el tiempo estimado definitivo.

---

## Descripción Profesional

Texto generado por la IA que resume de manera clara, coherente y profesional la actividad realizada durante la atención de un caso.

La descripción debe basarse únicamente en la información disponible del caso y su contexto autorizado.

---

## Contexto

Conjunto de información que se proporciona a la IA para generar un resultado.

Puede incluir:

- Categoría final.
- Descripción del caso.
- Solución.
- Proyecto.
- Estado.
- Rango de tiempo permitido.

---

# 4. Términos de Arquitectura

## Regla de Negocio

Condición o restricción definida por la organización que determina cómo debe comportarse el sistema.

Ejemplo:

> Los casos en estado `Solucionado` o `Cerrado` pueden ser procesados.
> 

---

## Módulo

Unidad funcional del sistema que agrupa componentes relacionados con una responsabilidad determinada.

Un módulo no deberá crearse únicamente por anticipación.

> **Un módulo se crea cuando existe una necesidad real de incorporar archivos, componentes o responsabilidades relacionadas con esa funcionalidad.**
> 

---

## Servicio

Componente encargado de ejecutar una responsabilidad específica dentro del sistema.

Un servicio puede utilizar otros componentes mediante contratos definidos, evitando acoplamiento innecesario.

---

## Servicio Interno

Servicio que forma parte de la lógica interna de la aplicación y que no es expuesto directamente mediante un endpoint HTTP para el frontend.

Ejemplos:

```
Catalog Service
AI Service
Estimation Engine
Excel Service
```

---

## Endpoint

Punto de entrada HTTP mediante el cual el frontend puede solicitar una operación al backend.

En V1, los endpoints públicos corresponden principalmente a operaciones como:

- Cargar archivo.
- Consultar casos.
- Procesar casos.
- Consultar resultados.
- Exportar información.

Los servicios internos no tendrán endpoints propios para ser consumidos directamente por el frontend.

---

## Orquestación

Proceso mediante el cual un servicio coordina diferentes componentes para ejecutar una operación completa de negocio.

En BOT-COMProject, el `Case Service` será responsable de orquestar el procesamiento de casos.

---

## Flujo de Procesamiento

Secuencia de pasos que sigue la información desde la carga del maestro de casos hasta la generación del tiempo y descripción.

```
Excel
 ↓
Validación
 ↓
Selección de responsable
 ↓
Filtrado de casos
 ↓
Validación de estado
 ↓
Categoría final
 ↓
Catálogo de Tiempos
 ↓
Estimation Engine
 ↓
AI Service
 ↓
Resultado
```

---

## Clean Architecture

Modelo de arquitectura de software basado en la separación de responsabilidades y el desacoplamiento entre componentes.

Su objetivo es facilitar:

- Mantenimiento.
- Pruebas.
- Evolución.
- Reutilización.
- Independencia entre lógica de negocio e infraestructura.

---

## MVP / V1

Primera versión funcional del sistema que contiene las funcionalidades esenciales para validar la solución.

En BOT-COMProject V1, el proceso termina cuando se han generado y almacenado:

```
Caso
+
Tiempo estimado
+
Descripción profesional
```

La integración automática con COMProject queda fuera de V1.

---

## Fuente de Verdad

Documento, catálogo o componente autorizado que contiene la definición oficial de una determinada información o regla.

Ejemplos:

| Información | Fuente de verdad |
| --- | --- |
| Estados procesables | Catálogo de Estados |
| Rangos de tiempo | Catálogo de Tiempos |
| Categoría del caso | Maestro de Aranda |
| Responsable del caso | `Responsible Name` |
| Arquitectura | Documentación arquitectónica |
| Reglas de negocio | Documento de Reglas de Negocio |

---

# 5. Componentes Internos de Procesamiento

Estos términos representan responsabilidades internas del procesamiento. **No implican necesariamente que cada uno deba convertirse en un módulo independiente.**

---

## Case Validator

Componente encargado de verificar que un caso contenga la información mínima necesaria para continuar con el procesamiento.

---

## Case Filter

Componente encargado de aplicar los criterios de filtrado establecidos por las reglas de negocio.

Puede validar, entre otros:

- Responsable seleccionado.
- Estado procesable.
- Información requerida.

---

## Case Normalizer

Componente encargado de estandarizar información de los casos cuando sea necesario para garantizar consistencia durante el procesamiento.

---

## Case Context Builder

Componente encargado de construir el contexto que será utilizado por el `Estimation Engine` y el `AI Service`.

Debe incluir únicamente la información necesaria para generar el resultado.

---

# 6. Convenciones del Proyecto

Todos los integrantes deberán utilizar los términos de este glosario de manera consistente.

| Término | Convención |
| --- | --- |
| **Caso** | Registro proveniente del maestro de Aranda. |
| **Responsable** | Persona seleccionada para procesar sus casos. |
| **Responsible Name** | Campo del Excel que identifica al responsable asociado al caso. |
| **Categoría** | Categoría final utilizada para determinar el rango de tiempo. |
| **Caso Procesable** | Caso que cumple todas las condiciones necesarias para continuar. |
| **Solucionado** | Estado procesable. |
| **Cerrado** | Estado procesable en V1. |
| **Catálogo de Tiempos** | Fuente oficial de rangos de tiempo. |
| **Catalog Service** | Único servicio autorizado para consultar catálogos. |
| **Tiempo Recomendado** | Valor propuesto por la IA. |
| **Tiempo Estimado** | Resultado final validado por el sistema. |
| **IA** | Componente utilizado para generación y recomendación, siempre sujeto a las reglas del sistema. |
| **AI Service** | Servicio interno que interactúa con el modelo de IA. |
| **Estimation Engine** | Componente que controla la estimación dentro del rango permitido. |
| **COMProject** | Sistema destino de una futura integración. |
| **V1** | Versión que genera tiempo y descripción, sin registro automático en COMProject. |

---

# 7. Reglas de uso del Glosario

### Regla GLO-001

Todos los documentos técnicos deberán utilizar los términos definidos en este glosario.

### Regla GLO-002

No se deberán crear sinónimos diferentes para conceptos que ya tengan un término oficial.

### Regla GLO-003

Si durante el desarrollo aparece un concepto nuevo que tenga relevancia arquitectónica, funcional o de negocio, deberá incorporarse al glosario.

### Regla GLO-004

Si un término cambia de significado como consecuencia de una decisión del proyecto, deberá actualizarse primero el glosario y posteriormente los documentos afectados.