# Databricks notebook source
# MAGIC %md
# MAGIC # Radar Tributario · 99 · Limpieza opcional
# MAGIC
# MAGIC Elimina solo los cuatro schemas del participante. No ejecutar durante
# MAGIC el workshop; la operación borra datos sintéticos, acciones e historial.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "radar_tributario_workshop", "Catálogo")
dbutils.widgets.text("participant_id", "", "Identificador")
dbutils.widgets.text("confirmation", "", "Escribir DELETE")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Catálogo inválido")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido")
if dbutils.widgets.get("confirmation").strip() != "DELETE":
    raise ValueError("Limpieza cancelada: escribe DELETE")

for schema in (
    f"bronze_{PARTICIPANT_ID}",
    f"silver_{PARTICIPANT_ID}",
    f"gold_{PARTICIPANT_ID}",
    f"ops_{PARTICIPANT_ID}",
):
    spark.sql(f"DROP SCHEMA IF EXISTS `{CATALOG}`.`{schema}` CASCADE")
    print(f"Eliminado: {CATALOG}.{schema}")
