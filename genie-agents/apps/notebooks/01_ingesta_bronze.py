# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Radar Tributario · 01 · Datos sintéticos y Bronze
# MAGIC
# MAGIC Genera contribuyentes, declaraciones y comprobantes tributarios
# MAGIC ficticios. Los errores son deliberados y reproducibles. Ninguna fila
# MAGIC representa una persona, empresa, operación o hallazgo real.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "radar_tributario_workshop", "Catálogo")
dbutils.widgets.text("participant_id", "", "Identificador")

# COMMAND ----------

import re
from pyspark.sql import functions as F

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Catálogo inválido")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido")
BRONZE_SCHEMA = f"bronze_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"
config = spark.table(f"`{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config`").first()
DOCUMENT_ROWS = int(config["expected_documents"])
TAXPAYER_ROWS = max(2_500, DOCUMENT_ROWS // 25)
VOLUME_PATH = f"/Volumes/{CATALOG}/{BRONZE_SCHEMA}/landing"
spark.conf.set("spark.sql.session.timeZone", "America/Lima")

regions = F.array(*[F.lit(x) for x in [
    "Lima", "Arequipa", "La Libertad", "Piura", "Cusco",
    "Junín", "Lambayeque", "Áncash", "Ica", "Loreto",
]])
activities = F.array(*[F.lit(x) for x in [
    "Comercio", "Servicios", "Manufactura", "Construcción", "Transporte",
]])
segments = F.array(F.lit("PRICO"), F.lit("Mediano"), F.lit("Pequeño"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Maestro sintético de contribuyentes
# MAGIC
# MAGIC El RUC válido se construye con once dígitos y dígito verificador. Cada
# MAGIC 997 filas se introduce un RUC con estructura inválida para evaluar DQ.

# COMMAND ----------

base_taxpayers = (
    spark.range(TAXPAYER_ROWS)
    .withColumn("taxpayer_id", F.format_string("TP%08d", F.col("id")))
    .withColumn("ruc10", F.concat(F.lit("20"), F.lpad(F.col("id").cast("string"), 8, "0")))
    .withColumn(
        "check_digit",
        F.pmod(
            11 - F.pmod(
                F.substring("ruc10", 1, 1).cast("int") * 5
                + F.substring("ruc10", 2, 1).cast("int") * 4
                + F.substring("ruc10", 3, 1).cast("int") * 3
                + F.substring("ruc10", 4, 1).cast("int") * 2
                + F.substring("ruc10", 5, 1).cast("int") * 7
                + F.substring("ruc10", 6, 1).cast("int") * 6
                + F.substring("ruc10", 7, 1).cast("int") * 5
                + F.substring("ruc10", 8, 1).cast("int") * 4
                + F.substring("ruc10", 9, 1).cast("int") * 3
                + F.substring("ruc10", 10, 1).cast("int") * 2,
                11,
            ),
            10,
        ),
    )
)

taxpayers = base_taxpayers.select(
    "taxpayer_id",
    F.format_string("Contribuyente Sintético %05d", F.col("id")).alias("taxpayer_name"),
    F.when(F.col("id") % 997 == 0, F.concat(F.lit("X"), F.col("ruc10")))
    .otherwise(F.concat(F.col("ruc10"), F.col("check_digit").cast("string")))
    .alias("ruc"),
    F.element_at(segments, (F.col("id") % 3 + 1).cast("int")).alias("segment"),
    F.element_at(regions, (F.col("id") % 10 + 1).cast("int")).alias("region"),
    F.element_at(activities, (F.col("id") % 5 + 1).cast("int")).alias("economic_activity"),
    F.when(F.col("id") % 113 == 0, "INACTIVE")
    .when(F.col("id") % 89 == 0, "DORMANT")
    .otherwise("ACTIVE")
    .alias("taxpayer_status"),
    F.date_sub(F.current_date(), (F.col("id") % 1800).cast("int")).alias("registration_date"),
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Comprobantes y declaraciones
# MAGIC
# MAGIC Se inyectan duplicados, contribuyentes desconocidos, montos negativos o
# MAGIC imposibles y emisiones de contribuyentes inactivos. Son anomalías de
# MAGIC datos y señales analíticas; nunca prueba de fraude.

# COMMAND ----------

base_docs = (
    spark.range(DOCUMENT_ROWS)
    .withColumn("event_date", F.date_sub(F.current_date(), (F.col("id") % 120).cast("int")))
    .withColumn("doc_key", F.when((F.col("id") > 0) & (F.col("id") % 811 == 0), F.col("id") - 1).otherwise(F.col("id")))
)
tax_documents = (
    base_docs.withColumn(
        "taxable_amount",
        F.when(F.col("id") % 733 == 0, F.lit(-500.0))
        .when(F.col("id") % 887 == 0, F.lit(9_999_999_999.0))
        .otherwise(F.round(F.lit(250.0) + F.pmod(F.col("id") * 37, F.lit(50_000)), 2))
        .cast("decimal(18,2)"),
    )
    .select(
        F.sha2(F.concat_ws("|", F.lit(CATALOG), F.col("doc_key")), 256).alias("document_id"),
        "event_date",
        F.when(F.col("id") % 991 == 0, "TP_UNKNOWN")
        .otherwise(F.format_string("TP%08d", F.col("id") % TAXPAYER_ROWS))
        .alias("taxpayer_id"),
        F.when(F.col("id") % 2 == 0, "INVOICE").otherwise("CREDIT_NOTE").alias("document_type"),
        F.format_string("F%03d-%08d", F.col("id") % 120, F.col("id")).alias("document_number"),
        "taxable_amount",
        F.round(F.col("taxable_amount") * F.lit(0.18), 2).cast("decimal(18,2)").alias("tax_amount"),
        F.when(F.col("id") % 7 == 0, "PURCHASE").otherwise("SALE").alias("flow_type"),
    )
)

filings = (
    spark.range(TAXPAYER_ROWS * 4)
    .withColumn("taxpayer_num", F.pmod(F.col("id"), F.lit(TAXPAYER_ROWS)))
    .withColumn(
        "period_offset",
        F.floor(F.col("id") / F.lit(TAXPAYER_ROWS)).cast("int"),
    )
    .withColumn(
        "event_date",
        F.date_sub(
            F.current_date(),
            F.pmod(
                F.col("taxpayer_num") * 7 + F.col("period_offset") * 11,
                F.lit(30),
            ).cast("int"),
        ),
    )
    .select(
        F.sha2(F.concat_ws("|", F.lit("filing"), F.col("id")), 256).alias("filing_id"),
        "event_date",
        F.format_string("TP%08d", F.col("taxpayer_num")).alias("taxpayer_id"),
        F.date_format(
            F.expr("add_months(trunc(current_date(), 'month'), -period_offset)"),
            "yyyy-MM",
        ).alias("tax_period"),
        F.round(F.lit(10_000.0) + F.pmod(F.col("id") * 101, F.lit(180_000)), 2)
        .cast("decimal(18,2)").alias("declared_sales"),
        F.round(F.lit(1_800.0) + F.pmod(F.col("id") * 43, F.lit(35_000)), 2)
        .cast("decimal(18,2)").alias("assessed_tax"),
        F.round(F.lit(900.0) + F.pmod(F.col("id") * 67, F.lit(42_000)), 2)
        .cast("decimal(18,2)").alias("claimed_tax_credit"),
        F.when(F.col("id") % 29 == 0, 4).when(F.col("id") % 13 == 0, 2).otherwise(0).alias("amendment_count"),
        F.current_timestamp().alias("filed_at"),
    )
)

# COMMAND ----------

for name, frame in {
    "taxpayers": taxpayers,
    "tax_documents": tax_documents,
    "tax_filings": filings,
}.items():
    path = f"{VOLUME_PATH}/{name}/current"
    frame.write.mode("overwrite").format("parquet").save(path)
    (
        spark.read.parquet(path)
        .withColumn("source_file", F.col("_metadata.file_path"))
        .withColumn("ingested_at", F.current_timestamp())
        .write.mode("overwrite").option("overwriteSchema", "true")
        .format("delta").saveAsTable(f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`{name}`")
    )

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT COUNT(*) total_documents,
          COUNT(*) - COUNT(DISTINCT document_id) duplicates,
          COUNT_IF(taxpayer_id = 'TP_UNKNOWN') unknown_taxpayer,
          COUNT_IF(taxable_amount < 0 OR taxable_amount > 100000000) impossible_amount
        FROM `{CATALOG}`.`{BRONZE_SCHEMA}`.`tax_documents`
        """
    )
)