# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # 03 · Capa Gold y modelo semántico
# MAGIC
# MAGIC **Objetivo:** transformar datos confiables en métricas y decisiones.
# MAGIC
# MAGIC Gold responde preguntas de negocio:
# MAGIC
# MAGIC - ¿Dónde existe riesgo de quiebre de stock?
# MAGIC - ¿Cuánto ingreso está en riesgo?
# MAGIC - ¿Qué acción recomendamos y con qué prioridad?
# MAGIC - ¿Qué decisiones ya tomó el equipo?
# MAGIC
# MAGIC Además publicamos una Unity Catalog Metric View para que Genie y la App
# MAGIC compartan la misma definición de los indicadores.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_retail_equipo_01", "Catálogo")
dbutils.widgets.text("participant_id", "", "Tu identificador")
dbutils.widgets.dropdown("optimize_tables", "true", ["true", "false"], "Optimizar tablas")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
OPTIMIZE_TABLES = dbutils.widgets.get("optimize_tables") == "true"

if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Nombre de catálogo inválido.")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido. Usa solo a-z, 0-9 o _.")

BRONZE_SCHEMA = f"bronze_{PARTICIPANT_ID}"
SILVER_SCHEMA = f"silver_{PARTICIPANT_ID}"
GOLD_SCHEMA = f"gold_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"

spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.sql(f"USE CATALOG `{CATALOG}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Agregado diario de desempeño
# MAGIC
# MAGIC Esta tabla reduce millones de eventos a un grano estable:
# MAGIC **día × sucursal × producto × canal**. Conservamos métricas aditivas
# MAGIC para permitir análisis flexible sin recalcular Bronze.

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE `{CATALOG}`.`{GOLD_SCHEMA}`.`sales_daily`
    USING DELTA
    CLUSTER BY (event_date, region, category)
    COMMENT 'Ventas confiables por día, sucursal, producto y canal'
    AS
    SELECT
      event_date,
      store_id,
      store_name,
      master_region AS region,
      store_format,
      product_id,
      sku,
      product_name,
      category,
      channel,
      SUM(quantity) AS units_sold,
      ROUND(SUM(net_revenue), 2) AS net_revenue,
      ROUND(SUM(net_revenue - estimated_cost), 2) AS gross_margin,
      COUNT(*) AS transaction_lines,
      COUNT_IF(quality_status = 'REPROCESSED_REGION') AS recovered_rows
    FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`sales`
    GROUP BY ALL
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Construir la cola priorizada de decisiones
# MAGIC
# MAGIC Combinamos velocidad de venta reciente, inventario y lead time.
# MAGIC `days_of_cover` estima cuántos días puede operar una combinación
# MAGIC sucursal-producto. La prioridad es una regla explicable, no una caja
# MAGIC negra.

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE `{CATALOG}`.`{GOLD_SCHEMA}`.`decision_queue`
    USING DELTA
    CLUSTER BY (priority, region, category)
    COMMENT 'Alertas priorizadas de reposición para la experiencia de decisiones'
    AS
    WITH demand AS (
      SELECT
        store_id,
        store_name,
        region,
        store_format,
        product_id,
        sku,
        product_name,
        category,
        SUM(units_sold) / 30.0 AS avg_daily_units,
        SUM(net_revenue) / 30.0 AS avg_daily_revenue,
        SUM(gross_margin) / 30.0 AS avg_daily_margin
      FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`sales_daily`
      WHERE event_date >= date_sub(current_date(), 29)
      GROUP BY ALL
    ),
    scored AS (
      SELECT
        sha2(concat_ws('|', CAST(i.store_id AS STRING), CAST(i.product_id AS STRING),
                       CAST(i.snapshot_date AS STRING)), 256) AS alert_id,
        i.snapshot_date,
        i.store_id,
        i.store_name,
        i.region,
        i.store_format,
        i.product_id,
        i.sku,
        i.product_name,
        i.category,
        i.on_hand_units,
        i.in_transit_units,
        i.reorder_point,
        i.lead_time_days,
        ROUND(COALESCE(d.avg_daily_units, 0), 2) AS avg_daily_units,
        ROUND(COALESCE(d.avg_daily_revenue, 0), 2) AS avg_daily_revenue,
        ROUND(
          (i.on_hand_units + i.in_transit_units)
          / GREATEST(COALESCE(d.avg_daily_units, 0), 0.1),
          1
        ) AS days_of_cover,
        GREATEST(
          CAST(CEIL(
            GREATEST(COALESCE(d.avg_daily_units, 0), 0.1)
            * (i.lead_time_days + 7)
            - (i.on_hand_units + i.in_transit_units)
          ) AS INT),
          0
        ) AS recommended_replenishment_units,
        ROUND(
          GREATEST(
            i.lead_time_days -
            (i.on_hand_units + i.in_transit_units)
            / GREATEST(COALESCE(d.avg_daily_units, 0), 0.1),
            0
          ) * COALESCE(d.avg_daily_revenue, 0),
          2
        ) AS revenue_at_risk
      FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`inventory` i
      LEFT JOIN demand d
        ON i.store_id = d.store_id
       AND i.product_id = d.product_id
    )
    SELECT
      *,
      CASE
        WHEN days_of_cover <= lead_time_days * 0.50 AND revenue_at_risk >= 50000
          THEN 'CRITICAL'
        WHEN days_of_cover <= lead_time_days
          THEN 'HIGH'
        WHEN days_of_cover <= lead_time_days + 3
          THEN 'MEDIUM'
        ELSE 'LOW'
      END AS priority,
      CASE
        WHEN days_of_cover <= lead_time_days
          THEN 'APPROVE_REPLENISHMENT'
        WHEN days_of_cover <= lead_time_days + 3
          THEN 'INVESTIGATE'
        ELSE 'MONITOR'
      END AS recommended_action,
      current_timestamp() AS calculated_at
    FROM scored
    WHERE recommended_replenishment_units > 0
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Tabla transaccional de decisiones y tareas
# MAGIC
# MAGIC La App escribirá exclusivamente en esta tabla a través de Databricks
# MAGIC SQL. Cada decisión crea una tarea con responsable, vencimiento y
# MAGIC contexto. Change Data Feed conserva los cambios para auditoría e
# MAGIC integraciones futuras.

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks` (
      action_id STRING NOT NULL COMMENT 'Identificador UUID de la decisión',
      alert_id STRING NOT NULL COMMENT 'Alerta Gold que originó la acción',
      decision_type STRING NOT NULL COMMENT 'APPROVE_REPLENISHMENT, INVESTIGATE o DISMISS',
      status STRING NOT NULL COMMENT 'OPEN, IN_PROGRESS, DONE o CANCELLED',
      assignee STRING NOT NULL COMMENT 'Responsable de ejecutar la tarea',
      notes STRING COMMENT 'Justificación humana de la decisión',
      priority STRING NOT NULL,
      store_id INT NOT NULL,
      store_name STRING NOT NULL,
      product_id INT NOT NULL,
      sku STRING NOT NULL,
      recommended_units INT,
      created_by STRING NOT NULL,
      created_at TIMESTAMP NOT NULL,
      due_at TIMESTAMP,
      updated_at TIMESTAMP NOT NULL
    )
    USING DELTA
    CLUSTER BY (status, priority, created_at)
    COMMENT 'Decisiones y tareas creadas desde Pulso Retail'
    TBLPROPERTIES (
      'delta.enableChangeDataFeed' = 'true',
      'delta.enableRowTracking' = 'true'
    )
    """
)

spark.sql(
    f"""
    CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`current_actions`
    COMMENT 'Decisiones operativas para consulta en Genie'
    AS
    SELECT
      action_id,
      alert_id,
      decision_type,
      status,
      assignee,
      notes,
      priority,
      store_id,
      store_name,
      product_id,
      sku,
      recommended_units,
      created_by,
      created_at,
      due_at,
      updated_at,
      CASE
        WHEN status NOT IN ('DONE', 'CANCELLED') AND due_at < current_timestamp()
          THEN true
        ELSE false
      END AS is_overdue
    FROM `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks`
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Resumen ejecutivo de calidad
# MAGIC
# MAGIC Genie puede explicar no solo el resultado, sino también la confianza de
# MAGIC la información utilizada.

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`data_quality_summary`
    COMMENT 'Resumen de reglas de calidad para usuarios de negocio'
    AS
    SELECT
      rule_id,
      rule_description,
      failed_rows,
      total_rows,
      ROUND(pass_rate * 100, 3) AS pass_rate_pct,
      measured_at
    FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`data_quality_metrics`
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Unity Catalog Metric View
# MAGIC
# MAGIC Una metric view centraliza dimensiones, medidas, descripciones y
# MAGIC formato. Genie y las visualizaciones dejan de inventar definiciones
# MAGIC diferentes para “ingreso”, “margen” o “unidades”.

# COMMAND ----------

metric_view_sql = f"""
CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`retail_performance_metrics`
WITH METRICS
LANGUAGE YAML
COMMENT 'Capa semántica de desempeño comercial para Pulso Retail'
AS $$
version: 1.1
comment: "Métricas certificadas de venta para el workshop Pulso Retail"
source: {CATALOG}.{GOLD_SCHEMA}.sales_daily
fields:
  - name: event_date
    expr: source.event_date
    display_name: Fecha
    comment: "Fecha calendario de la venta"
  - name: region
    expr: source.region
    display_name: Región
    synonyms: ["región", "territorio"]
  - name: store_name
    expr: source.store_name
    display_name: Sucursal
    synonyms: ["tienda", "local"]
  - name: store_format
    expr: source.store_format
    display_name: Formato de sucursal
  - name: category
    expr: source.category
    display_name: Categoría
    synonyms: ["familia"]
  - name: channel
    expr: source.channel
    display_name: Canal
measures:
  - name: net_revenue
    expr: SUM(source.net_revenue)
    display_name: Ingreso neto
    comment: "Venta después de descuentos, expresada en USD"
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: gross_margin
    expr: SUM(source.gross_margin)
    display_name: Margen bruto
    comment: "Ingreso neto menos costo estimado"
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: units_sold
    expr: SUM(source.units_sold)
    display_name: Unidades vendidas
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: transaction_lines
    expr: SUM(source.transaction_lines)
    display_name: Líneas de transacción
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: average_unit_revenue
    expr: SUM(source.net_revenue) / NULLIF(SUM(source.units_sold), 0)
    display_name: Ingreso promedio por unidad
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 0
$$
"""

spark.sql(metric_view_sql)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Optimización opcional
# MAGIC
# MAGIC `OPTIMIZE` compacta archivos pequeños y prepara las tablas para
# MAGIC consultas concurrentes. Es una operación real de mantenimiento; no se
# MAGIC ejecuta únicamente para generar consumo.

# COMMAND ----------

if OPTIMIZE_TABLES:
    for table in (
        f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`sales_events`",
        f"`{CATALOG}`.`{SILVER_SCHEMA}`.`sales`",
        f"`{CATALOG}`.`{GOLD_SCHEMA}`.`sales_daily`",
        f"`{CATALOG}`.`{GOLD_SCHEMA}`.`decision_queue`",
    ):
        print(f"Optimizando {table}")
        spark.sql(f"OPTIMIZE {table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Validar la capa de consumo

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT priority, COUNT(*) AS alerts,
               ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk,
               SUM(recommended_replenishment_units) AS recommended_units
        FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`decision_queue`
        GROUP BY priority
        ORDER BY CASE priority
          WHEN 'CRITICAL' THEN 1
          WHEN 'HIGH' THEN 2
          WHEN 'MEDIUM' THEN 3
          ELSE 4
        END
        """
    )
)

display(
    spark.sql(
        f"""
        SELECT
          region,
          MEASURE(net_revenue) AS net_revenue,
          MEASURE(gross_margin) AS gross_margin,
          MEASURE(units_sold) AS units_sold
        FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`retail_performance_metrics`
        GROUP BY ALL
        ORDER BY net_revenue DESC
        LIMIT 12
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ Cola de decisiones, tabla de write-back, resumen de calidad y metric
# MAGIC view certificada.
# MAGIC
# MAGIC **Siguiente:** configurar Genie con los artefactos de la carpeta
# MAGIC `genie/` y después conectar la Databricks App.