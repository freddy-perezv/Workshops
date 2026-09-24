# Databricks notebook source
# MAGIC %md
# MAGIC # Radar Tributario · 00 · Preparación gobernada
# MAGIC
# MAGIC Crea un entorno aislado Bronze/Silver/Gold/ops. Este laboratorio es
# MAGIC independiente del MVP SIRE: usa exclusivamente datos sintéticos y no
# MAGIC reproduce expedientes, contribuyentes ni decisiones reales.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "radar_tributario_workshop", "01. Catálogo")
dbutils.widgets.text("participant_id", "", "02. Identificador")
dbutils.widgets.dropdown("scale", "M", ["S", "M", "L"], "03. Escala")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
SCALE = dbutils.widgets.get("scale")
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("catalog_name inválido")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("participant_id inválido")

BRONZE_SCHEMA = f"bronze_{PARTICIPANT_ID}"
SILVER_SCHEMA = f"silver_{PARTICIPANT_ID}"
GOLD_SCHEMA = f"gold_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"
SCALE_ROWS = {"S": 50_000, "M": 250_000, "L": 1_000_000}
DOCUMENT_ROWS = SCALE_ROWS[SCALE]
spark.conf.set("spark.sql.session.timeZone", "America/Lima")

# COMMAND ----------

# MAGIC %md
# MAGIC El catálogo debe existir y haber sido asignado por el instructor. Las
# MAGIC operaciones siguientes son idempotentes.

# COMMAND ----------

spark.sql(f"USE CATALOG `{CATALOG}`")
for schema in (BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA, OPS_SCHEMA):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`{schema}`")

spark.sql(
    f"""CREATE VOLUME IF NOT EXISTS `{CATALOG}`.`{BRONZE_SCHEMA}`.`landing`
    COMMENT 'Landing sintético de Radar Tributario'"""
)
VOLUME_PATH = f"/Volumes/{CATALOG}/{BRONZE_SCHEMA}/landing"
for folder in ("taxpayers", "tax_documents", "tax_filings"):
    dbutils.fs.mkdirs(f"{VOLUME_PATH}/{folder}")

spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config` (
      catalog_name STRING NOT NULL, participant_id STRING NOT NULL,
      scale STRING NOT NULL, expected_documents BIGINT NOT NULL,
      initialized_by STRING NOT NULL, initialized_at TIMESTAMP NOT NULL
    ) USING DELTA
    """
)
spark.sql(f"DELETE FROM `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config`")
spark.sql(
    f"""
    INSERT INTO `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config`
    VALUES ('{CATALOG}', '{PARTICIPANT_ID}', '{SCALE}', {DOCUMENT_ROWS},
            current_user(), current_timestamp())
    """
)

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT schema_name FROM `{CATALOG}`.information_schema.schemata
        WHERE schema_name IN ('{BRONZE_SCHEMA}', '{SILVER_SCHEMA}',
                              '{GOLD_SCHEMA}', '{OPS_SCHEMA}')
        ORDER BY schema_name
        """
    )
)
print(f"Radar Tributario listo: escala {SCALE}, {DOCUMENT_ROWS:,} documentos")
