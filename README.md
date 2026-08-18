# BOT-COMProject

Sistema de automatización para el procesamiento de casos provenientes del Maestro de Casos de Aranda y la generación de estimaciones de tiempo para su posterior registro en COMProject.

---

## 1. Descripción del proyecto

BOT-COMProject tiene como objetivo automatizar el proceso de preparación y estimación de casos provenientes del Maestro de Casos de Aranda.

El sistema recibe un archivo Maestro de Casos, procesa la información, identifica los casos que pueden continuar, aplica las reglas y catálogos definidos por el negocio, utiliza un servicio de IA para generar recomendaciones y finalmente obtiene una estimación de tiempo validada.

El sistema debe mantener trazabilidad completa de:

```text
Archivo cargado
      ↓
Ejecución
      ↓
Caso original
      ↓
Procesamiento
      ↓
Estimación / Rechazo

```
