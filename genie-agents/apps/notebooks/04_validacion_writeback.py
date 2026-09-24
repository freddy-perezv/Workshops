# Databricks notebook source
# MAGIC %md
# MAGIC # Radar Tributario · 04 · Validación del ciclo humano
# MAGIC
# MAGIC Ejecuta esta notebook después de registrar una acción en la App. La
# MAGIC acción documenta una decisión de revisión sobre señales sintéticas; no
# MAGIC confirma fraude ni determina una deuda tributaria.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "radar_tributario_workshop", "Catálogo")
dbutils.widgets.text("participant_id", "", "Identificador")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Catálogo inválido")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido")
GOLD_SCHEMA = f"gold_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"
spark.conf.set("spark.sql.session.timeZone", "America/Lima")

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT action_id, alert_id, decision_type, status, priority,
               taxpayer_id, taxpayer_name, ruc, risk_score,
               assignee, created_by, created_at, due_at
        FROM `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks`
        ORDER BY created_at DESC LIMIT 20
        """
    )
)

# COMMAND ----------

history = spark.sql(f"DESCRIBE HISTORY `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks`")
current_version = int(history.agg({"version": "max"}).first()[0] or 0)
try:
    display(
        spark.sql(
            f"""
            SELECT _change_type, _commit_version, _commit_timestamp,
                   action_id, decision_type, status, assignee
            FROM table_changes('{CATALOG}.{OPS_SCHEMA}.action_tasks',
                               {max(0, current_version - 10)})
            ORDER BY _commit_version DESC
            """
        )
    )
except Exception as exc:
    print(f"Sin cambios disponibles todavía: {exc}")

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT decision_type, status, COUNT(*) tasks,
               COUNT_IF(is_overdue) overdue_tasks,
               ROUND(AVG(risk_score), 1) avg_risk_score
        FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`current_actions`
        GROUP BY ALL ORDER BY tasks DESC
        """
    )
)

# MAGIC %md
# MAGIC Regresa a Genie y pregunta: “¿Qué acciones se registraron hoy y qué
# MAGIC señales sustentaron su priorización?”. La respuesta debe separar
# MAGIC evidencia analítica, decisión humana y limitaciones de los datos.
