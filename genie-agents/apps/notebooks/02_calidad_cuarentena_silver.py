# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # 02 · Data Quality, cuarentena y capa Silver
# MAGIC
# MAGIC **Objetivo:** convertir datos raw en información confiable sin ocultar
# MAGIC los errores.
# MAGIC
# MAGIC Cada fila se evalúa contra reglas explícitas. Las filas válidas pasan a
# MAGIC Silver; las demás quedan en cuarentena con sus causas. Después
# MAGIC corregimos un caso recuperable y lo reingresamos de forma auditable.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_retail_equipo_01", "Catálogo")

# COMMAND ----------

import re
from pyspark.sql import functions as F

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Nombre de catálogo inválido.")

spark.conf.set("spark.sql.session.timeZone", "UTC")
sales = spark.table(f"`{CATALOG}`.`bronze`.`sales_events`").alias("s")
stores = spark.table(f"`{CATALOG}`.`bronze`.`stores`").alias("st")
products = spark.table(f"`{CATALOG}`.`bronze`.`products`").alias("p")
inventory = spark.table(f"`{CATALOG}`.`bronze`.`inventory_snapshot`").alias("i")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Definir reglas de calidad
# MAGIC
# MAGIC Las reglas tienen identificadores estables. Así podemos medirlas,
# MAGIC explicarlas al negocio y utilizarlas como evidencia durante una
# MAGIC auditoría.

# COMMAND ----------

duplicate_ids = (
    spark.table(f"`{CATALOG}`.`bronze`.`sales_events`")
    .groupBy("event_id")
    .count()
    .filter(F.col("count") > 1)
    .select(F.col("event_id").alias("duplicate_event_id"))
    .withColumn("is_duplicate", F.lit(True))
)

joined_sales = sales.join(
    stores.select(
        F.col("store_id").alias("master_store_id"),
        F.col("store_name"),
        F.col("region").alias("master_region"),
        F.col("store_format"),
    ),
    F.col("s.store_id") == F.col("master_store_id"),
    "left",
).join(
    products.select(
        F.col("product_id").alias("master_product_id"),
        F.col("sku"),
        F.col("product_name"),
        F.col("category"),
        F.col("target_margin_pct"),
    ),
    F.col("s.product_id") == F.col("master_product_id"),
    "left",
).join(
    duplicate_ids,
    F.col("s.event_id") == F.col("duplicate_event_id"),
    "left",
)

rule_results = [
    F.when(F.col("event_id").isNull(), "DQ001_EVENT_ID_MISSING"),
    F.when(F.col("is_duplicate"), "DQ009_EVENT_ID_DUPLICATED"),
    F.when(F.col("master_store_id").isNull(), "DQ002_STORE_UNKNOWN"),
    F.when(F.col("master_product_id").isNull(), "DQ003_PRODUCT_UNKNOWN"),
    F.when(
        F.col("quantity").isNull()
        | (F.col("quantity") <= 0)
        | (F.col("quantity") > 100),
        "DQ004_QUANTITY_OUT_OF_RANGE",
    ),
    F.when(
        F.col("unit_price").isNull() | (F.col("unit_price") <= 0),
        "DQ005_PRICE_INVALID",
    ),
    F.when(
        F.col("discount_pct").isNull()
        | (F.col("discount_pct") < 0)
        | (F.col("discount_pct") > 0.80),
        "DQ006_DISCOUNT_INVALID",
    ),
    F.when(F.col("reported_region").isNull(), "DQ007_REGION_MISSING"),
    F.when(
        F.col("reported_region").isNotNull()
        & F.col("master_region").isNotNull()
        & (F.col("reported_region") != F.col("master_region")),
        "DQ008_REGION_MISMATCH",
    ),
]

evaluated_sales = joined_sales.withColumn(
    "dq_reasons",
    F.filter(F.array(*rule_results), lambda reason: reason.isNotNull()),
).withColumn("dq_passed", F.size("dq_reasons") == 0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Separar válidos y cuarentena
# MAGIC
# MAGIC Cuarentena no significa “borrar”. Conservamos la fila, sus metadatos,
# MAGIC las reglas incumplidas y el estado de resolución.

# COMMAND ----------

valid_sales = evaluated_sales.filter("dq_passed").select(
    "event_id",
    "event_ts",
    "event_date",
    F.col("s.store_id").alias("store_id"),
    "store_name",
    "master_region",
    "store_format",
    F.col("s.product_id").alias("product_id"),
    "sku",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "discount_pct",
    "channel",
    F.round(
        F.col("quantity") * F.col("unit_price") * (1 - F.col("discount_pct")), 2
    )
    .cast("decimal(20,2)")
    .alias("net_revenue"),
    F.round(
        F.col("quantity")
        * F.col("unit_price")
        * (1 - F.col("target_margin_pct")),
        2,
    )
    .cast("decimal(20,2)")
    .alias("estimated_cost"),
    F.lit("ORIGINAL_VALID").alias("quality_status"),
    "source_file",
    "ingested_at",
)

quarantine_sales = (
    evaluated_sales.filter("NOT dq_passed")
    .select(
        "event_id",
        "event_ts",
        "event_date",
        F.col("s.store_id").alias("store_id"),
        F.col("s.product_id").alias("product_id"),
        "quantity",
        "unit_price",
        "discount_pct",
        "channel",
        "reported_region",
        "master_region",
        "dq_reasons",
        "source_file",
        "ingested_at",
    )
    .withColumn("quarantined_at", F.current_timestamp())
    .withColumn("resolution_status", F.lit("PENDING"))
    .withColumn("resolution_note", F.lit(None).cast("string"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Reprocesar un error recuperable
# MAGIC
# MAGIC Una región ausente puede completarse desde la dimensión maestra si
# MAGIC la sucursal es válida y no existe otro error. No “arreglamos” precios,
# MAGIC productos o cantidades sin una decisión de negocio.

# COMMAND ----------

recoverable = evaluated_sales.filter(
    (F.size("dq_reasons") == 1)
    & (F.array_contains("dq_reasons", "DQ007_REGION_MISSING"))
)

recovered_sales = recoverable.select(
    "event_id",
    "event_ts",
    "event_date",
    F.col("s.store_id").alias("store_id"),
    "store_name",
    "master_region",
    "store_format",
    F.col("s.product_id").alias("product_id"),
    "sku",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "discount_pct",
    "channel",
    F.round(
        F.col("quantity") * F.col("unit_price") * (1 - F.col("discount_pct")), 2
    )
    .cast("decimal(20,2)")
    .alias("net_revenue"),
    F.round(
        F.col("quantity")
        * F.col("unit_price")
        * (1 - F.col("target_margin_pct")),
        2,
    )
    .cast("decimal(20,2)")
    .alias("estimated_cost"),
    F.lit("REPROCESSED_REGION").alias("quality_status"),
    "source_file",
    "ingested_at",
)

silver_sales = valid_sales.unionByName(recovered_sales)

resolved_ids = recoverable.select("event_id").withColumn(
    "resolved", F.lit(True)
)
quarantine_sales = (
    quarantine_sales.join(resolved_ids, "event_id", "left")
    .withColumn(
        "resolution_status",
        F.when(F.col("resolved"), "REPROCESSED").otherwise("PENDING"),
    )
    .withColumn(
        "resolution_note",
        F.when(
            F.col("resolved"),
            "Región completada desde la dimensión maestra de sucursales",
        ),
    )
    .drop("resolved")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validar inventario
# MAGIC
# MAGIC El inventario negativo no se corrige automáticamente porque podría
# MAGIC representar un problema físico o de integración. Se conserva en una
# MAGIC cuarentena separada.

# COMMAND ----------

evaluated_inventory = (
    inventory.join(
        stores.select("store_id", "store_name", "region", "store_format"),
        "store_id",
        "left",
    )
    .join(products.select("product_id", "sku", "product_name", "category"), "product_id")
    .withColumn(
        "dq_reasons",
        F.filter(
            F.array(
                F.when(F.col("store_name").isNull(), "DQ101_STORE_UNKNOWN"),
                F.when(F.col("sku").isNull(), "DQ102_PRODUCT_UNKNOWN"),
                F.when(F.col("on_hand_units") < 0, "DQ103_NEGATIVE_ON_HAND"),
                F.when(F.col("reorder_point") <= 0, "DQ104_REORDER_POINT_INVALID"),
                F.when(
                    ~F.col("lead_time_days").between(1, 60),
                    "DQ105_LEAD_TIME_INVALID",
                ),
            ),
            lambda reason: reason.isNotNull(),
        ),
    )
)

silver_inventory = evaluated_inventory.filter(F.size("dq_reasons") == 0).drop(
    "dq_reasons"
)
quarantine_inventory = (
    evaluated_inventory.filter(F.size("dq_reasons") > 0)
    .withColumn("quarantined_at", F.current_timestamp())
    .withColumn("resolution_status", F.lit("PENDING"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Materializar tablas Delta Silver y cuarentena

# COMMAND ----------

for table_name, frame in {
    "sales": silver_sales,
    "inventory": silver_inventory,
    "quarantine_sales": quarantine_sales,
    "quarantine_inventory": quarantine_inventory,
}.items():
    (
        frame.write.mode("overwrite")
        .option("overwriteSchema", "true")
        .format("delta")
        .saveAsTable(f"`{CATALOG}`.`silver`.`{table_name}`")
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Publicar métricas de calidad
# MAGIC
# MAGIC Una métrica agregada permite monitorear tendencia y establecer un
# MAGIC contrato: el pipeline no solo produce datos, también demuestra su
# MAGIC nivel de confianza.

# COMMAND ----------

rule_dictionary = spark.createDataFrame(
    [
        ("DQ001_EVENT_ID_MISSING", "Evento sin identificador"),
        ("DQ002_STORE_UNKNOWN", "Sucursal inexistente"),
        ("DQ003_PRODUCT_UNKNOWN", "Producto inexistente o nulo"),
        ("DQ004_QUANTITY_OUT_OF_RANGE", "Cantidad fuera de rango"),
        ("DQ005_PRICE_INVALID", "Precio nulo o no positivo"),
        ("DQ006_DISCOUNT_INVALID", "Descuento fuera de política"),
        ("DQ007_REGION_MISSING", "Región ausente"),
        ("DQ008_REGION_MISMATCH", "Región no coincide con sucursal"),
        ("DQ009_EVENT_ID_DUPLICATED", "Identificador de evento duplicado"),
    ],
    ["rule_id", "rule_description"],
)

failed_by_rule = (
    evaluated_sales.select(F.explode("dq_reasons").alias("rule_id"))
    .groupBy("rule_id")
    .agg(F.count("*").alias("failed_rows"))
)
total_rows = evaluated_sales.count()

dq_metrics = (
    rule_dictionary.join(failed_by_rule, "rule_id", "left")
    .fillna(0, subset=["failed_rows"])
    .withColumn("total_rows", F.lit(total_rows))
    .withColumn(
        "pass_rate",
        F.round((F.col("total_rows") - F.col("failed_rows")) / F.col("total_rows"), 6),
    )
    .withColumn("measured_at", F.current_timestamp())
)

(
    dq_metrics.write.mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable(f"`{CATALOG}`.`silver`.`data_quality_metrics`")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Validar el resultado
# MAGIC
# MAGIC Observa tres cantidades: Bronze, Silver y cuarentena. Silver incluye
# MAGIC filas originalmente válidas más regiones recuperadas. La suma no debe
# MAGIC hacerse directamente porque los registros reprocesados permanecen en
# MAGIC cuarentena como evidencia histórica.

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT 'bronze' AS layer, COUNT(*) AS rows
        FROM `{CATALOG}`.`bronze`.`sales_events`
        UNION ALL
        SELECT 'silver', COUNT(*) FROM `{CATALOG}`.`silver`.`sales`
        UNION ALL
        SELECT 'quarantine_pending', COUNT(*)
        FROM `{CATALOG}`.`silver`.`quarantine_sales`
        WHERE resolution_status = 'PENDING'
        UNION ALL
        SELECT 'quarantine_reprocessed', COUNT(*)
        FROM `{CATALOG}`.`silver`.`quarantine_sales`
        WHERE resolution_status = 'REPROCESSED'
        """
    )
)

display(
    spark.table(f"`{CATALOG}`.`silver`.`data_quality_metrics`").orderBy(
        "rule_id"
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ Silver confiable, cuarentena auditable, reproceso controlado y
# MAGIC métricas de calidad.
# MAGIC
# MAGIC **Siguiente:** `03_gold_semantic_layer` convertirá estos datos en
# MAGIC decisiones, KPIs y semántica de negocio para Genie.