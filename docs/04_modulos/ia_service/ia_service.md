**Proyecto:** BOT-COMProject

**Versión:** 1.0

**Estado:** Definido

---

# 1. Objetivo

El **AI Service** es el componente responsable de gestionar la interacción entre BOT-COMProject y el modelo de Inteligencia Artificial local utilizado para generar:

- Una recomendación de tiempo.
- Una descripción profesional de la actividad realizada.

El servicio utilizará un modelo local mediante **Ollama**.

El AI Service deberá trabajar exclusivamente con el contexto autorizado proporcionado por el flujo de procesamiento.

> **La IA no es la fuente de verdad de las reglas de negocio.**
> 

Las reglas relacionadas con categorías y rangos de tiempo son definidas por los catálogos y aplicadas mediante los servicios correspondientes.

---

# 2. Responsabilidades

El AI Service será responsable de:

- Recibir el contexto preparado para la IA.
- Construir la solicitud al modelo.
- Incluir las restricciones proporcionadas por el Estimation Engine.
- Ejecutar la inferencia mediante Ollama.
- Procesar la respuesta del modelo.
- Validar la estructura básica de la respuesta.
- Convertir la respuesta al contrato esperado por el sistema.
- Informar errores de inferencia.
- Entregar la recomendación al Estimation Engine.

---

# 3. Responsabilidades que NO corresponden al módulo

El AI Service **no será responsable de**:

- Definir rangos de tiempo.
- Crear categorías.
- Modificar categorías.
- Crear reglas de negocio.
- Modificar el Catálogo de Tiempos.
- Determinar qué estados son procesables.
- Seleccionar responsables.
- Filtrar casos.
- Acceder directamente a PostgreSQL.
- Leer archivos Excel.
- Registrar información en COMProject.
- Decidir si un caso es procesable.
- Aceptar definitivamente una estimación fuera de las reglas.

La validación de negocio de la estimación corresponde al **Estimation Engine**.

---

# 4. Modelo de IA

La V1 utilizará:

```
Ollama
   │
   ▼
Modelo local configurado
```

El modelo concreto será configurable mediante la configuración de la aplicación.

El AI Service no deberá depender de un modelo específico en su lógica de negocio.

Por ejemplo:

```
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

Esto permitirá cambiar posteriormente el modelo sin modificar la lógica principal del servicio.

---

# 5. Entradas

El AI Service recibirá un contexto preparado por el `Estimation Engine`.

El contexto deberá contener únicamente información necesaria para realizar la tarea.

Ejemplo:

```
{
  "case": {
    "codigo": "INC001245",
    "proyecto": "Hospital Militar",
    "categoria_final": "Ingreso de Huella",
    "descripcion": "Se reporta inconveniente con el dispositivo...",
    "solucion": "Se realizó configuración y validación...",
    "estado": "Solucionado"
  },
  "estimation_rule": {
    "min_minutes": 30,
    "max_minutes": 60
  }
}
```

---

# 6. Información autorizada

La IA podrá utilizar:

- Código del caso.
- Proyecto.
- Categoría final.
- Descripción.
- Solución.
- Estado.
- Rango mínimo.
- Rango máximo.

La información deberá provenir del contexto preparado por el sistema.

La IA no deberá recibir información innecesaria que pueda afectar la generación del resultado.

---

# 7. Tareas de la IA

En V1 el modelo tendrá dos responsabilidades principales.

## 7.1 Recomendar tiempo

La IA deberá recomendar un tiempo dentro del rango proporcionado.

Ejemplo:

```
Rango autorizado:

30 - 60 minutos

Recomendación:

45 minutos
```

La IA **no podrá modificar el rango**.

---

## 7.2 Generar descripción

La IA deberá generar una descripción profesional basada en:

- Descripción del caso.
- Solución registrada.
- Categoría final.
- Proyecto.
- Información contextual disponible.

La descripción deberá representar las actividades realizadas sin inventar información.

---

# 8. Restricciones para la IA

La solicitud al modelo deberá establecer explícitamente que:

```
1. Debe utilizar únicamente la información proporcionada.
2. No debe inventar actividades.
3. No debe crear información que no esté presente.
4. No debe modificar la categoría.
5. No debe crear categorías.
6. No debe modificar el rango autorizado.
7. El tiempo debe estar dentro del rango proporcionado.
8. Debe devolver únicamente la estructura solicitada.
```

Estas restricciones forman parte del contrato entre el sistema y el modelo.

---

# 9. Contrato de entrada

El AI Service recibirá conceptualmente:

```
{
  "case_context": {
    "codigo": "INC001245",
    "proyecto": "Hospital Militar",
    "categoria_final": "Ingreso de Huella",
    "descripcion": "Descripción original...",
    "solucion": "Solución registrada...",
    "estado": "Solucionado"
  },
  "constraints": {
    "min_minutes": 30,
    "max_minutes": 60
  }
}
```

Los nombres definitivos de los campos deberán mantenerse consistentes con el `Case Contract` y el contrato del `Estimation Engine`.

---

# 10. Contrato de salida

El AI Service deberá devolver una estructura controlada.

Ejemplo:

```
{
  "estimated_minutes": 45,
  "description": "Se realizó la configuración y validación del dispositivo de acuerdo con la solución registrada en el caso."
}
```

La respuesta deberá contener como mínimo:

```
estimated_minutes
description
```

---

# 11. Formato de respuesta de la IA

El modelo deberá recibir instrucciones para responder exclusivamente en JSON.

Ejemplo:

```
{
  "estimated_minutes": 45,
  "description": "Descripción profesional..."
}
```

No deberá aceptarse como respuesta válida una salida como:

```
Creo que el tiempo adecuado sería 45 minutos.
```

o:

```
Tiempo: 45 minutos
Descripción: ...
```

La respuesta deberá transformarse al contrato interno definido por el sistema o rechazarse si no puede interpretarse de manera segura.

---

# 12. Validación estructural

El AI Service deberá validar que la respuesta tenga:

```
estimated_minutes
description
```

Además:

### `estimated_minutes`

Debe:

- Existir.
- Ser numérico.
- Representar minutos.
- No ser negativo.
- Poder convertirse al tipo definido por el contrato.

### `description`

Debe:

- Existir.
- Ser texto.
- No estar vacía.

---

# 13. Validación del rango

La validación de negocio del rango corresponde al `Estimation Engine`.

Por lo tanto:

```
AI Service
     │
     ▼
Respuesta IA
     │
     ▼
Estimation Engine
     │
     ▼
¿Está dentro del rango?
```

El AI Service puede realizar validaciones estructurales, pero **no sustituye la validación del Estimation Engine**.

Ejemplo:

```
IA:

estimated_minutes = 25

Rango:

30 - 60
```

El AI Service puede entregar el valor estructurado:

```
{
  "estimated_minutes": 25
}
```

El Estimation Engine determinará:

```
25 < 30
```

y rechazará el resultado.

---

# 14. Descripción profesional

La descripción generada deberá:

- Ser clara.
- Ser profesional.
- Representar la actividad realizada.
- Utilizar la información disponible.
- Evitar información inventada.
- Evitar referencias innecesarias a la IA.
- Mantener relación con la solución registrada.

Ejemplo de información:

```
Descripción:
Se reporta inconveniente con la configuración de un dispositivo.

Solución:
Se realizó configuración y validación.
```

Resultado esperado:

```
Se realizó la configuración y validación del dispositivo
de acuerdo con la solución registrada en el caso.
```

---

# 15. Información no disponible

Cuando la información necesaria no esté disponible, la IA **no deberá inventarla**.

Ejemplo:

```
Descripción:
Se requiere configurar un punto de red.

Solución:
[Vacía]
```

La IA no deberá afirmar:

```
Se realizó la instalación física del punto de red y se verificó la conectividad.
```

si dicha información no está disponible.

En estos casos deberá generar una descripción basada únicamente en la información disponible o informar que no existe suficiente contexto, según las reglas que se establezcan para el resultado.

---

# 16. Construcción del Prompt

La construcción del prompt deberá estar centralizada en el AI Service.

Conceptualmente:

```
AI Service
    │
    ├── System Instructions
    │
    ├── Case Context
    │
    └── Constraints
            │
            ▼
          Prompt
            │
            ▼
          Ollama
```

El prompt no deberá contener rangos de categorías escritos manualmente.

Incorrecto:

```
Ingreso de Huella = 30-60
```

Correcto:

```
Categoría:
Ingreso de Huella

Rango autorizado:
30-60 minutos
```

El rango debe llegar dinámicamente desde el `Estimation Engine`.

---

# 17. Prompt de sistema

El prompt de sistema deberá establecer las restricciones generales del comportamiento de la IA.

Conceptualmente:

```
Eres un asistente encargado de analizar casos de soporte
y generar una recomendación de tiempo y una descripción
profesional.

Debes utilizar exclusivamente la información proporcionada.

No debes inventar información.

No debes modificar la categoría.

No debes crear reglas.

Debes recomendar un tiempo dentro del rango autorizado.

Debes responder exclusivamente en el formato JSON solicitado.
```

El texto definitivo del prompt podrá evolucionar durante las pruebas del modelo.

---

# 18. Parámetros del modelo

Los parámetros de Ollama deberán ser configurables.

Como mínimo se deberá contemplar configuración para:

| Parámetro | Tipo | Valor por Defecto | Descripción |
|-----------|------|-------------------|-------------|
| `AI_MODEL` | String | `qwen2.5:latest` | Modelo a utilizar |
| `AI_TEMPERATURE` | Float | `0.3` | Temperatura del modelo |
| `AI_TIMEOUT` | Integer | `60` | Timeout en segundos |
| `AI_MAX_TOKENS` | Integer | `500` | Máximo de tokens en respuesta |

Ejemplo conceptual:

```
AI_MODEL=qwen2.5:latest
AI_TEMPERATURE=0.3
AI_TIMEOUT=60
AI_MAX_TOKENS=500
```

Los valores concretos podrán ajustarse durante las pruebas del modelo.

---

# 19. Errores

El AI Service deberá manejar al menos:

| Código | Descripción |
| --- | --- |
| `AI_CONNECTION_ERROR` | No fue posible comunicarse con Ollama |
| `AI_TIMEOUT` | El modelo no respondió dentro del tiempo permitido |
| `AI_INVALID_RESPONSE` | La respuesta no tiene el formato esperado |
| `AI_EMPTY_RESPONSE` | El modelo no devolvió contenido |
| `AI_PARSE_ERROR` | No fue posible interpretar la respuesta |
| `AI_MODEL_ERROR` | Error producido por el modelo |
| `AI_CONFIGURATION_ERROR` | Configuración inválida del servicio |

---

# 20. Reintentos

El AI Service podrá implementar reintentos ante errores técnicos temporales.

Ejemplo:

```
Solicitud
   │
   ▼
Ollama
   │
   ├── Éxito ──► Resultado
   │
   └── Error
          │
          ▼
       Reintento
```

Sin embargo, un resultado semánticamente inválido, como un tiempo fuera del rango, **no deberá considerarse automáticamente un error técnico**.

La estrategia de regeneración de una estimación fuera de rango deberá ser definida explícitamente antes de implementarse.

---

# 21. Separación entre errores técnicos y errores de negocio

El sistema deberá distinguir:

### Error técnico

```
Ollama no responde
```

o:

```
Timeout
```

### Resultado inválido de negocio

```
Rango autorizado: 30-60
IA: 75
```

La diferencia es importante:

```
Error técnico
     ↓
AI Service

Resultado fuera de reglas
     ↓
Estimation Engine
```

---

# 22. Dependencias

El AI Service dependerá de:

```
AI Provider
     │
     ▼
Ollama
```

No deberá depender directamente de:

```
PostgreSQL
Excel Service
Case Repository
Catalog Service
COMProject
Frontend
```

El rango de tiempo será recibido como parte del contexto del `Estimation Engine`.

---

# 23. Abstracción del proveedor de IA

El servicio deberá utilizar una abstracción que permita cambiar el proveedor posteriormente.

Conceptualmente:

```
             AI Service
                 │
                 ▼
          AI Provider Interface
                 │
        ┌────────┴─────────┐
        ▼                  ▼
 Ollama Provider       Futuro Provider
```

Para V1:

```
AI Provider
     │
     ▼
Ollama
```

Esto evita que el dominio dependa directamente de la implementación concreta de Ollama.

---

# 24. Persistencia

El AI Service no deberá acceder directamente a la base de datos.

La persistencia de:

- Tiempo estimado.
- Descripción.
- Resultado de IA.
- Metadatos de procesamiento.

será responsabilidad de los componentes de aplicación y persistencia definidos en la arquitectura.

---

# 25. Seguridad y control de información

El AI Service deberá trabajar únicamente con información autorizada por el sistema.

No deberá:

- Exponer información innecesaria.
- Incorporar datos externos no autorizados.
- Consultar fuentes externas para completar información.
- Modificar la información original del caso.

La información original del Excel deberá mantenerse separada de la información generada por la IA.

---

# 26. Reglas del módulo

### RAI-01 — IA local

La V1 utilizará un modelo local mediante Ollama.

### RAI-02 — Contexto autorizado

La IA solo podrá utilizar información proporcionada por el sistema.

### RAI-03 — Sin invención

La IA no podrá inventar actividades, soluciones, resultados o datos.

### RAI-04 — Categoría inmutable

La IA no podrá modificar la categoría final.

### RAI-05 — Rango inmutable

La IA no podrá modificar el rango autorizado.

### RAI-06 — Reglas externas

La IA no podrá crear ni modificar reglas de negocio.

### RAI-07 — Respuesta estructurada

La IA deberá responder mediante el formato definido por el contrato.

### RAI-08 — Validación

Toda respuesta deberá pasar por las validaciones correspondientes antes de considerarse válida.

### RAI-09 — Sin acceso directo a catálogos

La IA no consultará directamente el Catálogo de Tiempos.

### RAI-10 — Sin acceso directo a base de datos

La IA no accederá directamente a PostgreSQL.

### RAI-11 — Sin integración externa

La IA no se comunicará directamente con COMProject.

### RAI-12 — Proveedor desacoplado

La lógica del sistema no deberá depender directamente de una implementación específica de Ollama.

---

# 27. Flujo completo

```
                 Caso procesable
                       │
                       ▼
              Estimation Engine
                       │
                       ▼
             Rango autorizado
                       │
                       ▼
              Context Builder
                       │
                       ▼
                  AI Service
                       │
                       ▼
               Construir Prompt
                       │
                       ▼
                AI Provider
                       │
                       ▼
                    Ollama
                       │
                       ▼
                 Modelo local
                       │
                       ▼
              Respuesta JSON
                       │
                       ▼
            Validación estructural
                       │
                ┌──────┴──────┐
                │             │
              Válida        Inválida
                │             │
                ▼             ▼
             Resultado       Error
                │
                ▼
          Estimation Engine
                │
                ▼
       Validación de negocio
                │
                ▼
       Resultado procesado
```

---

# 28. Ejemplo completo

### Entrada

```
{
  "case_context": {
    "codigo": "INC001245",
    "proyecto": "Hospital Militar",
    "categoria_final": "Configurar punto de red Usuarios y/o proyectos",
    "descripcion": "Usuario solicita configuración de punto de red.",
    "solucion": "Se realizó la configuración solicitada.",
    "estado": "Solucionado"
  },
  "constraints": {
    "min_minutes": 30,
    "max_minutes": 40
  }
}
```

### Respuesta esperada

```
{
  "estimated_minutes": 35,
  "description": "Se realizó la configuración del punto de red solicitado, de acuerdo con la solución registrada en el caso."
}
```

### Validación posterior

```
30 ≤ 35 ≤ 40
```

Resultado:

```
VALID
```

---

# 29. Criterios de aceptación

El AI Service se considerará correctamente implementado cuando:

- Utilice Ollama como proveedor local.
- Reciba un contexto estructurado.
- Reciba los límites de tiempo proporcionados por el sistema.
- Genere una recomendación de tiempo.
- Genere una descripción profesional.
- Devuelva una estructura JSON válida.
- Detecte respuestas malformadas.
- Detecte respuestas vacías.
- Maneje errores de comunicación.
- Maneje timeouts.
- No invente información.
- No modifique categorías.
- No modifique rangos.
- No cree reglas.
- No acceda directamente a PostgreSQL.
- No acceda directamente al Catálogo de Tiempos.
- No interactúe directamente con COMProject.
- Mantenga desacoplado el proveedor de IA.
- Permita cambiar el modelo mediante configuración.

---

# 30. Relación con otros documentos

| Documento | Relación |
| --- | --- |
| Project Charter | Define el uso de IA local en V1 |
| Análisis del Proceso de Negocio | Define la generación de tiempo y descripción |
| Mapa de Módulos | Define la responsabilidad del AI Service |
| Gestión de Casos | Proporciona casos procesables |
| Estimation Engine | Proporciona contexto y restricciones |
| Catálogo de Tiempos | Fuente indirecta de los rangos |
| Case Contract | Define estructura de información del caso |
| Modelo de Datos | Define persistencia de resultados |
| Contrato de IA | Define la interfaz específica de entrada/salida |

---

# 31. Regla de consistencia

> **El AI Service es un consumidor de reglas, no una fuente de reglas.**
> 

La autoridad sobre el tiempo seguirá este flujo:

```
Catálogo de Tiempos
        │
        ▼
Catalog Service
        │
        ▼
Estimation Engine
        │
        ▼
AI Service
        │
        ▼
Recomendación
        │
        ▼
Estimation Engine
        │
        ▼
Validación
```

La IA puede **recomendar**, pero el sistema decide si esa recomendación es válida.