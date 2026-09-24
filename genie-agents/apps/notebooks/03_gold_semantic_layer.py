# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Radar Tributario · 03 · Gold, señales y capa semántica
# MAGIC
# MAGIC Las reglas priorizan señales explicables para revisión humana. Un
# MAGIC puntaje alto no demuestra fraude, evasión ni incumplimiento: indica que
# MAGIC conviene revisar datos y contexto antes de decidir.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "radar_tributario_workshop", "Catálogo")
dbutils.widgets.text("participant_id", "", "Identificador")
dbutils.widgets.dropdown("optimize_tables", "false", ["true", "false"], "Optimizar")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
OPTIMIZE_TABLES = dbutils.widgets.get("optimize_tables") == "true"
if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError("Catálogo inválido")
if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError("Identificador inválido")
BRONZE_SCHEMA = f"bronze_{PARTICIPANT_ID}"
SILVER_SCHEMA = f"silver_{PARTICIPANT_ID}"
GOLD_SCHEMA = f"gold_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"
spark.conf.set("spark.sql.session.timeZone", "America/Lima")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Actividad diaria del contribuyente

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE `{CATALOG}`.`{GOLD_SCHEMA}`.`taxpayer_activity_daily`
    USING DELTA
    CLUSTER BY (event_date, region, segment)
    COMMENT 'Actividad tributaria diaria sintética; no representa contribuyentes reales'
    AS
    WITH document_activity AS (
      SELECT event_date, taxpayer_id, taxpayer_name, ruc, segment, region,
             economic_activity,
             ROUND(SUM(CASE WHEN flow_type = 'SALE' THEN taxable_amount ELSE 0 END), 2)
               AS third_party_sales,
             ROUND(SUM(CASE WHEN flow_type = 'PURCHASE' THEN tax_amount ELSE 0 END), 2)
               AS document_tax_credit,
             COUNT(*) AS document_count
      FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`tax_documents`
      GROUP BY ALL
    ),
    filing_activity AS (
      SELECT event_date, taxpayer_id, taxpayer_name, ruc, segment, region,
             economic_activity,
             ROUND(SUM(declared_sales), 2) AS declared_sales,
             ROUND(SUM(assessed_tax), 2) AS assessed_tax,
             ROUND(SUM(claimed_tax_credit), 2) AS claimed_tax_credit,
             SUM(amendment_count) AS amendment_count
      FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`tax_filings`
      GROUP BY ALL
    )
    SELECT
      COALESCE(f.event_date, d.event_date) AS event_date,
      COALESCE(f.taxpayer_id, d.taxpayer_id) AS taxpayer_id,
      COALESCE(f.taxpayer_name, d.taxpayer_name) AS taxpayer_name,
      COALESCE(f.ruc, d.ruc) AS ruc,
      COALESCE(f.segment, d.segment) AS segment,
      COALESCE(f.region, d.region) AS region,
      COALESCE(f.economic_activity, d.economic_activity) AS economic_activity,
      COALESCE(f.declared_sales, 0) AS declared_sales,
      COALESCE(d.third_party_sales, 0) AS third_party_sales,
      COALESCE(f.assessed_tax, 0) AS assessed_tax,
      COALESCE(f.claimed_tax_credit, 0) AS claimed_tax_credit,
      COALESCE(f.amendment_count, 0) AS amendment_count,
      COALESCE(d.document_count, 0) AS document_count
    FROM filing_activity f
    FULL OUTER JOIN document_activity d
      ON f.event_date = d.event_date AND f.taxpayer_id = d.taxpayer_id
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cola explicable de señales de riesgo
# MAGIC
# MAGIC Señales: brecha entre ventas declaradas y comprobantes, crédito fiscal
# MAGIC excesivo, rectificatorias inusuales, emisión estando inactivo/dormido y
# MAGIC duplicados. Se prioriza revisión; no se etiqueta fraude.

# COMMAND ----------

spark.sql(
    f"""
    CREATE OR REPLACE TABLE `{CATALOG}`.`{GOLD_SCHEMA}`.`risk_queue`
    USING DELTA
    CLUSTER BY (priority, region, segment)
    COMMENT 'Cola sintética de señales para revisión; no constituye prueba de fraude'
    AS
    WITH activity AS (
      SELECT taxpayer_id,
             MAX(taxpayer_name) taxpayer_name, MAX(ruc) ruc, MAX(segment) segment,
             MAX(region) region, MAX(economic_activity) economic_activity,
             SUM(declared_sales) declared_sales,
             SUM(third_party_sales) third_party_sales,
             SUM(assessed_tax) assessed_tax,
             SUM(claimed_tax_credit) claimed_tax_credit,
             SUM(amendment_count) amendment_count
      FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`taxpayer_activity_daily`
      GROUP BY taxpayer_id
    ),
    duplicate_documents AS (
      SELECT d.taxpayer_id, COUNT(*) duplicate_count
      FROM `{CATALOG}`.`{BRONZE_SCHEMA}`.`tax_documents` d
      INNER JOIN (
        SELECT document_id
        FROM `{CATALOG}`.`{BRONZE_SCHEMA}`.`tax_documents`
        GROUP BY document_id HAVING COUNT(*) > 1
      ) x USING (document_id)
      GROUP BY d.taxpayer_id
    ),
    status_issuance AS (
      SELECT d.taxpayer_id,
             COUNT_IF(t.taxpayer_status IN ('DORMANT', 'INACTIVE')) inactive_issuance
      FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`tax_documents` d
      JOIN `{CATALOG}`.`{SILVER_SCHEMA}`.`taxpayers` t USING (taxpayer_id)
      GROUP BY d.taxpayer_id
    ),
    signals AS (
      SELECT a.*,
        ROUND(a.third_party_sales - a.declared_sales, 2) sales_gap,
        ROUND(a.claimed_tax_credit / NULLIF(a.assessed_tax, 0), 4) credit_ratio,
        COALESCE(x.duplicate_count, 0) duplicate_count,
        COALESCE(s.inactive_issuance, 0) inactive_issuance,
        CASE WHEN a.third_party_sales > a.declared_sales * 1.30
             AND a.third_party_sales - a.declared_sales > 10000 THEN 1 ELSE 0 END mismatch_signal,
        CASE WHEN a.claimed_tax_credit / NULLIF(a.assessed_tax, 0) > 1.20
             THEN 1 ELSE 0 END credit_signal,
        CASE WHEN a.amendment_count >= 4 THEN 1 ELSE 0 END amendment_signal,
        CASE WHEN COALESCE(s.inactive_issuance, 0) > 0 THEN 1 ELSE 0 END inactive_signal,
        CASE WHEN COALESCE(x.duplicate_count, 0) > 0 THEN 1 ELSE 0 END duplicate_signal
      FROM activity a
      LEFT JOIN duplicate_documents x USING (taxpayer_id)
      LEFT JOIN status_issuance s USING (taxpayer_id)
    ),
    scored AS (
      SELECT *,
        mismatch_signal + credit_signal + amendment_signal + inactive_signal
          + duplicate_signal AS signal_count,
        LEAST(100,
          mismatch_signal * 30 + credit_signal * 25 + amendment_signal * 15
          + inactive_signal * 20 + duplicate_signal * 10
        ) AS risk_score
      FROM signals
    )
    SELECT
      sha2(concat_ws('|', taxpayer_id, CAST(current_date() AS STRING)), 256) alert_id,
      CASE WHEN risk_score >= 70 THEN 'CRITICAL'
           WHEN risk_score >= 45 THEN 'HIGH'
           WHEN risk_score >= 25 THEN 'MEDIUM' ELSE 'LOW' END priority,
      taxpayer_id, taxpayer_name, ruc, segment, region, economic_activity,
      risk_score,
      ROUND(declared_sales, 2) declared_sales,
      ROUND(third_party_sales, 2) third_party_sales,
      sales_gap, ROUND(credit_ratio, 4) credit_ratio,
      ROUND(claimed_tax_credit, 2) claimed_tax_credit,
      amendment_count, signal_count,
      CASE WHEN mismatch_signal = 1 THEN 'SALES_MISMATCH'
           WHEN credit_signal = 1 THEN 'EXCESSIVE_TAX_CREDIT'
           WHEN inactive_signal = 1 THEN 'DORMANT_OR_INACTIVE_ISSUANCE'
           WHEN amendment_signal = 1 THEN 'UNUSUAL_AMENDMENTS'
           ELSE 'DUPLICATE_DOCUMENTS' END primary_signal,
      CASE WHEN risk_score >= 70 THEN 'OPEN_INVESTIGATION'
           WHEN risk_score >= 25 THEN 'REQUEST_CLARIFICATION'
           ELSE 'DISMISS' END recommended_action,
      concat_ws('; ',
        CASE WHEN mismatch_signal = 1 THEN concat('brecha de ventas PEN ', CAST(sales_gap AS STRING)) END,
        CASE WHEN credit_signal = 1 THEN concat('ratio de crédito ', CAST(ROUND(credit_ratio, 2) AS STRING)) END,
        CASE WHEN amendment_signal = 1 THEN concat(CAST(amendment_count AS STRING), ' rectificatorias') END,
        CASE WHEN inactive_signal = 1 THEN concat(CAST(inactive_issuance AS STRING), ' comprobantes con estado inactivo/dormido') END,
        CASE WHEN duplicate_signal = 1 THEN concat(CAST(duplicate_count AS STRING), ' duplicados') END
      ) evidence_summary
    FROM scored
    WHERE signal_count > 0
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Contrato operacional para la App

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks` (
      action_id STRING NOT NULL,
      alert_id STRING NOT NULL,
      decision_type STRING NOT NULL COMMENT 'OPEN_INVESTIGATION, REQUEST_CLARIFICATION o DISMISS',
      status STRING NOT NULL,
      assignee STRING NOT NULL,
      notes STRING,
      priority STRING NOT NULL,
      taxpayer_id STRING NOT NULL,
      taxpayer_name STRING NOT NULL,
      ruc STRING NOT NULL,
      risk_score INT NOT NULL,
      created_by STRING NOT NULL,
      created_at TIMESTAMP NOT NULL,
      due_at TIMESTAMP,
      updated_at TIMESTAMP NOT NULL
    ) USING DELTA
    CLUSTER BY (status, priority, created_at)
    TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true',
                   'delta.enableRowTracking' = 'true')
    """
)
spark.sql(
    f"""
    CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`current_actions`
    AS SELECT *,
      status NOT IN ('DONE', 'CANCELLED') AND due_at < current_timestamp() AS is_overdue
    FROM `{CATALOG}`.`{OPS_SCHEMA}`.`action_tasks`
    """
)
spark.sql(
    f"""
    CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`data_quality_summary`
    AS SELECT rule_id, rule_description, failed_rows, total_rows,
              ROUND(pass_rate * 100, 3) pass_rate_pct, measured_at
    FROM `{CATALOG}`.`{SILVER_SCHEMA}`.`data_quality_metrics`
    """
)

# COMMAND ----------

metric_view_sql = f"""
CREATE OR REPLACE VIEW `{CATALOG}`.`{GOLD_SCHEMA}`.`tax_risk_metrics`
WITH METRICS
LANGUAGE YAML
COMMENT 'Métricas tributarias sintéticas certificadas para Radar Tributario'
AS $$
version: 1.1
source: {CATALOG}.{GOLD_SCHEMA}.taxpayer_activity_daily
fields:
  - name: event_date
    expr: source.event_date
    display_name: Fecha
  - name: region
    expr: source.region
    display_name: Región
  - name: segment
    expr: source.segment
    display_name: Segmento
  - name: economic_activity
    expr: source.economic_activity
    display_name: Actividad económica
measures:
  - name: declared_sales
    expr: SUM(source.declared_sales)
    display_name: Ventas declaradas
  - name: assessed_tax
    expr: SUM(source.assessed_tax)
    display_name: Impuesto determinado
  - name: claimed_tax_credit
    expr: SUM(source.claimed_tax_credit)
    display_name: Crédito fiscal declarado
  - name: taxpayers_count
    expr: COUNT(DISTINCT source.taxpayer_id)
    display_name: Contribuyentes
$$
"""
spark.sql(metric_view_sql)

if OPTIMIZE_TABLES:
    for table in ("taxpayer_activity_daily", "risk_queue"):
        spark.sql(f"OPTIMIZE `{CATALOG}`.`{GOLD_SCHEMA}`.`{table}`")

# COMMAND ----------

display(
    spark.sql(
        f"""SELECT priority, COUNT(*) alerts, ROUND(AVG(risk_score), 1) avg_score
        FROM `{CATALOG}`.`{GOLD_SCHEMA}`.`risk_queue`
        GROUP BY priority ORDER BY avg_score DESC"""
    )
)