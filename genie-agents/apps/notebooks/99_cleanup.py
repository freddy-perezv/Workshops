# Databricks notebook source
# MAGIC %md
# MAGIC # 99 · Limpieza opcional
# MAGIC
# MAGIC Esta notebook elimina únicamente los cuatro schemas del participante,
# MAGIC incluyendo tablas, views, volume, decisiones e historial. No elimina el
# MAGIC catálogo compartido ni los datos de otros participantes.
# MAGIC
# MAGIC No debe ejecutarse durante el workshop. Úsala únicamente cuando el
# MAGIC equipo confirme que ya no necesita los resultados.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_retail_equipo_01", "Catálogo")
dbutils.widgets.text("participant_id", "", "Tu identificador")
dbutils.widgets.text("confirmation", "", "Escribir DELETE")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
CONFIRMATION = dbutils.widgets.get("confirmation").strip()

if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Nombre de catálogo inválido.")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido. Usa solo a-z, 0-9 o _.")

if CONFIRMATION != "DELETE":
    raise ValueError("Limpieza cancelada. Escribe DELETE para confirmar.")

SCHEMAS = (
    f"bronze_{PARTICIPANT_ID}",
    f"silver_{PARTICIPANT_ID}",
    f"gold_{PARTICIPANT_ID}",
    f"ops_{PARTICIPANT_ID}",
)

print(f"Se eliminarán permanentemente estos schemas de {CATALOG}: {SCHEMAS}")

# COMMAND ----------

for schema in SCHEMAS:
    spark.sql(f"DROP SCHEMA IF EXISTS `{CATALOG}`.`{schema}` CASCADE")
    print(f"Schema {CATALOG}.{schema} eliminado.")