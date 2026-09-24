-- Sustituir <catalog> y <gold_schema>. Registrar cada bloque por separado.

-- Q01. Ventas declaradas e impuesto por región, últimos 90 días
SELECT region,
  MEASURE(declared_sales) declared_sales,
  MEASURE(assessed_tax) assessed_tax,
  MEASURE(taxpayers_count) taxpayers_count
FROM <catalog>.<gold_schema>.tax_risk_metrics
WHERE event_date >= date_sub(current_date(), 89)
GROUP BY ALL ORDER BY declared_sales DESC;

-- Q02. Cinco alertas de mayor puntaje
SELECT alert_id, priority, taxpayer_name, ruc, region, risk_score,
       signal_count, primary_signal, evidence_summary, recommended_action
FROM <catalog>.<gold_schema>.risk_queue
ORDER BY risk_score DESC, signal_count DESC LIMIT 5;

-- Q03. Brecha de ventas por región y segmento
SELECT region, segment, COUNT(*) alerts, ROUND(SUM(sales_gap), 2) sales_gap
FROM <catalog>.<gold_schema>.risk_queue
WHERE sales_gap > 0
GROUP BY ALL ORDER BY sales_gap DESC;

-- Q04. Crédito fiscal excesivo
SELECT taxpayer_name, ruc, claimed_tax_credit, credit_ratio,
       risk_score, evidence_summary
FROM <catalog>.<gold_schema>.risk_queue
WHERE primary_signal = 'EXCESSIVE_TAX_CREDIT' OR credit_ratio > 1.2
ORDER BY credit_ratio DESC LIMIT 10;

-- Q05. Rectificatorias inusuales
SELECT taxpayer_name, ruc, amendment_count, risk_score, priority,
       evidence_summary
FROM <catalog>.<gold_schema>.risk_queue
WHERE amendment_count >= 4
ORDER BY amendment_count DESC, risk_score DESC LIMIT 10;

-- Q06. Distribución agregada de señales
SELECT region, segment, economic_activity, priority,
       COUNT(*) alerts, ROUND(AVG(risk_score), 1) avg_risk_score
FROM <catalog>.<gold_schema>.risk_queue
GROUP BY ALL ORDER BY alerts DESC;

-- Q07. Reglas de calidad con más fallas
SELECT rule_id, rule_description, failed_rows, total_rows, pass_rate_pct
FROM <catalog>.<gold_schema>.data_quality_summary
ORDER BY failed_rows DESC, rule_id;

-- Q08. Acciones registradas hoy
SELECT created_at, decision_type, status, priority, taxpayer_name, ruc,
       risk_score, assignee, due_at, created_by
FROM <catalog>.<gold_schema>.current_actions
WHERE CAST(created_at AS DATE) = current_date()
ORDER BY created_at DESC;

-- Q09. Tareas vencidas
SELECT action_id, decision_type, taxpayer_name, ruc, risk_score, assignee, due_at
FROM <catalog>.<gold_schema>.current_actions
WHERE is_overdue ORDER BY due_at;

-- Q10. Alertas críticas sin acción vigente
SELECT q.alert_id, q.taxpayer_name, q.ruc, q.risk_score, q.primary_signal,
       q.evidence_summary
FROM <catalog>.<gold_schema>.risk_queue q
LEFT ANTI JOIN <catalog>.<gold_schema>.current_actions a
  ON q.alert_id = a.alert_id
 AND a.status IN ('OPEN', 'IN_PROGRESS', 'DONE')
WHERE q.priority = 'CRITICAL'
ORDER BY q.risk_score DESC LIMIT 20;

-- Q11. Crédito fiscal por actividad económica
SELECT economic_activity,
  MEASURE(claimed_tax_credit) claimed_tax_credit,
  MEASURE(assessed_tax) assessed_tax,
  MEASURE(taxpayers_count) taxpayers_count
FROM <catalog>.<gold_schema>.tax_risk_metrics
GROUP BY ALL ORDER BY claimed_tax_credit DESC;

-- Q12. Seguimiento de investigaciones
SELECT status, priority, COUNT(*) actions,
       ROUND(AVG(risk_score), 1) avg_risk_score,
       COUNT_IF(is_overdue) overdue
FROM <catalog>.<gold_schema>.current_actions
WHERE decision_type = 'OPEN_INVESTIGATION'
GROUP BY ALL ORDER BY actions DESC;
