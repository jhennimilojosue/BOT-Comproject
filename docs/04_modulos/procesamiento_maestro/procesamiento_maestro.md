**Proyecto:** BOT-COMProject

**Versión:** 1.1

**Estado:** Definido

**Tipo:** Contrato técnico / Diseño de módulo

---

# 1. Objetivo

El **Excel Service** es el componente responsable de procesar técnicamente el Maestro de Casos exportado desde Aranda y transformar su contenido en una colección de casos que pueda ser utilizada por el módulo **Gestión de Casos**.

Su responsabilidad se limita a:

- Recibir el archivo Excel.
- Validar su estructura.
- Identificar las columnas requeridas.
- Extraer la información necesaria.
- Transformar los valores al formato interno esperado.
- Normalizar los datos de entrada.
- Reportar errores relacionados con el archivo o su estructura.
- Entregar los casos al flujo de Gestión de Casos.

El Excel Service **no debe aplicar reglas de negocio relacionadas con la selección de casos, estimación de tiempos o generación de contenido mediante IA**.

---

# 2. Responsabilidades

El Excel Service será responsable de:

- Recibir archivos `.xlsx`.
- Validar que el archivo pueda ser procesado.
- Validar la estructura requerida.
- Identificar los encabezados del Maestro de Casos.
- Extraer las columnas necesarias.
- Transformar los valores al modelo interno de `Case`.
- Normalizar información técnica del archivo.
- Detectar errores estructurales.
- Informar registros que no puedan ser interpretados correctamente.
- Entregar una colección de casos al módulo Gestión de Casos.

---

# 3. Exclusiones

El Excel Service **no será responsable de**:

- Determinar si un caso es procesable.
- Filtrar por responsable seleccionado.
- Determinar estados procesables.
- Consultar el Catálogo de Estados.
- Consultar el Catálogo de Tiempos.
- Determinar si una categoría está configurada.
- Calcular tiempos.
- Utilizar IA.
- Generar descripciones.
- Registrar resultados en COMProject.
- Exportar resultados finales.
- Aplicar reglas de negocio de estimación.

La separación será:

```
Excel Service
      │
      │ Extrae y normaliza
      ▼
Gestión de Casos
      │
      │ Aplica reglas de negocio
      ▼
Estimation Engine
```

---

# 4. Entrada

El servicio recibirá:

```
Archivo Excel (.xlsx)
```

El archivo corresponde al **Maestro de Casos exportado desde Aranda**.

---

# 5. Formato esperado

El formato principal esperado será:

```
.xlsx
```

El Excel Service deberá trabajar con la estructura oficial definida para el Maestro de Casos.

La estructura deberá considerarse un contrato de entrada del sistema.

Si la estructura requerida no está presente, el procesamiento deberá detenerse antes de entregar casos al siguiente módulo.

---

# 6. Información requerida

El Excel Service deberá identificar y extraer, como mínimo, la información necesaria para construir el modelo interno de `Case`.

### 6.1 Mapeo de columnas Excel

| Nombre Físico Excel | Campo Interno | Obligatorio |
|---------------------|---------------|-------------|
| `Codigo Caso` | `case_code` | Sí |
| `Tipo Caso` | `case_type` | Sí |
| `Responsible Name` | `responsible_name` | Sí |
| `Proyecto` | `project` | Sí |
| `Fecha` | `registered_at` | Sí |
| `Estado` | `status` | Sí |
| `Categoria` | `final_category` | Sí |
| `Descripcion` | `description` | Sí |
| `Solucion` | `solution` | Sí |
| `Usuario` | `user_name` | No |

El nombre físico de las columnas deberá corresponder exactamente con los valores indicados en la tabla.

El Excel Service será responsable de realizar el mapeo correspondiente.

### 6.1.1 Valores de Tipo Caso

El campo `case_type` admitirá únicamente los siguientes valores:

```
Incidente
Requerimiento
```

Si el valor no coincide con uno de los permitidos, el caso deberá ser rechazado con el código `INVALID_CASE_TYPE`.

Este campo se utiliza para determinar en qué catálogo de tiempos buscar la configuración de la categoría.

### 6.2 Formato de fecha

El campo `registered_at` podrá venir en los siguientes formatos:
- `DD/MM/YYYY`
- `MM/DD/YYYY`
- `YYYY-MM-DD`

El sistema normalizará a formato ISO 8601: `YYYY-MM-DD`

### 6.3 Duplicados en el mismo archivo

Si se detectan casos con el mismo `case_code` en el mismo archivo:
- Se procesará únicamente la primera ocurrencia
- Las ocurrencias duplicadas serán omitidas sin generar error

---

# 7. Mapeo conceptual

El procesamiento deberá seguir conceptualmente:

```
Maestro de Casos
       │
       ▼
Identificación de columnas
       │
       ▼
Mapeo de campos
       │
       ▼
Transformación
       │
       ▼
Normalización
       │
       ▼
Case
```

Ejemplo:

```
Código Caso
     ↓
case_code

Responsible Name
     ↓
responsible_name

Categoría
     ↓
final_category
```

---

# 8. Validación del archivo

Antes de procesar los registros, el Excel Service deberá validar:

### 8.1 Extensión

El archivo deberá tener una extensión soportada:

```
.xlsx
```

---

### 8.2 Archivo legible

El sistema deberá verificar que el archivo pueda ser abierto correctamente.

Si el archivo está:

- corrupto,
- incompleto,
- protegido de una forma no soportada,
- o no puede ser interpretado,

el procesamiento deberá finalizar con un error de archivo.

---

### 8.3 Estructura

El sistema deberá verificar que existan las columnas requeridas.

Ejemplo:

```
Código Caso
Responsible Name
Proyecto
Estado
Categoría
Descripción
Solución
```

Si falta una columna obligatoria, el archivo no podrá continuar.

---

# 9. Identificación de encabezados

El Excel Service deberá identificar correctamente la fila que contiene los encabezados reales del Maestro de Casos.

No deberá asumir necesariamente que los encabezados se encuentran en la primera fila si el formato oficial del Maestro contiene filas previas.

El servicio deberá trabajar con la estructura definida para el Maestro de Casos.

---

# 10. Extracción de información

Una vez identificada la estructura, el servicio deberá extraer únicamente la información necesaria para el funcionamiento de BOT-COMProject.

Conceptualmente:

```
Excel
 │
 ├── Código
 ├── Responsable
 ├── Usuario
 ├── Proyecto
 ├── Fecha
 ├── Estado
 ├── Categoría
 ├── Descripción
 └── Solución
```

La información no requerida para el procesamiento no deberá incorporarse al modelo interno salvo que exista una decisión posterior que lo justifique.

---

# 11. Normalización

El Excel Service podrá realizar normalizaciones técnicas necesarias para convertir los valores del Excel a un formato consistente.

Ejemplos:

- Eliminar espacios innecesarios.
- Convertir valores vacíos a `None`.
- Normalizar fechas.
- Convertir tipos de datos.
- Normalizar representaciones textuales.
- Eliminar caracteres no deseados producto del formato del Excel.

Ejemplo:

```
"  Solucionado  "
        ↓
"Solucionado"
```

La normalización **no deberá cambiar el significado del dato de negocio**.

---

# 12. Diferencia entre normalización y reglas de negocio

El Excel Service podrá realizar:

```
"  Juan Pérez  "
       ↓
"Juan Pérez"
```

Pero no podrá decidir:

```
Solucionado → Procesable
```

Esta decisión corresponde al **Catálogo de Estados** y al flujo de **Gestión de Casos**.

De igual manera, el Excel Service podrá extraer:

```
Categoría:
Configurar punto de red
```

pero no podrá determinar:

```
30 - 40 minutos
```

Esta responsabilidad corresponde al `Catalog Service` y al `Estimation Engine`.

---

# 13. Modelo de salida

El Excel Service deberá entregar una colección de objetos compatibles con el contrato `Case`.

Conceptualmente:

```
{
  "case_code": "INC001245",
  "user_name": "Juan Pérez",
  "responsible_name": "Carlos Rodríguez",
  "project": "Hospital Militar",
  "registered_at": "2026-08-10",
  "status": "Solucionado",
  "final_category": "Ingreso de Huella",
  "description": "Problema con el registro de huella.",
  "solution": "Se realizó la configuración correspondiente."
}
```

El objeto deberá cumplir con el **Case Contract** definido para el proyecto.

---

# 14. Salidas

El Excel Service tendrá dos resultados principales.

## 14.1 Procesamiento exitoso

```
Excel
   ↓
Validación
   ↓
Extracción
   ↓
Normalización
   ↓
Collection[Case]
```

---

## 14.2 Error de procesamiento

Cuando el archivo no pueda ser procesado correctamente, deberá devolver información suficiente para identificar el problema.

Ejemplo:

```
{
  "error_code": "REQUIRED_COLUMN_MISSING",
  "message": "La columna 'Responsible Name' no fue encontrada."
}
```

---

# 15. Tipos de errores

El servicio deberá diferenciar al menos entre:

### `INVALID_FILE`

Archivo inválido o no soportado.

### `UNREADABLE_FILE`

El archivo no puede ser abierto o interpretado.

### `INVALID_STRUCTURE`

La estructura del archivo no corresponde al formato esperado.

### `REQUIRED_COLUMN_MISSING`

Falta una columna obligatoria.

### `INVALID_DATA_FORMAT`

Uno o más valores no pueden convertirse al formato esperado.

---

# 16. Errores de registro

Un registro individual con información problemática no deberá confundirse con un error estructural del archivo.

Por ejemplo:

```
Archivo correcto
      │
      ├── Caso 001 → válido
      ├── Caso 002 → válido
      ├── Caso 003 → dato inválido
      └── Caso 004 → válido
```

Cuando sea técnicamente posible, el Excel Service podrá reportar el registro afectado sin detener innecesariamente todo el procesamiento.

Sin embargo, la decisión de si dicho caso puede continuar como **caso procesable** corresponde a Gestión de Casos.

---

# 17. Responsabilidad sobre campos obligatorios

Existe una separación importante:

### Excel Service

Verifica que pueda extraer y transformar correctamente la información.

### Gestión de Casos

Determina si esa información cumple las condiciones necesarias para que el caso sea procesable.

Ejemplo:

```
Excel Service
    ↓
¿Existe una columna Estado?
    ↓
Sí
    ↓
Extrae "Pendiente"
    ↓
Entrega Case
```

Después:

```
Gestión de Casos
    ↓
¿"Pendiente" es procesable?
    ↓
Catalog Service
    ↓
No
    ↓
Caso no procesable
```

---

# 18. Dependencias

El Excel Service depende de:

```
Gestión de Archivos
```

y entrega información a:

```
Gestión de Casos
```

No deberá depender directamente de:

```
Catalog Service
Estimation Engine
AI Service
COMProject
Export Service
```

---

# 19. Flujo interno

```
                 Archivo Excel
                       │
                       ▼
                File Validation
                       │
                       ▼
              Structure Validator
                       │
                       ▼
               Header Resolver
                       │
                       ▼
                Column Mapper
                       │
                       ▼
               Data Extractor
                       │
                       ▼
               Data Normalizer
                       │
                       ▼
                Case Mapper
                       │
                       ▼
                Collection[Case]
                       │
                       ▼
               Gestión de Casos
```

---

# 20. Componentes internos

El módulo podrá organizar internamente sus responsabilidades mediante componentes como:

## 20.1 File Validator

Valida que el archivo pueda ser procesado.

---

## 20.2 Structure Validator

Verifica que la estructura requerida esté presente.

---

## 20.3 Header Resolver

Identifica la fila de encabezados correspondiente al formato oficial.

---

## 20.4 Column Mapper

Relaciona las columnas del Excel con los campos internos del sistema.

---

## 20.5 Data Extractor

Extrae los valores necesarios de cada registro.

---

## 20.6 Data Normalizer

Transforma los datos a formatos consistentes.

---

## 20.7 Case Mapper

Construye el objeto `Case` utilizado por el resto del sistema.

---

# 21. Contrato con Gestión de Casos

El contrato entre ambos módulos será:

```
Excel Service
     │
     │ Collection[Case]
     ▼
Gestión de Casos
```

Excel Service garantiza:

- Estructura interna válida.
- Tipos de datos convertidos.
- Campos correctamente mapeados.
- Datos normalizados técnicamente.

Gestión de Casos garantiza:

- Aplicación de reglas de negocio.
- Filtrado por responsable.
- Validación de estados.
- Validación de categorías.
- Identificación de casos procesables.

---

# 22. Reglas del Excel Service

### REX-01 — Formato soportado

El servicio procesará archivos `.xlsx` compatibles con el formato definido para el Maestro de Casos.

### REX-02 — Estructura obligatoria

La ausencia de una columna obligatoria impedirá procesar el archivo.

### REX-03 — No reglas de negocio

El Excel Service no deberá implementar reglas de negocio relacionadas con la procesabilidad de los casos.

### REX-04 — No estimación

El Excel Service no deberá calcular ni recomendar tiempos.

### REX-05 — No IA

El Excel Service no deberá comunicarse con Ollama ni con el `AI Service`.

### REX-06 — No acceso a catálogos

El Excel Service no deberá consultar directamente los catálogos.

### REX-07 — Normalización sin alteración semántica

La normalización no deberá modificar el significado original de la información.

### REX-08 — Contrato Case

Los registros extraídos deberán transformarse al modelo definido por `Case Contract`.

### REX-09 — No integración externa

El Excel Service no deberá comunicarse con COMProject.

### REX-10 — Trazabilidad

Los errores de procesamiento deberán proporcionar información suficiente para identificar el problema y, cuando corresponda, el registro afectado.

---

# 23. Persistencia

El Excel Service **no será responsable directamente de la persistencia**.

El flujo será:

```
Excel Service
      │
      ▼
Gestión de Casos
      │
      ▼
Case Repository
      │
      ▼
PostgreSQL
```

El servicio no deberá acceder directamente a PostgreSQL.

---

# 24. Pruebas requeridas

El Excel Service deberá contar como mínimo con pruebas para:

### Archivo

- Archivo `.xlsx` válido.
- Archivo con extensión no soportada.
- Archivo corrupto.
- Archivo vacío.

### Estructura

- Todas las columnas requeridas.
- Columna obligatoria faltante.
- Encabezados incorrectos.
- Estructura inesperada.

### Datos

- Fecha válida.
- Fecha inválida.
- Valores vacíos.
- Espacios innecesarios.
- Tipos de datos inesperados.

### Transformación

- Mapeo correcto de columnas.
- Normalización correcta.
- Construcción correcta del `Case`.

### Integración

- Excel Service → Gestión de Casos.
- Error de Excel Service correctamente comunicado.

---

# 25. Principios de diseño

El módulo deberá cumplir:

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Inversión de dependencias.
- Testabilidad.
- Separación entre infraestructura y dominio.
- No dependencia de reglas de negocio externas.
- No dependencia directa de IA.
- No dependencia directa de COMProject.
- Uso del `Case Contract` como contrato de salida.

---

# 26. Relación con otros documentos

Este documento deberá mantenerse alineado con:

| Documento | Relación |
| --- | --- |
| Project Charter | Define el objetivo y alcance V1 |
| Análisis del Proceso de Negocio | Define el flujo del proceso |
| Mapa de Módulos | Define la responsabilidad del Excel Service |
| Arquitectura del Sistema | Define su ubicación arquitectónica |
| Estructura y Convenciones | Define organización y estándares de código |
| Modelo de Datos | Define las entidades persistentes |
| Case Contract | Define la estructura de salida |
| Diseño Gestión de Casos | Define el procesamiento posterior |
| Catálogo de Estados | Define estados procesables |
| Catálogo de Tiempos | Define rangos de estimación |

---

# 27. Regla de consistencia

El Excel Service deberá respetar la siguiente separación:

```
                 Excel Service
                       │
          ┌────────────┴────────────┐
          │                         │
      Técnico                    Negocio
          │                         │
     Extraer                    Filtrar
     Mapear                     Validar
     Normalizar                 Procesar
          │                         │
          ▼                         ▼
     Case Contract          Gestión de Casos
```

> **El Excel Service transforma información del archivo al modelo interno del sistema; no decide qué significa esa información dentro de las reglas del negocio.**
> 

---

# 28. Evolución futura

El módulo podrá evolucionar para soportar:

- Nuevas versiones del Maestro de Casos.
- Nuevas fuentes de información.
- Validación de diferentes formatos de Excel.
- Versionamiento del esquema de entrada.
- Procesamiento de grandes volúmenes.
- Detección técnica de cambios estructurales.
- Soporte para otros formatos de archivo.

Estas extensiones deberán mantener la responsabilidad principal del módulo y no incorporar reglas pertenecientes a otros componentes.

---

# 29. Definición del módulo

La definición oficial del Excel Service para V1 es:

> **Excel Service es el componente encargado de recibir el Maestro de Casos de Aranda, validar su estructura, extraer la información requerida, normalizarla técnicamente y transformarla al contrato interno de `Case`, entregando los datos a Gestión de Casos sin aplicar reglas de negocio de procesabilidad, estimación o inteligencia artificial.**
>

---

# 30. Control de Versión

| Versión | Estado | Cambios principales |
| --- | --- | --- |
| 1.0 | Definido | Contrato inicial del Excel Service |
| **1.1** | **Definido** | Incorporación de columna `Tipo Caso` (`case_type`) para discriminación de incidentes y requerimientos |