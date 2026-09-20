# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # 01 · Ingesta a escala y capa Bronze
# MAGIC
# MAGIC **Objetivo:** simular una fuente empresarial, escribir archivos raw en
# MAGIC un Unity Catalog Volume e ingerirlos como tablas Delta Bronze.
# MAGIC
# MAGIC Los datos representan ventas e inventario de una cadena de retail con
# MAGIC operación regional. Algunos registros contienen errores intencionales.
# MAGIC Bronze no los corrige: conserva fielmente lo recibido para mantener
# MAGIC trazabilidad.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_retail_equipo_01", "Catálogo")

# COMMAND ----------

import re
from pyspark.sql import functions as F

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Nombre de catálogo inválido.")

spark.conf.set("spark.sql.session.timeZone", "UTC")
config = spark.table(f"`{CATALOG}`.`ops`.`workshop_config`").first()
SCALE = config["scale"]
EVENT_ROWS = int(config["expected_events"])
VOLUME_PATH = f"/Volumes/{CATALOG}/bronze/landing"

print(f"Generando {EVENT_ROWS:,} eventos (escala {SCALE})")
print(f"Landing: {VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Dimensión de sucursales
# MAGIC
# MAGIC Creamos 120 sucursales distribuidas en 12 regiones. Esta dimensión
# MAGIC será la referencia maestra para validar región y sucursal.

# COMMAND ----------

REGIONS = [
    "Norte",
    "Noreste",
    "Este",
    "Sureste",
    "Sur",
    "Suroeste",
    "Oeste",
    "Noroeste",
    "Centro",
    "Centro Norte",
    "Centro Sur",
    "Metropolitana",
]

region_array = F.array(*[F.lit(value) for value in REGIONS])

stores = (
    spark.range(1, 121)
    .select(
        F.col("id").cast("int").alias("store_id"),
        F.format_string("Sucursal %03d", F.col("id")).alias("store_name"),
        F.element_at(region_array, (((F.col("id") - 1) % len(REGIONS)) + 1).cast("int")).alias(
            "region"
        ),
        F.when((F.col("id") % 4) == 0, "Hipermercado")
        .when((F.col("id") % 4) == 1, "Express")
        .otherwise("Supermercado")
        .alias("store_format"),
        (150 + (F.col("id") % 40) * 10).cast("int").alias("capacity_units"),
        F.lit(True).alias("is_active"),
    )
)

display(stores.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Catálogo de productos
# MAGIC
# MAGIC Los 400 productos se distribuyen en categorías con precios y margen
# MAGIC determinísticos. Esto hace que todos obtengan el mismo resultado y
# MAGIC facilita comparar las respuestas de Genie.

# COMMAND ----------

CATEGORIES = [
    "Almacén",
    "Bebidas",
    "Lácteos",
    "Limpieza",
    "Cuidado personal",
    "Congelados",
    "Frescos",
    "Mascotas",
]
category_array = F.array(*[F.lit(value) for value in CATEGORIES])

products = (
    spark.range(1, 401)
    .select(
        F.col("id").cast("int").alias("product_id"),
        F.format_string("SKU-%05d", F.col("id")).alias("sku"),
        F.format_string("Producto %03d", F.col("id")).alias("product_name"),
        F.element_at(category_array, (((F.col("id") - 1) % len(CATEGORIES)) + 1).cast("int")).alias(
            "category"
        ),
        F.round(F.lit(650.0) + (F.col("id") % 70) * 125.75, 2)
        .cast("decimal(18,2)")
        .alias("list_price"),
        F.round(F.lit(0.12) + (F.col("id") % 18) / 100.0, 4)
        .cast("decimal(5,4)")
        .alias("target_margin_pct"),
    )
)

display(products.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Generar eventos de venta con problemas intencionales
# MAGIC
# MAGIC Los errores son pequeños pero visibles:
# MAGIC
# MAGIC - Identificador de evento duplicado.
# MAGIC - Sucursal inexistente.
# MAGIC - Producto nulo.
# MAGIC - Cantidad negativa.
# MAGIC - Precio nulo.
# MAGIC - Descuento superior al 100%.
# MAGIC - Región nula.
# MAGIC
# MAGIC Usamos operaciones modulares en lugar de valores aleatorios para que el
# MAGIC experimento sea reproducible y sus métricas puedan evaluarse.

# COMMAND ----------

base_events = (
    spark.range(EVENT_ROWS)
    .withColumn("event_date", F.date_sub(F.current_date(), (F.col("id") % 90).cast("int")))
    .withColumn(
        "event_key",
        F.when(
            (F.col("id") > 0) & ((F.col("id") % 811) == 0),
            F.col("id") - 1,
        ).otherwise(F.col("id")),
    )
    .withColumn(
        "event_ts",
        F.expr(
            "timestampadd(SECOND, CAST(pmod(id * 7919, 86400) AS INT), "
            "CAST(event_date AS TIMESTAMP))"
        ),
    )
)

sales_events = base_events.select(
    F.sha2(
        F.concat_ws("|", F.lit(CATALOG), F.col("event_key").cast("string")),
        256,
    ).alias("event_id"),
    "event_ts",
    "event_date",
    F.when((F.col("id") % 997) == 0, F.lit(9999))
    .otherwise(((F.col("id") % 120) + 1).cast("int"))
    .alias("store_id"),
    F.when((F.col("id") % 503) == 0, F.lit(None).cast("int"))
    .otherwise(((F.col("id") * 7 % 400) + 1).cast("int"))
    .alias("product_id"),
    F.when((F.col("id") % 389) == 0, F.lit(-2))
    .otherwise(((F.col("id") % 6) + 1).cast("int"))
    .alias("quantity"),
    F.when((F.col("id") % 701) == 0, F.lit(None).cast("decimal(18,2)"))
    .otherwise(F.round(F.lit(650.0) + (F.col("id") * 7 % 70) * 125.75, 2))
    .cast("decimal(18,2)")
    .alias("unit_price"),
    F.when((F.col("id") % 887) == 0, F.lit(1.35))
    .otherwise(F.round((F.col("id") % 18) / 100.0, 4))
    .cast("decimal(5,4)")
    .alias("discount_pct"),
    F.when((F.col("id") % 3) == 0, "ONLINE")
    .when((F.col("id") % 3) == 1, "STORE")
    .otherwise("PICKUP")
    .alias("channel"),
    F.when((F.col("id") % 613) == 0, F.lit(None).cast("string"))
    .otherwise(
        F.element_at(region_array, ((F.col("id") % len(REGIONS)) + 1).cast("int"))
    )
    .alias("reported_region"),
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Generar snapshot de inventario
# MAGIC
# MAGIC Un registro por combinación sucursal-producto. El inventario bajo,
# MAGIC combinado con velocidad de ventas y lead time, permitirá construir la
# MAGIC cola de decisiones de la App.

# COMMAND ----------

inventory = (
    stores.select("store_id")
    .crossJoin(products.select("product_id"))
    .withColumn("snapshot_date", F.current_date())
    .withColumn(
        "on_hand_units",
        F.when(
            ((F.col("store_id") * 401 + F.col("product_id")) % 541) == 0, -5
        )
        .otherwise(
            (
                (F.col("store_id") * 17 + F.col("product_id") * 13) % 180
            ).cast("int")
        ),
    )
    .withColumn(
        "in_transit_units",
        ((F.col("store_id") + F.col("product_id")) % 40).cast("int"),
    )
    .withColumn(
        "reorder_point",
        (20 + (F.col("product_id") % 45)).cast("int"),
    )
    .withColumn(
        "lead_time_days",
        (1 + (F.col("store_id") + F.col("product_id")) % 14).cast("int"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Escribir archivos raw en el Volume
# MAGIC
# MAGIC Esta escritura materializa físicamente los datos y produce trabajo
# MAGIC distribuido real. `overwrite` hace la notebook repetible sin acumular
# MAGIC archivos de ejecuciones anteriores.

# COMMAND ----------

try:
    parallelism = max(8, min(128, int(spark.conf.get('spark.default.parallelism')) * 2))
except Exception:
    parallelism = 8

(
    stores.coalesce(1)
    .write.mode("overwrite")
    .format("parquet")
    .save(f"{VOLUME_PATH}/stores/current")
)
(
    products.coalesce(1)
    .write.mode("overwrite")
    .format("parquet")
    .save(f"{VOLUME_PATH}/products/current")
)
(
    inventory.repartition(parallelism, "store_id")
    .write.mode("overwrite")
    .format("parquet")
    .save(f"{VOLUME_PATH}/inventory/current")
)
(
    sales_events.repartition(parallelism, "event_date")
    .write.mode("overwrite")
    .partitionBy("event_date")
    .format("parquet")
    .save(f"{VOLUME_PATH}/sales_events/current")
)

print("Archivos raw generados.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Ingestar Bronze
# MAGIC
# MAGIC Agregamos metadatos técnicos (`source_file` e `ingested_at`) sin alterar
# MAGIC el contenido de negocio. Bronze sirve como evidencia inmutable de lo
# MAGIC recibido y punto de partida para reejecutar reglas de calidad.

# COMMAND ----------

raw_stores = spark.read.parquet(f"{VOLUME_PATH}/stores/current")
raw_products = spark.read.parquet(f"{VOLUME_PATH}/products/current")
raw_inventory = spark.read.parquet(f"{VOLUME_PATH}/inventory/current")
raw_sales = spark.read.parquet(f"{VOLUME_PATH}/sales_events/current")

for name, frame in {
    "stores": raw_stores,
    "products": raw_products,
    "inventory_snapshot": raw_inventory,
    "sales_events": raw_sales,
}.items():
    (
        frame.withColumn("source_file", F.col("_metadata.file_path"))
        .withColumn("ingested_at", F.current_timestamp())
        .write.mode("overwrite")
        .option("overwriteSchema", "true")
        .format("delta")
        .saveAsTable(f"`{CATALOG}`.`bronze`.`{name}`")
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Validar volumen y errores presentes
# MAGIC
# MAGIC Todavía no corregimos ni descartamos nada. Las métricas confirman que
# MAGIC Bronze contiene tanto eventos válidos como errores conocidos.

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT
          COUNT(*) AS total_events,
          COUNT(*) - COUNT(DISTINCT event_id) AS duplicate_event_ids,
          COUNT_IF(store_id = 9999) AS invalid_store,
          COUNT_IF(product_id IS NULL) AS null_product,
          COUNT_IF(quantity <= 0) AS invalid_quantity,
          COUNT_IF(unit_price IS NULL OR unit_price <= 0) AS invalid_price,
          COUNT_IF(discount_pct < 0 OR discount_pct > 0.80) AS invalid_discount,
          COUNT_IF(reported_region IS NULL) AS null_region
        FROM `{CATALOG}`.`bronze`.`sales_events`
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ Archivos raw en el Volume y cuatro tablas Delta Bronze.
# MAGIC
# MAGIC **Siguiente:** `02_calidad_cuarentena_silver` aplicará reglas, separará
# MAGIC errores y mostrará cómo reingresar registros corregibles.