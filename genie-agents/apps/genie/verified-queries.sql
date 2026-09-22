-- Reemplazar <catalog> por el catálogo del participante.
-- Registrar cada bloque por separado como consulta verificada en Genie.

-- ============================================================================
-- Q01. ¿Qué regiones tienen mayor ingreso neto en los últimos 30 días?
-- ============================================================================
SELECT
  region,
  MEASURE(net_revenue) AS net_revenue,
  MEASURE(gross_margin) AS gross_margin,
  MEASURE(units_sold) AS units_sold
FROM <catalog>.<gold_schema>.retail_performance_metrics
WHERE event_date >= date_sub(current_date(), 29)
GROUP BY ALL
ORDER BY net_revenue DESC
LIMIT 10;

-- ============================================================================
-- Q02. ¿Cuáles son las cinco alertas críticas con mayor ingreso en riesgo?
-- ============================================================================
SELECT
  store_name,
  region,
  sku,
  product_name,
  category,
  days_of_cover,
  lead_time_days,
  revenue_at_risk,
  recommended_replenishment_units
FROM <catalog>.<gold_schema>.decision_queue
WHERE priority = 'CRITICAL'
ORDER BY revenue_at_risk DESC, store_name, sku
LIMIT 5;

-- ============================================================================
-- Q03. ¿Dónde está concentrado el ingreso en riesgo?
-- ============================================================================
SELECT
  region,
  category,
  COUNT(*) AS alerts,
  ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk,
  SUM(recommended_replenishment_units) AS recommended_units
FROM <catalog>.<gold_schema>.decision_queue
WHERE priority IN ('CRITICAL', 'HIGH')
GROUP BY ALL
ORDER BY revenue_at_risk DESC
LIMIT 10;

-- ============================================================================
-- Q04. ¿Qué sucursales tienen más alertas críticas?
-- ============================================================================
SELECT
  store_name,
  region,
  COUNT(*) AS critical_alerts,
  ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
FROM <catalog>.<gold_schema>.decision_queue
WHERE priority = 'CRITICAL'
GROUP BY ALL
ORDER BY critical_alerts DESC, revenue_at_risk DESC
LIMIT 10;

-- ============================================================================
-- Q05. ¿Qué acciones se crearon hoy y quién es responsable?
-- ============================================================================
SELECT
  created_at,
  decision_type,
  status,
  priority,
  store_name,
  sku,
  recommended_units,
  assignee,
  due_at,
  created_by
FROM <catalog>.<gold_schema>.current_actions
WHERE CAST(created_at AS DATE) = current_date()
ORDER BY created_at DESC;

-- ============================================================================
-- Q06. ¿Qué tareas están vencidas?
-- ============================================================================
SELECT
  action_id,
  decision_type,
  priority,
  store_name,
  sku,
  assignee,
  due_at,
  datediff(current_timestamp(), due_at) AS days_overdue
FROM <catalog>.<gold_schema>.current_actions
WHERE is_overdue
ORDER BY days_overdue DESC, priority;

-- ============================================================================
-- Q07. ¿Qué alertas críticas todavía no tienen una acción vigente?
-- ============================================================================
SELECT
  q.alert_id,
  q.store_name,
  q.region,
  q.sku,
  q.days_of_cover,
  q.lead_time_days,
  q.revenue_at_risk,
  q.recommended_replenishment_units
FROM <catalog>.<gold_schema>.decision_queue q
LEFT ANTI JOIN <catalog>.<gold_schema>.current_actions a
  ON q.alert_id = a.alert_id
 AND a.status IN ('OPEN', 'IN_PROGRESS', 'DONE')
WHERE q.priority = 'CRITICAL'
ORDER BY q.revenue_at_risk DESC
LIMIT 20;

-- ============================================================================
-- Q08. ¿Qué reglas de calidad presentan más fallas?
-- ============================================================================
SELECT
  rule_id,
  rule_description,
  failed_rows,
  total_rows,
  pass_rate_pct
FROM <catalog>.<gold_schema>.data_quality_summary
ORDER BY failed_rows DESC, rule_id;

-- ============================================================================
-- Q09. Compara ingreso y margen por canal durante los últimos 30 días.
-- ============================================================================
SELECT
  channel,
  MEASURE(net_revenue) AS net_revenue,
  MEASURE(gross_margin) AS gross_margin,
  ROUND(
    MEASURE(gross_margin) / NULLIF(MEASURE(net_revenue), 0) * 100,
    2
  ) AS gross_margin_pct
FROM <catalog>.<gold_schema>.retail_performance_metrics
WHERE event_date >= date_sub(current_date(), 29)
GROUP BY ALL
ORDER BY net_revenue DESC;

-- ============================================================================
-- Q10. ¿Cuántas unidades de reposición fueron aprobadas por región?
-- ============================================================================
SELECT
  q.region,
  COUNT(*) AS approved_actions,
  SUM(a.recommended_units) AS approved_units
FROM <catalog>.<gold_schema>.current_actions a
JOIN <catalog>.<gold_schema>.decision_queue q USING (alert_id)
WHERE a.decision_type = 'APPROVE_REPLENISHMENT'
  AND a.status IN ('OPEN', 'IN_PROGRESS', 'DONE')
GROUP BY ALL
ORDER BY approved_units DESC;

-- ============================================================================
-- Q11. Tendencia diaria de ingreso neto durante los últimos 14 días.
-- ============================================================================
SELECT
  event_date,
  MEASURE(net_revenue) AS net_revenue,
  MEASURE(gross_margin) AS gross_margin
FROM <catalog>.<gold_schema>.retail_performance_metrics
WHERE event_date >= date_sub(current_date(), 13)
GROUP BY ALL
ORDER BY event_date;

-- ============================================================================
-- Q12. ¿Qué categorías requieren más unidades de reposición inmediata?
-- ============================================================================
SELECT
  category,
  COUNT(*) AS alerts,
  SUM(recommended_replenishment_units) AS recommended_units,
  ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
FROM <catalog>.<gold_schema>.decision_queue
WHERE priority IN ('CRITICAL', 'HIGH')
GROUP BY ALL
ORDER BY recommended_units DESC
LIMIT 10;
