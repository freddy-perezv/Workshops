# Databricks notebook source
# MAGIC %md
# MAGIC # 99 · Limpieza opcional
# MAGIC
# MAGIC Esta notebook elimina **todo el catálogo del laboratorio**, incluyendo
# MAGIC tablas, views, volume, decisiones e historial.
# MAGIC
# MAGIC No debe ejecutarse durante el workshop. Úsala únicamente cuando el
# MAGIC equipo confirme que ya no necesita los resultados.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "", "Catálogo a eliminar")
dbutils.widgets.text("confirmation", "", "Escribir DELETE")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
CONFIRMATION = dbutils.widgets.get("confirmation").strip()

if not re.fullmatch(r"workshop_[a-z0-9_]{3,54}", CATALOG):
    raise ValueError(
        "Por seguridad, solo se eliminan catálogos cuyo nombre inicia con workshop_."
    )

if CONFIRMATION != "DELETE":
    raise ValueError("Limpieza cancelada. Escribe DELETE para confirmar.")

print(f"Se eliminará permanentemente el catálogo: {CATALOG}")

# COMMAND ----------

spark.sql(f"DROP CATALOG `{CATALOG}` CASCADE")
print(f"Catálogo {CATALOG} eliminado.")
