**Proyecto:** BOT-COMProject

**Versión:** 1.1

**Estado:** Definido

**Tipo:** Documento de arquitectura

---

# 1. Objetivo

Este documento define la arquitectura técnica y conceptual de **BOT-COMProject**, estableciendo la organización de sus componentes, responsabilidades, dependencias, comunicación y principios de diseño.

Su objetivo es proporcionar una estructura que permita desarrollar el sistema de forma:

- Modular.
- Escalable.
- Testable.
- Mantenible.
- Desacoplada.
- Alineada con Clean Architecture.

Este documento servirá como referencia para la implementación del backend, frontend, persistencia, servicios internos y comunicación con la IA local.

> Este documento define la arquitectura del sistema, no las reglas específicas de negocio ni la implementación detallada de cada módulo.
> 

---

# 2. Alcance Arquitectónico

La arquitectura definida corresponde a la **V1 de BOT-COMProject**.

La V1 comprende:

```
Carga del Maestro de Casos
        ↓
Validación inicial del archivo
        ↓
Procesamiento del Excel
        ↓
Selección del responsable
        ↓
Gestión y filtrado de casos
        ↓
Consulta de catálogos
        ↓
Preparación del contexto
        ↓
Estimación de tiempo
        ↓
Generación de descripción
        ↓
Validación del resultado
        ↓
Presentación de resultados
        ↓
Exportación
```

La integración automática con COMProject queda fuera de la V1.

---

# 3. Principios Arquitectónicos

BOT-COMProject seguirá los siguientes principios:

### PA-01 — Separación de responsabilidades

Cada componente deberá tener una responsabilidad claramente definida.

### PA-02 — Bajo acoplamiento

Los módulos no deberán depender directamente de implementaciones concretas de otros módulos.

### PA-03 — Alta cohesión

Los componentes deberán agrupar responsabilidades relacionadas.

### PA-04 — Inversión de dependencias

La lógica de negocio no deberá depender directamente de infraestructura.

### PA-05 — Testabilidad

Los componentes deberán poder probarse de forma aislada siempre que sea posible.

### PA-06 — Centralización de reglas

Las reglas configurables del negocio deberán mantenerse en los catálogos correspondientes.

### PA-07 — IA desacoplada

La lógica de negocio no deberá depender directamente de Ollama ni de un modelo específico.

### PA-08 — Infraestructura desacoplada

El dominio y los servicios de aplicación no deberán conocer detalles innecesarios de PostgreSQL, Pandas, Ollama o FastAPI.

### PA-09 — Comunicación mediante contratos

Los componentes deberán comunicarse mediante contratos definidos y estructuras conocidas.

### PA-10 — Evolución controlada

No deberán crearse módulos, servicios o componentes únicamente por anticipación de funcionalidades futuras.

---

# 4. Estilo Arquitectónico

BOT-COMProject utilizará una arquitectura basada en:

```
Clean Architecture
+
Arquitectura modular
+
Casos de uso
+
Servicios de aplicación
+
Repositorios
```

Conceptualmente:

```
                 ┌──────────────────────┐
                 │      Frontend        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │         API          │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     Application      │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Cases        Estimation      Catalog
              │           Engine        Service
              │             │             │
              ▼             ▼             ▼
        Repository       AI Service    Catalogs
              │             │
              │             ▼
              │          Ollama
              │
              └───────────┬──────────────┘
                          ▼
                     PostgreSQL
```

---

# 5. Capas del Sistema

## 5.1 Presentation

Responsable de la interacción con el usuario.

Incluye:

- Frontend.
- API.
- Endpoints HTTP.
- Validación de solicitudes externas.
- Transformación de respuestas.

La capa de presentación:

- No deberá implementar reglas de negocio.
- No deberá consultar directamente la base de datos.
- No deberá consultar directamente Ollama.
- No deberá leer directamente los catálogos.

---

# 5.2 Application

Contiene los **casos de uso y la orquestación del proceso**.

Responsabilidades:

- Coordinar servicios.
- Ejecutar casos de uso.
- Coordinar repositorios mediante contratos.
- Coordinar servicios especializados.
- Controlar el flujo de procesamiento.
- Transformar los resultados entre las diferentes etapas.

El principal caso de uso de V1 será:

```
Process Cases
```

La API deberá iniciar este caso de uso sin implementar dentro del endpoint la lógica completa del proceso.

---

# 5.3 Domain

Contiene los conceptos y reglas propias del negocio.

Puede incluir:

- Entidades.
- Value Objects.
- Contratos.
- Reglas de dominio.
- Excepciones de negocio.
- Interfaces de repositorios.
- Contratos de servicios.

Esta capa no deberá depender de:

```
FastAPI
PostgreSQL
SQLAlchemy
Pandas
Ollama
React
```

---

# 5.4 Infrastructure

Contiene las implementaciones concretas necesarias para interactuar con tecnologías y sistemas externos.

Incluye:

- PostgreSQL.
- SQLAlchemy.
- Pandas.
- Ollama.
- Lectura de archivos.
- Implementaciones de repositorios.
- Implementaciones de proveedores de IA.
- Implementaciones de acceso a catálogos.

La infraestructura implementará los contratos definidos por las capas internas.

---

# 6. Módulos Funcionales V1

La V1 estará compuesta por los siguientes módulos funcionales:

```
Gestión de Archivos
Excel Service
Gestión de Casos
Catalog Service
Case Repository
Estimation Engine
AI Service
Vista Previa
Exportación
```

Los siguientes componentes pertenecen internamente a otros módulos:

```
Gestión de Casos
 ├── Case Normalizer
 ├── Case Validator
 ├── Case Filter
 └── Case Context Builder
```

Estos componentes **no deberán convertirse en módulos independientes** mientras no exista una necesidad real que justifique dicha separación.

---

# 7. Gestión de Archivos

### Responsabilidad

Gestionar la recepción y validación inicial del Maestro de Casos.

### Entrada

```
Archivo .xlsx
```

### Salidas

```
Archivo validado
o
Error de carga/validación
```

### Responsabilidades

- Recibir el archivo.
- Validar extensión.
- Validar condiciones básicas del archivo.
- Validar estructura inicial requerida.
- Entregar el archivo al `Excel Service`.

### Restricción

No deberá interpretar reglas de negocio relacionadas con los casos.

---

# 8. Excel Service

### Responsabilidad

Extraer y transformar la información necesaria del Maestro de Casos.

Responsabilidades:

- Leer el archivo.
- Identificar encabezados.
- Identificar columnas requeridas.
- Extraer información.
- Normalizar valores iniciales.
- Crear casos normalizados.
- Reportar errores de procesamiento.

Información relevante:

```
Código
Responsible Name
Usuario
Proyecto
Fecha
Estado
Categoría final
Descripción
Solución
```

El `Excel Service` no deberá:

- Determinar estados procesables.
- Determinar tiempos.
- Consultar directamente los catálogos de negocio.
- Ejecutar IA.
- Registrar información en COMProject.

---

# 9. Gestión de Casos

### Responsabilidad

Validar, normalizar, filtrar y preparar los casos para las siguientes etapas del procesamiento.

Incluye:

```
Case Normalizer
Case Validator
Case Filter
Case Context Builder
```

Debe:

- Normalizar información.
- Validar datos obligatorios.
- Validar el responsable seleccionado.
- Filtrar casos por responsable.
- Validar estados procesables.
- Validar categoría final.
- Validar configuración de categoría mediante `Catalog Service`.
- Identificar casos no procesables.
- Evitar duplicidades durante una ejecución.
- Preparar los casos para `Estimation Engine`.

No deberá:

- Calcular tiempos.
- Ejecutar IA.
- Comunicarse directamente con Ollama.
- Registrar información en COMProject.
- Modificar catálogos.

---

# 10. Case Context Builder

`Case Context Builder` es un componente interno de Gestión de Casos.

### Responsabilidad

Construir el contexto autorizado que será utilizado posteriormente por `AI Service`.

Puede contener:

```
Código
Responsable
Proyecto
Categoría final
Descripción
Solución
Estado
Rango autorizado
```

El contexto deberá contener únicamente la información necesaria para la operación de IA.

### Restricción

El `Case Context Builder`:

- No calcula tiempos.
- No genera recomendaciones.
- No ejecuta el modelo.
- No modifica información original del caso.

---

# 11. Catalog Service

El sistema tendrá un servicio centralizado denominado:

```
Catalog Service
```

Será el único componente autorizado para acceder a los catálogos de negocio.

Conceptualmente:

```
                 Catalog Service
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Estados        Tiempos      Responsables
```

Responsabilidades:

- Consultar catálogos.
- Validar configuraciones.
- Determinar estados procesables.
- Consultar rangos de tiempo.
- Consultar responsables disponibles.
- Validar que una configuración esté activa.

Los consumidores no deberán acceder directamente a los archivos ni a la persistencia de los catálogos.

---

# 12. Catálogo de Estados

El `Catalog Service` será responsable de consultar el Catálogo de Estados.

Para V1:

```
Solucionado → Procesable
Cerrado     → Procesable
```

Los demás estados serán considerados no procesables según la configuración vigente del catálogo.

La lógica de qué estados son procesables **no deberá estar escrita directamente en `Case Filter`**.

---

# 13. Catálogo de Responsables

El sistema contará con un catálogo de responsables para V1.

El flujo será:

```
Usuario
   ↓
Selecciona responsable
   ↓
API
   ↓
Application
   ↓
Catalog Service
   ↓
Responsable válido
   ↓
Gestión de Casos
```

El responsable seleccionado deberá validarse antes de procesar los casos.

---

# 14. Catálogo de Tiempos

El Catálogo de Tiempos define los rangos autorizados para cada categoría final.

Flujo:

```
Categoría final
       ↓
Catalog Service
       ↓
Rango mínimo / máximo
       ↓
Estimation Engine
```

El rango autorizado constituye una **restricción de negocio**.

Ningún resultado de estimación podrá encontrarse fuera de dicho rango.

---

# 15. Case Repository

El `Case Repository` abstraerá la persistencia relacionada con los casos y sus resultados de procesamiento.

Conceptualmente:

```
Application / Domain
        ↓
Case Repository Contract
        ↓
Case Repository Implementation
        ↓
SQLAlchemy
        ↓
PostgreSQL
```

Responsabilidades:

- Guardar casos cuando corresponda.
- Consultar casos.
- Consultar resultados de procesamiento.
- Apoyar el control de duplicidades.
- Recuperar información necesaria para etapas posteriores.

El repositorio:

- No deberá contener reglas de negocio.
- No deberá determinar estados procesables.
- No deberá determinar tiempos.
- No deberá ejecutar IA.

---

# 16. Estimation Engine

### Responsabilidad

Determinar el tiempo estimado respetando el rango autorizado por el Catálogo de Tiempos.

Entrada conceptual:

```
Caso
+
Categoría final
+
Rango autorizado
```

Flujo:

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
Validación
   ↓
Tiempo estimado
```

El `Estimation Engine` deberá garantizar que:

```
tiempo_minimo <= tiempo_estimado <= tiempo_maximo
```

Si la recomendación de la IA se encuentra fuera del rango autorizado, el resultado no deberá aceptarse directamente.

---

# 17. AI Service

### Responsabilidad

Gestionar la comunicación con el modelo de IA local.

Tecnología inicial:

```
Ollama
```

Responsabilidades:

- Construir la solicitud al modelo.
- Enviar el contexto.
- Ejecutar inferencia.
- Recibir la respuesta.
- Validar la estructura de respuesta.
- Transformar la respuesta al contrato esperado.

La IA podrá generar:

```
Tiempo recomendado
Descripción profesional
```

La IA no tendrá autoridad para:

- Crear reglas.
- Modificar catálogos.
- Cambiar rangos.
- Procesar estados no permitidos.
- Modificar los datos originales del caso.
- Registrar directamente información en sistemas externos.

---

# 18. Proveedor de IA

La arquitectura deberá permitir cambiar el proveedor o modelo de IA sin modificar la lógica principal.

Conceptualmente:

```
Estimation Engine
       │
       ▼
   AI Service
       │
       ▼
   AI Provider
       │
       ▼
     Ollama
       │
       ▼
Modelo configurado
```

La dependencia con Ollama deberá permanecer encapsulada en infraestructura.

---

# 19. Resultado de Procesamiento

El procesamiento de cada caso podrá producir:

```
Caso
 │
 ├── Tiempo estimado
 │
 └── Descripción profesional
```

El resultado deberá distinguirse conceptualmente de la información original del caso.

```
Datos originales
      +
Procesamiento
      ↓
Resultado
```

Los resultados serán utilizados posteriormente por:

```
Vista Previa
Exportación
```

---

# 20. Vista Previa

### Responsabilidad

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

La Vista Previa no deberá recalcular resultados ni modificar las reglas del proceso.

---

# 21. Exportación

### Responsabilidad

Generar una salida estructurada de los resultados procesados.

Salidas previstas:

```
Archivo Excel
Reporte de procesamiento
```

La exportación utilizará los resultados generados por el flujo de procesamiento.

No deberá:

- Ejecutar IA.
- Calcular tiempos.
- Consultar directamente catálogos.
- Aplicar reglas de negocio nuevas.

---

# 22. Caso de Uso Principal

La operación principal de V1 será:

```
POST /api/v1/cases/process
```

Esta operación representará la entrada al proceso completo.

Conceptualmente:

```
Frontend
   │
   ▼
API
   │
   ▼
Process Cases Use Case
   │
   ├── Gestión de Archivos
   ├── Excel Service
   ├── Catalog Service
   ├── Gestión de Casos
   ├── Case Repository
   ├── Estimation Engine
   └── AI Service
```

El endpoint deberá actuar como adaptador de entrada.

La orquestación deberá pertenecer a la capa `Application`.

---

# 23. Comunicación entre Componentes

La comunicación interna deberá realizarse mediante contratos definidos.

Ejemplo:

```
Gestión de Casos
       │
       ▼
Catalog Service
       │
       ▼
Catalog Contract
```

Los componentes no deberán depender de las estructuras internas de otros componentes.

La comunicación deberá utilizar:

- Interfaces.
- DTOs.
- Entidades.
- Contratos definidos.

según corresponda a cada capa.

---

# 24. Persistencia

La base de datos de V1 será:

```
PostgreSQL
```

La persistencia deberá estar aislada mediante repositorios.

Conceptualmente:

```
Domain
   │
   ▼
Repository Interface
   │
   ▼
Repository Implementation
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
```

Ninguna regla de negocio deberá realizar consultas SQL directamente.

---

# 25. Flujo Arquitectónico Completo

```
                         Usuario
                            │
                            ▼
                       Frontend
                            │
                            ▼
                          API
                            │
                            ▼
                  Process Cases Use Case
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
    Gestión de Archivos             Responsable
             │                             │
             ▼                             ▼
       Excel Service                 Catalog Service
             │                             │
             └──────────────┬──────────────┘
                            ▼
                     Gestión de Casos
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          Case Repository       Catalog Service
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    Estimation Engine
                            │
                            ▼
                       AI Service
                            │
                            ▼
                         Ollama
                            │
                            ▼
                  Resultado generado
                            │
                            ▼
                       Validación
                            │
                            ▼
                   Resultado procesado
                       │          │
                       ▼          ▼
                 Vista Previa  Exportación
```

# 26. Manejo de Errores

Los errores deberán clasificarse según su naturaleza.

### Error de entrada

Ejemplo:

```
Excel inválido
```

### Error de validación

Ejemplo:

```
Datos obligatorios incompletos
```

### Error de negocio

Ejemplo:

```
Categoría no configurada
Estado no procesable
```

### Error de infraestructura

Ejemplo:

```
Base de datos no disponible
```

### Error de IA

Ejemplo:

```
Respuesta inválida del modelo
```

Los errores deberán transformarse en resultados controlados mediante los contratos correspondientes.

---

# 27. Procesamiento Parcial

La arquitectura deberá permitir que un caso no procesable no bloquee innecesariamente el procesamiento de los demás casos válidos.

Ejemplo:

```
100 casos recibidos

80 procesables
10 estado no procesable
5 categoría no configurada
3 datos incompletos
2 errores
```

Resultado:

```
80 casos procesados
20 casos reportados con motivo
```

Cada caso deberá mantener su propio resultado de procesamiento.

---

# 28. Seguridad

La V1 no tendrá:

```
Login
JWT
Usuarios
Roles
Permisos
Sesiones
```

Por tanto, estos componentes no deberán formar parte de la arquitectura funcional de V1.

La seguridad de infraestructura deberá manejarse independientemente de la lógica funcional.

---

# 29. Integración con COMProject

La integración directa con COMProject queda fuera de V1.

La arquitectura deberá permitir posteriormente incorporar:

```
Resultado aprobado
       ↓
COMProject Service
       ↓
COMProject
```

sin modificar significativamente:

- Gestión de Casos.
- Estimation Engine.
- AI Service.
- Catalog Service.
- Case Repository.

---

# 30. Tecnologías

| Componente | Tecnología |
| --- | --- |
| Backend | FastAPI |
| Frontend | React |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy |
| Procesamiento Excel | Pandas |
| Validación | Pydantic |
| IA local | Ollama |

Estas tecnologías corresponden a las decisiones actuales de V1.

---

# 31. Principios de Dependencia

Las dependencias deberán seguir la dirección:

```
Presentation
      ↓
Application
      ↓
Domain
      ↑
Infrastructure
```

La infraestructura implementará los contratos definidos por las capas internas.

No deberá ocurrir:

```
Domain
   ↓
PostgreSQL
```

ni:

```
Domain
   ↓
Ollama
```

ni:

```
Domain
   ↓
Pandas
```

---

# 32. Reglas Arquitectónicas

### RA-01

Ningún endpoint deberá contener lógica de negocio compleja.

### RA-02

La lógica de negocio deberá mantenerse fuera de la capa de presentación.

### RA-03

Los catálogos deberán consultarse exclusivamente mediante `Catalog Service`.

### RA-04

Los módulos no deberán acceder directamente a PostgreSQL.

### RA-05

La IA deberá estar encapsulada mediante `AI Service`.

### RA-06

El modelo de IA no deberá modificar las reglas del negocio.

### RA-07

Los repositorios deberán abstraer la persistencia.

### RA-08

Los componentes deberán comunicarse mediante contratos definidos.

### RA-09

La integración con COMProject deberá permanecer desacoplada.

### RA-10

No deberán crearse módulos que no sean necesarios para V1.

### RA-11

Los componentes internos de un módulo no deberán convertirse automáticamente en módulos independientes.

### RA-12

Las restricciones de negocio deberán validarse independientemente de las recomendaciones generadas por la IA.

---

# 33. Estructura Conceptual

La estructura inicial podrá organizarse conceptualmente como:

```
backend/
│
├── api/
│
├── application/
│
├── domain/
│
├── infrastructure/
│
└── tests/
```

La estructura física definitiva deberá mantenerse alineada con el documento:

**Estructura y Convenciones del Proyecto.**

---

# 34. Pruebas

Cada componente deberá contar con pruebas apropiadas.

## Unitarias

Para:

- Validadores.
- Filtros.
- Normalizadores.
- Reglas de dominio.
- Estimation Engine.
- Transformaciones.
- Validaciones de resultados.

## Integración

Para:

- PostgreSQL.
- Repositories.
- Catalog Service.
- Excel Service.
- Ollama.
- Integración entre componentes.

## End-to-End

Para validar el flujo principal:

```
Excel
 ↓
Responsable
 ↓
Casos
 ↓
Filtrado
 ↓
Estimación
 ↓
IA
 ↓
Validación
 ↓
Resultado
 ↓
Exportación
```

---

# 35. Escalabilidad

La arquitectura permitirá posteriormente incorporar:

- Integración con COMProject.