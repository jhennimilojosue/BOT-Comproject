**Proyecto:** BOT-COMProject

**Versión:** 1.2

**Estado:** Definido

---

# 1. Objetivo

Definir los módulos funcionales que componen BOT-COMProject, estableciendo sus responsabilidades, entradas, salidas, dependencias y relaciones.

La organización de módulos deberá mantener una separación clara de responsabilidades y estar alineada con los principios de **Clean Architecture**.

El mapa de módulos representa la organización lógica del sistema y servirá como referencia para:

- Diseño de arquitectura.
- Diseño de componentes.
- Definición de responsabilidades.
- Definición de dependencias.
- Implementación.
- Pruebas.
- Evolución futura del sistema.

> Un módulo no deberá crearse únicamente por anticipación. Se incorporará cuando exista una necesidad real de agregar archivos, componentes o responsabilidades relacionadas con una funcionalidad.
> 

---

# 2. Alcance de V1

La V1 deberá permitir:

```
Cargar Maestro de Casos
        ↓
Validar archivo
        ↓
Extraer casos
        ↓
Seleccionar responsable
        ↓
Filtrar casos
        ↓
Validar información
        ↓
Consultar catálogos
        ↓
Estimar tiempo
        ↓
Generar descripción profesional
        ↓
Validar resultado
        ↓
Mostrar resultados
        ↓
Exportar información
```

La integración automática con COMProject queda fuera del alcance de V1.

---

# 3. Vista General

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
                         Excel Service
                               │
                               ▼
                       Gestión de Casos
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        Catalog Service   Case Repository   Resultado
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
     Estados  Tiempos  Responsables
                │
                ▼
          Estimation Engine
                │
                ▼
            AI Service
                │
                ▼
        Resultado procesado
                │
          ┌─────┴─────┐
          ▼           ▼
     Vista Previa  Exportación
```

---

# 4. Gestión de Archivos

## Responsabilidad

Gestionar la recepción y validación inicial del Maestro de Casos proporcionado por el usuario.

Este componente constituye el punto de entrada del archivo al sistema.

## Entradas

```
Archivo Excel (.xlsx)
```

## Salidas

```
Archivo validado
Errores de carga
Errores de estructura
```

## Funciones

- Recibir el archivo.
- Validar extensión.
- Validar que el archivo pueda ser leído.
- Validar estructura inicial.
- Entregar el archivo validado al `Excel Service`.

## No es responsable de

- Interpretar reglas de negocio.
- Filtrar casos.
- Estimar tiempos.
- Generar descripciones.
- Consultar la IA.

---

# 5. Excel Service

## Responsabilidad

Procesar el Maestro de Casos y transformar la información proveniente de Aranda en casos normalizados que puedan ser utilizados por el sistema.

## Entradas

```
Archivo Excel validado
```

## Salidas

```
Colección de casos normalizados
Errores de procesamiento
```

## Funciones

- Leer el archivo.
- Identificar la estructura requerida.
- Identificar encabezados.
- Extraer las columnas necesarias.
- Mapear información al `Case Contract`.
- Normalizar datos estructurales.
- Extraer `Responsible Name`.
- Extraer categoría final.
- Extraer estado.
- Extraer proyecto.
- Extraer descripción.
- Extraer solución.
- Entregar los casos normalizados a Gestión de Casos.

## Restricción

`Excel Service` no deberá implementar reglas de negocio relacionadas con:

- Estados procesables.
- Rangos de tiempo.
- Responsables habilitados.
- Estimación.
- IA.

Su responsabilidad es **extraer y transformar la información del archivo**.

---

# 6. Gestión de Casos

## Responsabilidad

Administrar y preparar los casos provenientes del `Excel Service` para que puedan continuar hacia el proceso de estimación.

Sus responsabilidades principales son:

- Normalizar.
- Validar.
- Filtrar.
- Preparar.

## Entradas

```
Casos normalizados
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
- Validar responsable seleccionado.
- Filtrar por responsable.
- Validar estados procesables.
- Validar categoría final.
- Consultar configuraciones mediante `Catalog Service`.
- Detectar duplicados dentro de la ejecución.
- Preparar los casos para `Estimation Engine`.

## No es responsable de

- Calcular tiempos.
- Generar descripciones.
- Ejecutar IA.
- Registrar horas en COMProject.

---

# 7. Componentes internos de Gestión de Casos

Los siguientes componentes forman parte del procesamiento interno de Gestión de Casos.

## 7.1 Case Normalizer

Estandariza la información proveniente del Excel.

Puede realizar:

- Eliminación de espacios innecesarios.
- Normalización de texto.
- Normalización de fechas.
- Estandarización de valores vacíos.
- Normalización de nombres.

No modifica reglas de negocio.

---

## 7.2 Case Validator

Verifica que el caso contenga la información mínima necesaria.

Puede validar:

- Código.
- Responsable.
- Proyecto.
- Fecha.
- Estado.
- Categoría final.
- Información necesaria para continuar.

---

## 7.3 Case Filter

Determina si un caso puede continuar.

El flujo principal es:

```
Responsable seleccionado
        ↓
Estado procesable
        ↓
Información requerida
        ↓
Categoría configurada
        ↓
Caso procesable
```

El `Case Filter` deberá utilizar `Catalog Service` cuando necesite información proveniente de catálogos.

---

# 8. Catalog Service

## Responsabilidad

Proporcionar acceso centralizado a los catálogos de negocio utilizados por BOT-COMProject.

Es el **único componente autorizado para consultar directamente la fuente de los catálogos**.

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
- Determinar si un estado es procesable.
- Consultar categorías configuradas.
- Obtener rangos de tiempo.
- Consultar responsables disponibles.
- Validar configuraciones activas.

## Regla principal

Los módulos consumidores no deberán acceder directamente a los archivos o persistencia de los catálogos.

```
Módulo
   ↓
Catalog Service
   ↓
Catálogo
```

Nunca:

```
Módulo
   ↓
Archivo/Base de datos
```

---

# 9. Case Repository

## Responsabilidad

Gestionar la persistencia de la información relacionada con los casos y sus resultados de procesamiento.

## Funciones

- Persistir información cuando el flujo lo requiera.
- Consultar información de casos.
- Consultar resultados de procesamiento.
- Apoyar la identificación de duplicados.
- Recuperar información para etapas posteriores.

El repositorio no deberá contener reglas de negocio.

## Restricción

Los módulos de negocio no deberán acceder directamente a la base de datos.

```
Módulo
   ↓
Repository
   ↓
Base de datos
```

---

# 10. Estimation Engine

## Responsabilidad

Determinar el tiempo estimado de un caso utilizando:

- Información del caso.
- Categoría final.
- Rango autorizado.
- Contexto requerido para la estimación.

## Entradas

```
Caso procesable
Categoría final
Rango mínimo
Rango máximo
Contexto del caso
```

## Salidas

```
Tiempo recomendado
Tiempo validado
Resultado de estimación
```

## Flujo

```
Caso procesable
       ↓
Categoría final
       ↓
Catalog Service
       ↓
Rango autorizado
       ↓
Case Context Builder
       ↓
AI Service
       ↓
Tiempo recomendado
       ↓
Validación
       ↓
Tiempo estimado
```

## Restricción principal

El tiempo final deberá cumplir:

```
Tiempo mínimo
      ≤
Tiempo estimado
      ≤
Tiempo máximo
```

El `Estimation Engine` es responsable de garantizar esta restricción.

---

# 11. Case Context Builder

## Responsabilidad

Construir el contexto que será enviado al `AI Service`.

Puede incluir:

```
Código
Descripción
Solución
Proyecto
Categoría final
Estado
Rango permitido
```

El contexto deberá contener únicamente información necesaria y autorizada.

## Restricción

El `Case Context Builder` no determina el tiempo.

Su responsabilidad es preparar el contexto para la IA.

---

# 12. AI Service

## Responsabilidad

Gestionar la interacción con el modelo de IA local utilizado por BOT-COMProject.

La V1 utilizará **Ollama** como mecanismo de inferencia local.

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
- Ejecutar inferencia.
- Procesar la respuesta.
- Validar la estructura de salida.
- Entregar la recomendación al `Estimation Engine`.

## Restricciones

La IA no podrá:

- Crear nuevas reglas.
- Modificar catálogos.
- Modificar rangos.
- Recomendar tiempos fuera del rango autorizado.
- Inventar información no presente en el contexto autorizado.

---

# 13. Resultado de Procesamiento

El resultado principal generado para cada caso procesado será:

```
Caso
 │
 ├── Tiempo estimado
 │
 └── Descripción profesional
```

El resultado deberá mantener la relación con el caso original para permitir su revisión y posterior utilización.

---

# 14. Validación del Resultado

Antes de presentar el resultado como válido, el sistema deberá verificar:

## Tiempo

```
mínimo ≤ tiempo estimado ≤ máximo
```

## Descripción

La descripción deberá:

- Tener contenido.
- Ser coherente con el contexto.
- Representar la actividad realizada.
- No inventar información.
- Cumplir el formato establecido.

Un resultado inválido no deberá presentarse como resultado final válido.

---

# 15. Vista Previa

## Responsabilidad

Presentar al usuario los resultados generados para su revisión.

Podrá mostrar:

| Campo | Información |
| --- | --- |
| Código | Código del caso |
| Responsable | Responsable seleccionado |
| Proyecto | Proyecto |
| Categoría | Categoría final |
| Estado | Estado del caso |
| Tiempo | Tiempo estimado |
| Descripción | Descripción generada |
| Resultado | Estado de procesamiento |

La Vista Previa no deberá modificar las reglas de negocio ni realizar estimaciones.

---

# 16. Exportación

## Responsabilidad

Generar una salida estructurada con los resultados procesados.

## Salidas

```
Archivo Excel
Reporte de procesamiento
```

La exportación permitirá utilizar posteriormente la información generada para el proceso de registro de horas.

## Fuera de alcance

La exportación no registra directamente información en COMProject.

---

# 17. Integración con COMProject

## Estado

**Fuera del alcance de V1.**

## Responsabilidad futura

Permitir el registro automático de la información aprobada en COMProject.

La arquitectura deberá permitir incorporar esta funcionalidad posteriormente sin modificar significativamente los módulos existentes.

---

# 18. Dependencias

| Componente | Dependencias |
| --- | --- |
| Gestión de Archivos | Ninguna |
| Excel Service | Gestión de Archivos |
| Gestión de Casos | Excel Service, Catalog Service, Case Repository |
| Case Normalizer | Gestión de Casos |
| Case Validator | Gestión de Casos |
| Case Filter | Gestión de Casos, Catalog Service |
| Catalog Service | Persistencia de catálogos |
| Case Repository | Base de datos |
| Estimation Engine | Catalog Service, AI Service |
| Case Context Builder | Estimation Engine |
| AI Service | Ollama |
| Vista Previa | Resultado de procesamiento |
| Exportación | Resultado de procesamiento |
| Integración COMProject | V2 o posterior |

---

# 19. Flujo de Comunicación

```
Usuario
   │
   ▼
Gestión de Archivos
   │
   ▼
Excel Service
   │
   ▼
Gestión de Casos
   │
   ├──────────────► Catalog Service
   │                     │
   │                     ├── Estados
   │                     └── Responsables
   │
   ├──────────────► Case Repository
   │
   ▼
Casos procesables
   │
   ▼
Estimation Engine
   │
   ├──────────────► Catalog Service
   │                     │
   │                     └── Tiempos
   │
   ▼
Case Context Builder
   │
   ▼
AI Service
   │
   ▼
Validación
   │
   ▼
Resultado
   │
   ├──────────────► Vista Previa
   │
   └──────────────► Exportación
```

---

# 20. Contratos entre Módulos

La comunicación entre módulos deberá realizarse mediante contratos definidos.

Principales contratos:

```
Excel Service
      ↓
Case Contract
      ↓
Gestión de Casos
```

```
Gestión de Casos
      ↓
Caso procesable
      ↓
Estimation Engine
```

```
Estimation Engine
      ↓
AI Service Contract
      ↓
AI Service
```

```
Resultado
      ↓
Vista Previa / Exportación
```

Los contratos deberán mantenerse independientes de las implementaciones concretas.

---

# 21. Principios de Diseño

Todos los componentes deberán cumplir:

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Comunicación mediante contratos.
- Separación entre dominio e infraestructura.
- Inversión de dependencias.
- Testabilidad.
- Reutilización cuando exista una necesidad real.
- Independencia de implementaciones concretas.
- Validaciones deterministas.
- Centralización de reglas de negocio.

---

# 22. Centralización de Catálogos

Los catálogos deberán mantenerse centralizados.

Ningún componente consumidor podrá acceder directamente a:

- Archivos Excel de catálogos.
- Tablas de catálogos.
- Estructuras de persistencia de catálogos.

El acceso será:

```
Componente
     ↓
Catalog Service
     ↓
Catálogo
```

Esto garantiza que las reglas de acceso y consulta estén centralizadas.

---

# 23. Módulos Fuera de V1

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

# 24. Regla de Creación de Módulos

> **No se deberá crear un módulo únicamente porque esté contemplado como una posible funcionalidad futura.**
> 

Un módulo será creado cuando exista una necesidad real de incorporar:

- Archivos.
- Componentes.
- Servicios.
- Modelos.
- Reglas.
- Responsabilidades relacionadas con una funcionalidad.

Esto evita una arquitectura sobredimensionada y mantiene el proyecto alineado con las necesidades reales de V1.

---

# 25. Regla de Consistencia

Este documento deberá mantenerse alineado con:

- Arquitectura del Sistema.
- Estructura y Convenciones del Proyecto.
- Modelo de Datos.
- Contrato de API.
- Case Contract.
- Diseño de Gestión de Casos.
- Diseño de Excel Service.
- Estimation Engine.
- AI Service.
- Catálogo de Estados.
- Catálogo de Responsables.
- Catálogo de Tiempos.

Cuando una nueva decisión modifique la responsabilidad o relación de un módulo:

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