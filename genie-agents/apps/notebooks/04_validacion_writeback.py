# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Validar el ciclo de decisión
# MAGIC
# MAGIC Ejecuta esta notebook **después de crear una acción en la App**.
# MAGIC
# MAGIC El objetivo es demostrar el ciclo completo:
# MAGIC
# MAGIC `Gold → Genie → decisión humana → write-back → auditoría → Genie`

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_argentina_equipo_01", "Catálogo")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Nombre de catálogo inválido.")

spark.conf.set("spark.sql.session.timeZone", "America/Argentina/Buenos_Aires")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Confirmar que la decisión quedó persistida

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT
          action_id,
          decision_type,
          status,
          priority,
          store_name,
          sku,
          recommended_units,
          assignee,
          created_by,
          created_at,
          due_at
        FROM `{CATALOG}`.`ops`.`action_tasks`
        ORDER BY created_at DESC
        LIMIT 20
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Observar Change Data Feed
# MAGIC
# MAGIC Change Data Feed permite enviar estas decisiones a otras aplicaciones,
# MAGIC pipelines o sistemas de notificación sin releer la tabla completa.

# COMMAND ----------

history = spark.sql(
    f"DESCRIBE HISTORY `{CATALOG}`.`ops`.`action_tasks`"
)
current_version = int(history.agg({"version": "max"}).first()[0] or 0)
starting_version = max(0, current_version - 10)

try:
    display(
        spark.sql(
            f"""
            SELECT
              _change_type,
              _commit_version,
              _commit_timestamp,
              action_id,
              decision_type,
              status,
              assignee
            FROM table_changes(
              '{CATALOG}.ops.action_tasks',
              {starting_version}
            )
            ORDER BY _commit_version DESC
            """
        )
    )
except Exception as exc:
    print(
        "La tabla todavía no tiene commits de datos o el historial disponible "
        f"empieza después de la versión solicitada. Detalle: {exc}"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Resumen listo para Genie

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT
          decision_type,
          status,
          COUNT(*) AS tasks,
          COUNT_IF(due_at < current_timestamp() AND status NOT IN ('DONE', 'CANCELLED'))
            AS overdue_tasks,
          SUM(recommended_units) AS committed_units
        FROM `{CATALOG}`.`gold`.`current_actions`
        GROUP BY ALL
        ORDER BY tasks DESC
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Cerrar el ciclo en Genie
# MAGIC
# MAGIC Regresa al chat de la App y pregunta:
# MAGIC
# MAGIC > ¿Qué decisiones se tomaron hoy, quién es responsable y cuántas
# MAGIC > unidades de reposición fueron comprometidas?
# MAGIC
# MAGIC Después pregunta:
# MAGIC
# MAGIC > ¿Quedan alertas críticas sin una acción abierta?
# MAGIC
# MAGIC La primera pregunta utiliza `gold.current_actions`; la segunda cruza
# MAGIC conceptualmente las acciones con `gold.decision_queue`.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ La decisión persiste, tiene identidad y vencimiento, aparece en el
# MAGIC historial de cambios y puede ser consultada por Genie.
