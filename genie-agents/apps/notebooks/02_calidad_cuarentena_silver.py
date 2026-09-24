# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Radar Tributario · 02 · Calidad, cuarentena y Silver
# MAGIC
# MAGIC Las reglas hacen visibles RUC inválidos, contribuyentes desconocidos,
# MAGIC duplicados y montos negativos/imposibles. Solo se recupera un problema
# MAGIC seguro: reconstruir el RUC sintético desde el identificador generado.

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
SILVER_SCHEMA = f"silver_{PARTICIPANT_ID}"
spark.conf.set("spark.sql.session.timeZone", "America/Lima")

taxpayers = spark.table(f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`taxpayers`")
documents = spark.table(f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`tax_documents`")
filings = spark.table(f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`tax_filings`")

# COMMAND ----------

def ruc_check_expr(column_name: str):
    r = F.col(column_name)
    weighted = sum(
        F.substring(r, i + 1, 1).cast("int") * weight
        for i, weight in enumerate([5, 4, 3, 2, 7, 6, 5, 4, 3, 2])
    )
    return F.pmod(11 - F.pmod(weighted, 11), 10)

evaluated_taxpayers = (
    taxpayers.withColumn(
        "valid_ruc",
        F.col("ruc").rlike(r"^\d{11}$")
        & (F.substring("ruc", 11, 1).cast("int") == ruc_check_expr("ruc")),
    )
    .withColumn(
        "dq_reasons",
        F.when(~F.col("valid_ruc"), F.array(F.lit("DQ001_INVALID_RUC")))
        .otherwise(F.expr("CAST(array() AS ARRAY<STRING>)")),
    )
)

# La recuperación es segura solo porque taxpayer_id y RUC son sintéticos y
# determinísticos dentro del workshop.
recoverable = (
    evaluated_taxpayers.filter(~F.col("valid_ruc"))
    .withColumn("ruc10", F.concat(F.lit("20"), F.substring("taxpayer_id", 3, 8)))
    .withColumn("ruc", F.concat("ruc10", ruc_check_expr("ruc10").cast("string")))
    .drop("ruc10", "valid_ruc", "dq_reasons")
    .withColumn("quality_status", F.lit("REPROCESSED_SYNTHETIC_RUC"))
)
valid_taxpayers = (
    evaluated_taxpayers.filter("valid_ruc")
    .drop("valid_ruc", "dq_reasons")
    .withColumn("quality_status", F.lit("ORIGINAL_VALID"))
)
silver_taxpayers = valid_taxpayers.unionByName(recoverable)
quarantine_taxpayers = (
    evaluated_taxpayers.filter(~F.col("valid_ruc"))
    .withColumn("resolution_status", F.lit("REPROCESSED"))
    .withColumn("resolution_note", F.lit("RUC sintético reconstruido desde taxpayer_id"))
    .withColumn("quarantined_at", F.current_timestamp())
)

# COMMAND ----------

duplicate_ids = (
    documents.groupBy("document_id").count().filter("count > 1")
    .select("document_id").withColumn("is_duplicate", F.lit(True))
)
evaluated_documents = (
    documents.join(duplicate_ids, "document_id", "left")
    .join(
        silver_taxpayers.select("taxpayer_id", "taxpayer_name", "ruc", "segment",
                                "region", "economic_activity", "taxpayer_status"),
        "taxpayer_id",
        "left",
    )
    .withColumn(
        "dq_reasons",
        F.filter(
            F.array(
                F.when(F.col("taxpayer_name").isNull(), "DQ002_UNKNOWN_TAXPAYER"),
                F.when(F.coalesce("is_duplicate", F.lit(False)), "DQ003_DUPLICATE_DOCUMENT"),
                F.when(F.col("taxable_amount") < 0, "DQ004_NEGATIVE_AMOUNT"),
                F.when(F.col("taxable_amount") > 100_000_000, "DQ005_IMPOSSIBLE_AMOUNT"),
                F.when(F.col("tax_amount") < 0, "DQ006_NEGATIVE_TAX"),
            ),
            lambda x: x.isNotNull(),
        ),
    )
)
silver_documents = evaluated_documents.filter(F.size("dq_reasons") == 0).drop(
    "dq_reasons", "is_duplicate"
)
quarantine_documents = (
    evaluated_documents.filter(F.size("dq_reasons") > 0)
    .withColumn("resolution_status", F.lit("PENDING"))
    .withColumn("quarantined_at", F.current_timestamp())
)

silver_filings = (
    filings.join(
        silver_taxpayers.select("taxpayer_id", "taxpayer_name", "ruc", "segment",
                                "region", "economic_activity", "taxpayer_status"),
        "taxpayer_id",
        "inner",
    )
    .filter(
        (F.col("declared_sales") >= 0)
        & (F.col("assessed_tax") >= 0)
        & (F.col("claimed_tax_credit") >= 0)
    )
)

# COMMAND ----------

for table_name, frame in {
    "taxpayers": silver_taxpayers,
    "tax_documents": silver_documents,
    "tax_filings": silver_filings,
    "quarantine_taxpayers": quarantine_taxpayers,
    "quarantine_documents": quarantine_documents,
}.items():
    (
        frame.write.mode("overwrite").option("overwriteSchema", "true")
        .format("delta").saveAsTable(f"`{CATALOG}`.`{SILVER_SCHEMA}`.`{table_name}`")
    )

rule_dictionary = spark.createDataFrame(
    [
        ("DQ001_INVALID_RUC", "RUC con longitud, caracteres o dígito verificador inválido"),
        ("DQ002_UNKNOWN_TAXPAYER", "Comprobante asociado a contribuyente desconocido"),
        ("DQ003_DUPLICATE_DOCUMENT", "Identificador de comprobante duplicado"),
        ("DQ004_NEGATIVE_AMOUNT", "Monto imponible negativo"),
        ("DQ005_IMPOSSIBLE_AMOUNT", "Monto imponible sobre umbral plausible del laboratorio"),
        ("DQ006_NEGATIVE_TAX", "Impuesto negativo"),
    ],
    ["rule_id", "rule_description"],
)
failures = (
    evaluated_taxpayers.select(F.explode("dq_reasons").alias("rule_id"))
    .unionByName(evaluated_documents.select(F.explode("dq_reasons").alias("rule_id")))
    .groupBy("rule_id").count().withColumnRenamed("count", "failed_rows")
)
total_rows = taxpayers.count() + documents.count()
dq_metrics = (
    rule_dictionary.join(failures, "rule_id", "left").fillna(0, ["failed_rows"])
    .withColumn("total_rows", F.lit(total_rows))
    .withColumn("pass_rate", F.round(1 - F.col("failed_rows") / F.col("total_rows"), 6))
    .withColumn("measured_at", F.current_timestamp())
)
dq_metrics.write.mode("overwrite").option("overwriteSchema", "true").format("delta").saveAsTable(
    f"`{CATALOG}`.`{SILVER_SCHEMA}`.`data_quality_metrics`"
)

# COMMAND ----------

display(dq_metrics.orderBy(F.desc("failed_rows")))