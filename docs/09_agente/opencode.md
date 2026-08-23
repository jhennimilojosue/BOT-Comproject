Proyecto: BOT-COMProject
Versión: 1.1
Estado: Definido
Tipo: Instrucciones de implementación para agente de desarrollo

1. Propósito

Este documento define las instrucciones que OpenCode deberá seguir para analizar, diseñar, implementar, probar y mantener el código fuente del proyecto BOT-COMProject.

OpenCode deberá utilizar la documentación existente en /docs como fuente principal de conocimiento del proyecto.

El objetivo es evitar que OpenCode:

Invente reglas de negocio.
Modifique decisiones arquitectónicas sin autorización.
Cree estructuras que contradigan la documentación.
Implemente funcionalidades fuera del alcance V1.
Duplique responsabilidades entre módulos.
Acceda directamente a infraestructura cuando exista una abstracción definida.
Modifique datos originales provenientes de Aranda.
Permita que la IA determine reglas que pertenecen al negocio.
Cree entidades, endpoints o módulos no definidos en el alcance.
Resuelva contradicciones documentales mediante suposiciones.
2. Principio fundamental

OpenCode deberá considerar la documentación del proyecto como la fuente de verdad para la implementación.

Antes de implementar una funcionalidad deberá:

Identificar qué documento define la funcionalidad.
Leer las reglas relacionadas.
Identificar las entidades involucradas.
Identificar las dependencias entre módulos.
Verificar los contratos existentes.
Implementar respetando la arquitectura definida.
Crear o actualizar las pruebas correspondientes.
Ejecutar las pruebas.
Verificar que la implementación no contradiga otros documentos.

OpenCode no deberá implementar una decisión únicamente porque sea una práctica común o porque considere que existe una alternativa técnicamente mejor.

Si existe una decisión explícita en la documentación, deberá respetarla.

3. Alcance V1

OpenCode deberá implementar exclusivamente las funcionalidades definidas para BOT-COMProject V1.

No deberá implementar anticipadamente funcionalidades futuras como:

Usuarios.
Autenticación.
Roles.
Permisos.
JWT.
Auditoría avanzada.
Administración de catálogos mediante interfaz.
Integración con COMProject.
Versionamiento de reglas.
Versionamiento de catálogos.
Historial avanzado.
Funcionalidades no definidas en la documentación V1.

Si una funcionalidad futura es necesaria para realizar correctamente una implementación actual, OpenCode deberá detenerse y reportar la dependencia antes de inventar una solución.

3.1 Conflictos entre documentos

Esta sección define cómo deberá comportarse OpenCode cuando encuentre información contradictoria dentro de la documentación del proyecto.

Estas reglas no son reglas de negocio de BOT-COMProject.

Son reglas de comportamiento para OpenCode respecto al uso de la documentación.

3.1.1 Lectura inicial del proyecto

Antes de realizar la primera implementación del proyecto, OpenCode deberá realizar una revisión inicial de la documentación disponible en /docs.

Deberá identificar como mínimo:

Propósito y alcance del proyecto.
Proceso general de negocio.
Arquitectura.
Módulos existentes.
Dependencias entre módulos.
Catálogos.
Contratos.
Modelo de datos.
API.
Convenciones de desarrollo.
Reglas específicas de comportamiento de OpenCode.

Esta revisión inicial tendrá como objetivo construir un contexto general del proyecto.

OpenCode no deberá asumir que el documento de la tarea actual es la única fuente necesaria para implementar una funcionalidad.

Posteriormente, para cada tarea, deberá realizar la lectura específica de los documentos relacionados siguiendo la regla definida en la sección 6. Regla de lectura documental.

Con eso conseguimos algo muy importante:

INICIO DEL PROYECTO
        │
        ▼
Leer README.md
        │
        ▼
Leer documentación general
        │
        ▼
Construir contexto del proyecto
        │
        ▼
Recibir tarea
        │
        ▼
Identificar fuente de verdad
        │
        ▼
Leer documentación específica
        │
        ▼
Analizar dependencias
        │
        ▼
Plan
        │
        ▼
Implementar
        │
        ▼
Pruebas
        │
        ▼
Validación documental
        │
        ▼
Reporte

3.1.2 No resolver conflictos automáticamente

OpenCode no deberá resolver por criterio propio una contradicción documental.

No deberá:

Elegir arbitrariamente uno de los documentos.
Utilizar la definición que considere técnicamente mejor.
Utilizar la definición del documento más reciente sin verificar la decisión.
Modificar uno de los documentos para eliminar la contradicción.
Implementar ambas definiciones simultáneamente.
Crear una regla intermedia no documentada.

Cuando el conflicto afecte una parte necesaria de la implementación, OpenCode deberá detener esa parte y solicitar una decisión.

3.1.3 Ámbito de autoridad

OpenCode deberá identificar qué documento es responsable de definir cada aspecto del sistema.

Como principio general:

Área	Fuente de verdad
Propósito y alcance	Project Charter
Terminología	Glosario
Proceso de negocio	Análisis del Proceso de Negocio
Arquitectura	Documentos de 02_arquitectura/
Estructura y convenciones técnicas	03_desarrollo/
Responsabilidades de módulos	Documentos de 04_modulos/
Estados	catalogo_estados.md
Responsables	catalogo_responsables.md
Tiempos y rangos	catalogo_tiempos.md
Estructura de casos	case_contract.md
Persistencia	modelo_datos_modulo.md
API	contratos_api.md
Comportamiento de OpenCode	opencode.md

Esta tabla establece qué documento debe consultarse primero para cada tipo de decisión.

No significa que un documento pueda ignorar las definiciones de otros documentos relacionados.

3.1.4 Conflictos entre documentos de diferentes áreas

Cuando dos documentos de áreas diferentes entren en conflicto, OpenCode deberá identificar cuál de los documentos tiene autoridad sobre la decisión específica.

Por ejemplo:

Catálogo de Tiempos
        ↓
Define los rangos autorizados


Estimation Engine
        ↓
Utiliza esos rangos

El Estimation Engine no deberá redefinir el rango establecido por el Catálogo de Tiempos.

De igual forma:

Catálogo de Estados
        ↓
Define estados procesables


Gestión de Casos
        ↓
Consume esa definición

Gestión de Casos no deberá crear una lista independiente de estados procesables.

3.1.5 Conflictos dentro de una misma área

Si dos documentos pertenecientes a la misma área presentan definiciones diferentes, OpenCode deberá tratarlo como un conflicto documental.

Ejemplo:

catalogo_tiempos.md


30 - 60 minutos

y:

estimation_engine.md


40 - 60 minutos

OpenCode no deberá asumir que el segundo documento modifica al primero.

Deberá reportar:

Existe una contradicción entre las definiciones.
Se requiere una decisión documental antes de continuar.
3.1.6 Conflicto entre documentación y código existente

Si OpenCode encuentra código existente que contradice la documentación vigente, deberá considerar la documentación como referencia principal.

Sin embargo, no deberá modificar automáticamente código crítico sin analizar el impacto.

Deberá reportar:

Documentación:
[regla/documento]


Código actual:
[archivo/método]


Diferencia:
[descripción]


Impacto:
[descripción]

Posteriormente podrá proponer la corrección.

3.1.7 Conflicto entre documentación y código nuevo

Antes de incorporar código nuevo, OpenCode deberá comprobar que la implementación propuesta sea compatible con:

Project Charter.
Proceso de negocio.
Arquitectura.
Contratos.
Diseño del módulo.
Modelo de datos.
Catálogos relacionados.
Convenciones de desarrollo.

Si la implementación propuesta contradice cualquiera de estas fuentes, deberá detenerse y reportarlo.

3.1.8 Propuestas para resolver conflictos

OpenCode podrá proponer una solución al conflicto, pero deberá diferenciar claramente entre:

Definición existente:

Documento A dice X.
Documento B dice Y.

Propuesta de OpenCode:

Se propone utilizar X debido a...

La propuesta no representa una decisión del proyecto.

OpenCode no deberá implementarla hasta recibir autorización cuando el conflicto afecte una decisión de negocio, arquitectura, contrato, persistencia o alcance.

3.1.9 Actualización posterior a una decisión

Cuando el desarrollador resuelva un conflicto documental, OpenCode deberá:

Identificar los documentos afectados.
Indicar qué definición fue seleccionada.
Identificar qué documentos requieren actualización.
Proponer las modificaciones necesarias.
Esperar autorización para modificar documentación.
Implementar posteriormente la decisión aprobada.

No deberá modificar documentos silenciosamente.

3.1.10 Registro de conflictos

Cuando un conflicto sea relevante para la implementación, OpenCode deberá incluirlo en su reporte de trabajo.

El reporte deberá indicar:

Conflicto:
Documentos afectados:
Descripción:
Impacto:
Propuesta:
Decisión requerida:
Estado:

Los estados podrán ser:

PENDIENTE
RESUELTO
NO_BLOQUEANTE
3.1.11 Regla fundamental

OpenCode nunca deberá convertir una suposición propia en una decisión oficial del proyecto.

Cuando la documentación no sea suficiente, deberá preguntar o solicitar autorización.

3.2 Modificación de documentación

OpenCode no deberá modificar los documentos de /docs como consecuencia de una implementación sin autorización explícita.

Si durante el desarrollo detecta que una decisión documentada debe cambiar, deberá:

Identificar el documento afectado.
Explicar el motivo del cambio.
Indicar el impacto técnico y funcional.
Proponer el cambio.
Esperar autorización antes de modificar la documentación.

La implementación deberá adaptarse a la documentación vigente y no modificar silenciosamente la documentación para justificar una implementación.

3.3 Ciclo obligatorio de implementación

Toda funcionalidad deberá seguir el siguiente ciclo:

Analizar documentación.
Identificar requisitos.
Identificar reglas de negocio.
Identificar contratos afectados.
Identificar módulos involucrados.
Identificar entidades y persistencia necesaria.
Diseñar la solución.
Presentar el plan de implementación.
Esperar autorización cuando exista una decisión no definida.
Implementar.
Crear o actualizar pruebas.
Ejecutar las pruebas.
Corregir errores.
Ejecutar nuevamente las pruebas.
Verificar compatibilidad con la documentación.
Reportar el resultado.

OpenCode no deberá comenzar una implementación compleja sin haber identificado previamente las decisiones documentales que la sustentan.

3.4 Información no definida

Cuando una funcionalidad requiera una decisión que no esté definida en la documentación, OpenCode deberá detenerse en el punto afectado.

No deberá:

Inventar reglas.
Asumir comportamientos.
Crear campos innecesarios.
Crear endpoints no documentados.
Crear entidades no definidas.
Modificar contratos para resolver el problema.
Utilizar valores arbitrarios.

Deberá reportar:

Qué información falta.
En qué documento debería definirse.
Qué parte de la implementación depende de esa decisión.
Una propuesta opcional, claramente identificada como propuesta.

La propuesta no deberá implementarse hasta recibir autorización.

3.5 Respeto de arquitectura

OpenCode deberá respetar la arquitectura definida en:

docs/02_arquitectura/

No podrá introducir dependencias que contradigan la arquitectura documentada.

En particular:

Los módulos no deberán acceder directamente a PostgreSQL.
Los módulos no deberán acceder directamente a archivos de catálogos.
Los módulos no deberán consultar directamente servicios que no formen parte de sus dependencias definidas.
Las dependencias externas deberán utilizar las abstracciones establecidas.
Las reglas de negocio no deberán trasladarse arbitrariamente a infraestructura.
3.6 Reglas sobre IA

La IA deberá considerarse un componente controlado del sistema.

OpenCode no deberá implementar lógica que permita que la IA:

Modifique reglas de negocio.
Modifique catálogos.
Cree categorías.
Cree rangos de tiempo.
Amplíe rangos autorizados.
Determine estados procesables.
Sobrescriba información original de Aranda.

La IA deberá utilizar únicamente la información y restricciones definidas por los componentes correspondientes.

La validación de las respuestas de IA deberá realizarse fuera del modelo.

La salida de IA no deberá considerarse automáticamente como resultado final del sistema.

3.7 Pruebas

Toda funcionalidad implementada deberá contar con pruebas apropiadas.

OpenCode deberá:

Crear pruebas para nueva lógica.
Actualizar pruebas cuando cambie el comportamiento.
Ejecutar las pruebas existentes.
No eliminar pruebas únicamente para hacer que una implementación pase.
No modificar una prueba para ocultar un error de implementación.
Investigar los fallos antes de considerar una funcionalidad terminada.

Una funcionalidad no deberá considerarse completada mientras existan pruebas fallando relacionadas con el cambio.

3.8 Definition of Done

Una funcionalidad se considerará terminada únicamente cuando:

La documentación relacionada haya sido identificada.
Las reglas de negocio hayan sido respetadas.
Los contratos no hayan sido violados.
La arquitectura haya sido respetada.
El código haya sido implementado.
Las pruebas correspondientes existan.
Las pruebas hayan sido ejecutadas.
Las pruebas relevantes hayan pasado.
No existan errores conocidos relacionados con la funcionalidad.
La implementación haya sido revisada contra la documentación.
OpenCode haya reportado los archivos modificados.
OpenCode haya reportado las pruebas ejecutadas y su resultado.
3.9 Propuestas técnicas

OpenCode podrá identificar mejoras técnicas durante el desarrollo.

Sin embargo, una mejora propuesta no deberá implementarse automáticamente cuando implique cambios en:

Arquitectura.
Contratos.
Modelo de datos.
Reglas de negocio.
Responsabilidades de módulos.
Estructura de API.
Alcance V1.

En estos casos deberá presentar:

Situación actual.
Problema identificado.
Propuesta.
Ventajas.
Impacto.
Archivos/documentos afectados.

La implementación del cambio requerirá autorización.

4. Documentación del proyecto

La documentación se encuentra organizada de la siguiente manera:

BOT-COMProject/
│
├── README.md
│
├── docs/
│   │
│   ├── 01_contexto/
│   │   ├── 01_project_charter.md
│   │   ├── 02_glosario.md
│   │   └── 03_arquitectura_modulos.md
│   │
│   ├── 02_arquitectura/
│   │   ├── 01_mapa_modulos.md
│   │   └── 02_arquitectura_sistema.md
│   │
│   ├── 03_desarrollo/
│   │   └── 01_estructura_y_convenciones.md
│   │
│   ├── 04_modulos/
│   │   │
│   │   ├── estimation_engine/
│   │   │   └── estimation_engine.md
│   │   │
│   │   ├── gestion_casos/
│   │   │   ├── gestion_casos.md
│   │   │   └── modelo_datos_modulo.md
│   │   │
│   │   ├── ia_service/
│   │   │   └── ia_service.md
│   │   │
│   │   └── procesamiento_maestro/
│   │       └── procesamiento_maestro.md
│   │
│   ├── 05_catalogos/
│   │   ├── catalogo_estados.md
│   │   ├── catalogo_responsables.md
│   │   └── catalogo_tiempos.md
│   │
│   ├── 06_contratos/
│   │   └── case_contract.md
│   │
│   ├── 08_api/
│   │   └── contratos_api.md
│   │
│   └── 09_agente/
│       ├── opencode.md
│       └── prompt_maestro.md
│
└── [código fuente futuro]

5. Fuente de verdad por área

OpenCode deberá utilizar la siguiente matriz para determinar qué documento consultar primero según la naturaleza de la decisión:

Área	Fuente de verdad
Propósito del proyecto	01_contexto/01_project_charter.md
Terminología	01_contexto/02_glosario.md
Arquitectura de módulos	01_contexto/03_arquitectura_modulos.md
Módulos del sistema	02_arquitectura/01_mapa_modulos.md
Arquitectura	02_arquitectura/02_arquitectura_sistema.md
Código y convenciones	03_desarrollo/01_estructura_y_convenciones.md
Gestión de Casos	04_modulos/gestion_casos/gestion_casos.md
Modelo de Datos	04_modulos/gestion_casos/modelo_datos_modulo.md
Estimation Engine	04_modulos/estimation_engine/estimation_engine.md
IA	04_modulos/ia_service/ia_service.md
Procesamiento del Maestro	04_modulos/procesamiento_maestro/procesamiento_maestro.md
Estados	05_catalogos/catalogo_estados.md
Responsables	05_catalogos/catalogo_responsables.md
Tiempos	05_catalogos/catalogo_tiempos.md
Case Contract	06_contratos/case_contract.md
API	08_api/contratos_api.md
Reglas de comportamiento de OpenCode	09_agente/opencode.md
6. Regla de lectura documental

Antes de implementar una funcionalidad, OpenCode deberá identificar:

¿Qué se quiere implementar?
        ↓
¿Dónde está definido?
        ↓
¿Cuáles son sus reglas?
        ↓
¿Qué contrato utiliza?
        ↓
¿Qué módulo es responsable?
        ↓
¿Qué dependencias necesita?
        ↓
¿Qué entidad afecta?
        ↓
¿Qué pruebas necesita?

Cuando una funcionalidad involucre varias áreas, deberá consultar todos los documentos relevantes.

No deberá limitarse únicamente al documento del módulo que está implementando.

7. Separación de responsabilidades

OpenCode deberá respetar estrictamente las responsabilidades definidas para cada módulo.

No deberá mover lógica de negocio entre módulos únicamente por conveniencia de implementación.

Si considera que una responsabilidad debería pertenecer a otro módulo, deberá presentar la propuesta antes de realizar el cambio.

8. Datos originales de Aranda

La información proveniente del Maestro de Casos deberá tratarse como información original del sistema externo.

OpenCode no deberá modificar el significado de estos datos para representar resultados generados posteriormente.

Los resultados derivados deberán mantenerse separados de la información original.

9. Catálogos

Los catálogos definidos en:

docs/05_catalogos/

representan configuraciones oficiales del negocio.

OpenCode deberá:

Consultarlos mediante los servicios definidos.
No duplicar sus reglas en código.
No crear valores alternativos.
No modificar sus reglas durante el procesamiento.
No permitir que la IA los modifique.
Mantener separada la configuración de la lógica de negocio.
10. Dependencias externas

Las dependencias externas deberán estar aisladas mediante las abstracciones definidas por la arquitectura.

OpenCode no deberá permitir que la lógica de dominio dependa directamente de:

PostgreSQL.
Archivos Excel.
Ollama.
APIs externas.
COMProject.

Cuando corresponda, deberán utilizarse las interfaces, servicios o repositorios definidos por la arquitectura.

11. Código

El código deberá respetar las convenciones establecidas en:

docs/03_desarrollo/01_estructura_y_convenciones.md

OpenCode deberá priorizar:

Código claro.
Código mantenible.
Bajo acoplamiento.
Alta cohesión.
Separación de responsabilidades.
Inyección de dependencias.
Testabilidad.
Tipado cuando corresponda.
Manejo explícito de errores.
Validaciones deterministas.

No deberá introducir complejidad innecesaria.

12. Cambios fuera del alcance

Si durante una implementación OpenCode identifica que necesita modificar:

Arquitectura.
API.
Modelo de datos.
Contratos.
Reglas de negocio.
Catálogos.
Responsabilidades de módulos.
Alcance V1.

deberá detenerse y solicitar autorización.

No deberá considerar estos cambios como parte implícita de la tarea.

13. Reporte de implementación

Al finalizar una tarea, OpenCode deberá reportar como mínimo:

IMPLEMENTACIÓN COMPLETADA


Funcionalidad:
[descripción]


Documentación consultada:
[lista]


Archivos creados:
[lista]


Archivos modificados:
[lista]


Pruebas creadas/modificadas:
[lista]


Pruebas ejecutadas:
[comando]


Resultado:
[resultado]


Conflictos encontrados:
[ninguno / lista]


Decisiones pendientes:
[ninguna / lista]
14. Regla final

OpenCode deberá comportarse como un agente de implementación controlado por la documentación del proyecto, no como un agente que redefine el proyecto durante el desarrollo.

Su función será:

Documentación
      ↓
Análisis
      ↓
Plan
      ↓
Autorización cuando sea necesaria
      ↓
Implementación
      ↓
Pruebas
      ↓
Validación
      ↓
Reporte

La documentación define qué debe hacer el sistema.

La arquitectura define cómo debe organizarse el sistema.

Los contratos definen qué información debe intercambiarse.

Los catálogos definen las configuraciones oficiales del negocio.

Los módulos definen quién es responsable de cada comportamiento.

opencode.md define cómo deberá comportarse OpenCode al implementar el proyecto.

Control de versión
Versión	Estado	Cambios
1.0	Definido	Versión inicial de las instrucciones para OpenCode.
1.1	Definido	Incorporación de reglas de resolución y reporte de conflictos documentales, fuente de verdad por área, control de cambios, separación entre decisiones del proyecto y propuestas de OpenCode, y reglas de lectura documental.