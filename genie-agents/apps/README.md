# Radar Tributario · Workshop hands-on

Laboratorio en español para construir una experiencia de priorización tributaria
explicable sobre Databricks. Está pensado para una administración tributaria
similar a SUNAT y es **independiente del MVP SIRE**: no replica sus flujos,
interfaces ni alcance.

> Todos los contribuyentes, RUC, declaraciones, comprobantes, montos y acciones
> son sintéticos. Las salidas son señales para revisión humana; nunca prueban
> fraude, evasión ni incumplimiento.

## Qué construye cada participante

1. Capas gobernadas Bronze, Silver, Gold y ops en Unity Catalog.
2. Datos tributarios sintéticos con errores reproducibles.
3. Calidad, cuarentena y recuperación controlada de un RUC sintético.
4. `taxpayer_activity_daily`, `risk_queue`, `current_actions`,
   `data_quality_summary` y la metric view `tax_risk_metrics`.
5. Dos experiencias Genie: baseline sin contexto y enriquecida con
   instrucciones y consultas verificadas.
6. Una App para revisar señales y registrar decisiones humanas.
7. Un dashboard agregado complementario, no una copia de la cola operativa.

## Escalas rápidas

- `S`: ~50 mil comprobantes, para prueba técnica.
- `M`: ~250 mil, recomendado para el workshop.
- `L`: ~1 millón, para compute validado previamente.

## Orden

1. Completar [PREWORK.md](PREWORK.md).
2. Ejecutar `notebooks/00_setup_unity_catalog.py`.
3. Ejecutar `01_ingesta_bronze.py`, `02_calidad_cuarentena_silver.py` y
   `03_gold_semantic_layer.py`.
4. Comparar las dos experiencias de [genie/README.md](genie/README.md).
5. Conectar la App siguiendo `app/README.md` sin modificar su código en este
   rediseño.
6. Registrar una acción y ejecutar `04_validacion_writeback.py`.
7. Crear el dashboard con [dashboard/README.md](dashboard/README.md).

## Contrato de decisión

Las decisiones permitidas son `OPEN_INVESTIGATION`,
`REQUEST_CLARIFICATION` y `DISMISS`. Genie analiza; solo la App escribe en
`ops_<id>.action_tasks`. Toda acción conserva identidad, responsable, notas,
prioridad, contribuyente, puntaje, autor y timestamps.

## Validación local

```bash
python3 scripts/validate_content.py
```
