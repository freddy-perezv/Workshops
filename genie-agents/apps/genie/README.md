# Laboratorio 1 · Construir el Genie Agent

Tiempo objetivo: **35–40 minutos**.

## Resultado

Un Genie Space que:

- Comprende la terminología de Pulso Retail.
- Usa métricas certificadas y tablas Gold.
- Explica calidad y trazabilidad.
- Distingue recomendación analítica de decisión humana.
- Responde un conjunto de preguntas benchmark.

## 1. Crear el Space

En AI/BI Genie, crea un Space:

- **Nombre:** `Pulso Retail · <equipo>`
- **Descripción:** `Copiloto para priorizar riesgo de inventario y dar seguimiento a decisiones de una operación regional.`
- **SQL warehouse:** el warehouse validado en el prework.

## 2. Agregar datos

Reemplaza `<catalog>` por el catálogo compartido y `<id>` por el mismo
`participant_id` utilizado en las notebooks. Agrega:

1. `<catalog>.gold_<id>.retail_performance_metrics`
2. `<catalog>.gold_<id>.decision_queue`
3. `<catalog>.gold_<id>.current_actions`
4. `<catalog>.gold_<id>.data_quality_summary`
5. `<catalog>.gold_<id>.sales_daily`

La metric view debe ser la fuente principal para desempeño comercial.
`sales_daily` se incluye para preguntas que necesiten detalle no expuesto por la
metric view.

## 3. Configurar instrucciones

Copia el contenido de [`instructions.md`](instructions.md) en las instrucciones
del Space. Revisa con los participantes:

- Definiciones de negocio.
- Elección de fuente.
- Límites: Genie recomienda; la App registra la decisión.
- Forma de comunicar incertidumbre y calidad.

## 4. Agregar sample questions

Agrega al menos estas preguntas visibles:

1. ¿Qué regiones tienen mayor ingreso neto en los últimos 30 días?
2. ¿Dónde está concentrado el ingreso en riesgo por quiebre de stock?
3. Muéstrame las alertas críticas con más de USD 50,000 en riesgo.
4. ¿Qué categorías tienen peor tasa de calidad?
5. ¿Qué decisiones se tomaron hoy y quién es responsable?
6. ¿Qué tareas están vencidas?

## 5. Agregar consultas verificadas

Usa [`verified-queries.sql`](verified-queries.sql). Cada bloque contiene la
pregunta y el SQL de referencia. Reemplaza `<catalog>` y `<gold_schema>` (por
ejemplo, `gold_freddy`) antes de copiarlo.

No es necesario registrar todos los bloques durante la sesión: agrega cuatro
como mínimo y deja el resto como material de continuidad.

## 6. Comparar “antes” y “después”

Antes de agregar instrucciones y SQL verificado, pregunta:

> ¿Cuáles son las cinco alertas más importantes y por qué?

Guarda la respuesta. Repite la misma pregunta después de la configuración.
Compara:

- Fuente elegida.
- Definición de “importante”.
- Presencia de ingreso en riesgo y cobertura.
- Recomendación con evidencia.

## 7. Evaluar

Ejecuta las preguntas de [`evaluation-questions.csv`](evaluation-questions.csv).
Registra para cada una:

- `PASS`: correcta y sustentada.
- `PARTIAL`: correcta pero incompleta.
- `FAIL`: fuente, métrica o conclusión incorrecta.

El objetivo del workshop es **80% PASS/PARTIAL y cero errores críticos** en
permisos, moneda o granularidad.

## 8. Conectar con la App

Copia el ID del Genie Space. Se utilizará como recurso `genie-space` de la
Databricks App y se expondrá en `DATABRICKS_GENIE_SPACE_ID`, sin hardcodearlo.

La App utilizará el componente `GenieChat` de AppKit con alias `pulso-retail`.
