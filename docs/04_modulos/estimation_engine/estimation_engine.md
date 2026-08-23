**Proyecto:** BOT-COMProject

**Versión:** 1.0

**Estado:** Definido

---

# 1. Objetivo

El **Estimation Engine** es el componente responsable de coordinar la determinación del tiempo estimado para cada caso procesable.

Su función principal es utilizar:

- La categoría final del caso.
- La configuración correspondiente del Catálogo de Tiempos.
- La información contextual del caso.
- El `AI Service`.

para obtener una recomendación de tiempo y garantizar que dicha recomendación cumpla las reglas autorizadas.

El Estimation Engine **no define ni modifica los rangos de tiempo**.

Los rangos son definidos por el **Catálogo de Tiempos** y consultados mediante el **Catalog Service**.

---

# 2. Responsabilidades

El Estimation Engine será responsable de:

- Recibir casos procesables desde Gestión de Casos.
- Identificar la categoría final del caso.
- Consultar la configuración de la categoría mediante `Catalog Service`.
- Obtener el rango mínimo y máximo autorizado.
- Construir el contexto necesario para la estimación.
- Solicitar una recomendación al `AI Service`.
- Recibir el resultado generado por la IA.
- Validar que el tiempo recomendado esté dentro del rango autorizado.
- Validar la estructura del resultado.
- Rechazar resultados inválidos.
- Entregar el tiempo validado al flujo de procesamiento.
- Entregar la información necesaria para la generación de la descripción profesional.

---

# 3. Responsabilidades que NO corresponden al módulo

El Estimation Engine **no será responsable de**:

- Definir categorías.
- Crear categorías.
- Definir rangos de tiempo.
- Modificar rangos.
- Crear reglas de negocio.
- Modificar catálogos.
- Filtrar casos por responsable.
- Determinar si un estado es procesable.
- Leer directamente el Excel.
- Acceder directamente a PostgreSQL.
- Comunicarse directamente con COMProject.
- Ejecutar directamente Ollama.
- Permitir tiempos fuera del rango autorizado.

La interacción con Ollama será responsabilidad del `AI Service`.

---

# 4. Entradas

El Estimation Engine recibirá un caso procesable proveniente de **Gestión de Casos**.

El contexto mínimo podrá contener:

```
{
  "codigo": "INC001245",
  "responsable": "Carlos Rodríguez",
  "proyecto": "Hospital Militar",
  "categoria_final": "Ingreso de Huella",
  "descripcion": "...",
  "solucion": "...",
  "estado": "Solucionado"
}
```

El caso deberá haber pasado previamente por las validaciones correspondientes de Gestión de Casos.

---

# 5. Obtención del rango de tiempo

El Estimation Engine deberá consultar el `Catalog Service`.

El flujo será:

```
Caso procesable
       │
       ▼
Categoría final
       │
       ▼
Catalog Service
       │
       ▼
Catálogo de Tiempos
       │
       ▼
Configuración activa
       │
       ├── mínimo
       └── máximo
```

Ejemplo:

```
Categoría:
Configurar punto de red Usuarios y/o proyectos

Rango autorizado:
30 - 40 minutos
```

El Estimation Engine utilizará estos valores como restricciones para la estimación.

---

# 6. Categoría final

El Estimation Engine utilizará exclusivamente:

```
categoria_final
```

proveniente del caso.

No deberá utilizar:

- Categorías anteriores.
- Subcategorías anteriores.
- Interpretaciones de la IA para cambiar la categoría.
- Categorías inventadas por el modelo.

El flujo será:

```
Caso
 │
 └── categoria_final
          │
          ▼
    Catalog Service
          │
          ▼
   Configuración activa
```

---

# 7. Construcción del contexto

El Estimation Engine deberá construir el contexto necesario para solicitar la estimación.

El contexto podrá contener:

```
Código
Responsable
Proyecto
Categoría final
Descripción
Solución
Estado
Tiempo mínimo
Tiempo máximo
```

Ejemplo conceptual:

```
{
  "case": {
    "codigo": "INC001245",
    "proyecto": "Hospital Militar",
    "categoria_final": "Ingreso de Huella",
    "descripcion": "Configuración de dispositivo...",
    "solucion": "Se realizó la configuración...",
    "estado": "Solucionado"
  },
  "estimation_rule": {
    "min_minutes": 30,
    "max_minutes": 60
  }
}
```

El contexto deberá contener únicamente información necesaria y autorizada.

---

# 8. Comunicación con AI Service

El Estimation Engine no ejecutará directamente el modelo de IA.

La comunicación será:

```
Estimation Engine
        │
        ▼
    AI Service
        │
        ▼
      Ollama
        │
        ▼
   Modelo local
```

El `AI Service` será responsable de la interacción técnica con Ollama.

El Estimation Engine será responsable de establecer las condiciones que debe respetar la estimación.

---

# 9. Solicitud de estimación

El Estimation Engine deberá proporcionar al `AI Service`:

```
Información del caso
+
Categoría final
+
Rango mínimo
+
Rango máximo
```

Conceptualmente:

```
Estimation Engine
       │
       │ Caso + contexto + restricciones
       ▼
   AI Service
       │
       ▼
Recomendación
```

La IA deberá recibir explícitamente los límites autorizados.

---

# 10. Resultado esperado

El `AI Service` deberá devolver un resultado estructurado.

Ejemplo:

```
{
  "estimated_minutes": 35,
  "description": "Se realizó la configuración..."
}
```

El Estimation Engine deberá validar este resultado antes de aceptarlo.

---

# 11. Validación del tiempo

La validación principal será:

```
mínimo ≤ tiempo_estimado ≤ máximo
```

Ejemplo:

```
Mínimo: 30
Máximo: 40
IA:     35

30 ≤ 35 ≤ 40
```

Resultado:

```
VÁLIDO
```

---

# 12. Tiempo fuera del rango

Si la IA devuelve:

```
25 minutos
```

cuando el rango autorizado es:

```
30 - 40
```

el resultado deberá ser rechazado.

```
25 < 30
```

De igual forma:

```
45 > 40
```

también deberá ser rechazado.

La IA **no podrá modificar automáticamente el resultado para hacerlo válido** sin seguir una estrategia explícitamente definida por el sistema.

---

# 13. Estrategia ante una estimación inválida

Cuando la IA genere un tiempo fuera del rango, el Estimation Engine deberá considerar el resultado inválido.

Flujo:

```
AI Service
     │
     ▼
Resultado
     │
     ▼
¿Tiempo dentro del rango?
     │
 ┌───┴────┐
 │        │
Sí       No
 │        │
 ▼        ▼
Aceptar  Rechazar
```

El resultado rechazado deberá generar información suficiente para identificar el problema.

Ejemplo (formato interno entre módulos):

```
{
  "status": "REJECTED",
  "reason": "ESTIMATION_OUT_OF_RANGE"
}
```

> **Nota:** Este es el formato interno utilizado entre módulos. El formato expuesto a través de la API (definido en `contratos_api.md`) utiliza una estructura diferente con `reason_code` y `message` para consumo externo.

> La cantidad máxima de reintentos o la estrategia exacta para regenerar una estimación deberá definirse posteriormente en el diseño del `AI Service` si se decide utilizar reintentos.
> 

---

# 14. Validación de la respuesta

Además del rango de tiempo, el Estimation Engine deberá comprobar que la respuesta tenga una estructura válida.

Como mínimo:

```
estimated_minutes
description
```

Deberá rechazarse una respuesta cuando:

- No exista el tiempo.
- El tiempo no sea numérico.
- El tiempo sea menor que el mínimo.
- El tiempo sea mayor que el máximo.
- La descripción esté vacía.
- La estructura de respuesta sea inválida.

---

# 15. Generación de descripción

La descripción profesional será generada por el `AI Service` utilizando el contexto autorizado.

El Estimation Engine deberá garantizar que la información necesaria para generar dicha descripción esté disponible.

La descripción deberá representar la actividad realizada según la información disponible.

La IA no deberá inventar información que no esté presente en el contexto autorizado.

---

# 16. Resultado del Estimation Engine

Cuando el proceso sea exitoso, el Estimation Engine entregará un resultado validado.

Ejemplo:

```
{
  "codigo": "INC001245",
  "estimated_minutes": 35,
  "description": "Se realizó la configuración y validación del dispositivo de acuerdo con la solución registrada en el caso.",
  "status": "VALID"
}
```

Este resultado continuará hacia la siguiente etapa del procesamiento.

---

# 17. Flujo interno

```
                 Caso procesable
                       │
                       ▼
              Estimation Engine
                       │
                       ▼
              Obtener categoría
                       │
                       ▼
               Catalog Service
                       │
                       ▼
              Obtener rango activo
                       │
                       ▼
            Construir contexto
                       │
                       ▼
                  AI Service
                       │
                       ▼
              Resultado de IA
                       │
                       ▼
               Validar resultado
                       │
                 ┌─────┴─────┐
                 │           │
               Válido      Inválido
                 │           │
                 ▼           ▼
              Aceptar      Rechazar
                 │
                 ▼
          Resultado procesado
```

---

# 18. Dependencias

El Estimation Engine dependerá de:

```
Catalog Service
AI Service
Case Context
```

### No dependerá directamente de:

```
Excel Service
Case Repository
PostgreSQL
Ollama
COMProject
Frontend
```

La dependencia hacia Ollama será indirecta mediante `AI Service`.

---

# 19. Catálogo de Tiempos

El Estimation Engine **no almacenará los rangos de tiempo**.

Ejemplo incorrecto:

```
if category == "Ingreso de Huella":
    minimum = 30
    maximum = 60
```

Esto no deberá existir dentro del Estimation Engine.

La información deberá obtenerse mediante:

```
Estimation Engine
        │
        ▼
Catalog Service
        │
        ▼
Catálogo de Tiempos
```

Esto permite modificar un rango desde el catálogo sin modificar el código del motor.

---

# 20. Reglas del módulo

### REE-01 — Categoría final

El Estimation Engine utilizará únicamente la categoría final proporcionada por Gestión de Casos.

### REE-02 — Catálogo centralizado

Los rangos deberán obtenerse exclusivamente mediante `Catalog Service`.

### REE-03 — Configuración activa

Solo podrá utilizarse una configuración activa del Catálogo de Tiempos.

### REE-04 — Rango obligatorio

No podrá realizarse una estimación si no existe un rango válido.

### REE-05 — Límite inferior

El tiempo estimado no podrá ser inferior al mínimo configurado.

### REE-06 — Límite superior

El tiempo estimado no podrá superar el máximo configurado.

### REE-07 — Validación obligatoria

Toda recomendación de IA deberá ser validada antes de ser aceptada.

### REE-08 — IA limitada

La IA no podrá modificar:

- Categorías.
- Rangos.
- Reglas.
- Configuraciones del catálogo.

### REE-09 — Sin reglas embebidas

El Estimation Engine no deberá contener rangos de tiempo definidos directamente en código.

### REE-10 — Resultado inválido

Una estimación que no cumpla las reglas deberá ser rechazada.

### REE-11 — Sin acceso directo a IA

El Estimation Engine no deberá comunicarse directamente con Ollama.

### REE-12 — Sin integración externa

El Estimation Engine no interactuará directamente con COMProject.

---

# 21. Manejo de errores

El módulo deberá contemplar al menos los siguientes escenarios:

| Código | Situación |
| --- | --- |
| `CATEGORY_NOT_FOUND` | Categoría no encontrada |
| `CATEGORY_NOT_ACTIVE` | Categoría sin configuración activa |
| `TIME_RANGE_INVALID` | Rango de tiempo inválido |
| `AI_INVALID_RESPONSE` | Respuesta de IA inválida |
| `ESTIMATION_OUT_OF_RANGE` | Tiempo fuera del rango |
| `DESCRIPTION_EMPTY` | Descripción vacía |
| `AI_SERVICE_ERROR` | Error del servicio de IA |
| `CATALOG_SERVICE_ERROR` | Error consultando catálogo |

Estos errores deberán permitir identificar el motivo por el cual un caso no pudo ser procesado correctamente.

---

# 22. Persistencia

El Estimation Engine no accederá directamente a la base de datos.

Si el resultado de estimación necesita almacenarse, deberá hacerlo mediante el componente de persistencia correspondiente.

Conceptualmente:

```
Estimation Engine
       │
       ▼
Application / Repository
       │
       ▼
PostgreSQL
```

El diseño específico de persistencia de `Estimation` deberá quedar definido en el **Modelo de Datos** y los contratos de persistencia correspondientes.

---

# 23. Principios de Diseño

El Estimation Engine deberá cumplir:

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Inversión de dependencias.
- Separación entre dominio e infraestructura.
- Testabilidad.
- Validaciones deterministas.
- Catálogos centralizados.
- Independencia de Ollama.
- Independencia de COMProject.
- No duplicación de reglas.
- Resultados reproducibles bajo las mismas restricciones y contexto cuando la estrategia de IA lo permita.

---

# 24. Exclusiones

El Estimation Engine no será responsable de:

- Leer Excel.
- Validar la estructura del archivo.
- Seleccionar responsables.
- Filtrar estados.
- Administrar categorías.
- Administrar catálogos.
- Crear rangos.
- Modificar rangos.
- Ejecutar Ollama directamente.
- Registrar información en COMProject.
- Exportar resultados.

---

# 25. Flujo de comunicación

```
                Gestión de Casos
                       │
                       ▼
              Estimation Engine
                       │
                       ├──────────────► Catalog Service
                       │                       │
                       │                       ▼
                       │                 Rango autorizado
                       │
                       ▼
                Context Builder
                       │
                       ▼
                  AI Service
                       │
                       ▼
                    Ollama
                       │
                       ▼
                Resultado IA
                       │
                       ▼
              Validación Engine
                       │
                 ┌─────┴─────┐
                 │           │
               Válido      Inválido
                 │           │
                 ▼           ▼
              Resultado    Error
                 │
                 ▼
             V1 Result
```

---

# 26. Criterios de aceptación

El Estimation Engine se considerará correctamente implementado cuando:

- Reciba únicamente casos procesables.
- Utilice exclusivamente la categoría final.
- Consulte el rango mediante `Catalog Service`.
- No tenga rangos de tiempo codificados directamente.
- Utilice únicamente configuraciones activas.
- Envíe el contexto necesario al `AI Service`.
- No se comunique directamente con Ollama.
- Valide el tiempo generado.
- Rechace tiempos fuera del rango.
- Valide la estructura de la respuesta.
- Detecte respuestas inválidas.
- Genere un resultado estructurado.
- Mantenga separación entre reglas y tecnología de IA.
- No tenga dependencias directas con COMProject.

---

# 27. Relación con otros documentos

Este documento deberá mantenerse alineado con:

| Documento | Relación |
| --- | --- |
| Project Charter | Define el objetivo y alcance V1 |
| Análisis del Proceso de Negocio | Define el flujo del proceso |
| Mapa de Módulos | Define la posición y responsabilidad del módulo |
| Diseño de Gestión de Casos | Define los casos que llegan al motor |
| Catálogo de Tiempos | Define los rangos autorizados |
| Catálogo de Estados | Define estados procesables |
| Catálogo de Responsables | Define responsables disponibles |
| Case Contract | Define la estructura del caso |
| AI Service | Define la interacción con la IA |
| Modelo de Datos | Define la persistencia de resultados |

---

# 28. Regla de consistencia

> **El Estimation Engine nunca podrá convertirse en la fuente de verdad de las reglas de tiempo.**
> 

La fuente de verdad será:

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
Validación
```

De esta forma, si mañana cambiamos:

```
30 - 60
```

por:

```
40 - 70
```

el código del Estimation Engine **no debería modificarse**.