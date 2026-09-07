-- @param metric_view STRING
-- @param queue_table STRING
WITH performance AS (
  SELECT
    MEASURE(net_revenue) AS net_revenue,
    MEASURE(gross_margin) AS gross_margin,
    MEASURE(units_sold) AS units_sold
  FROM IDENTIFIER(:metric_view)
  WHERE event_date >= date_sub(current_date(), 29)
),
risk AS (
  SELECT
    COUNT_IF(priority = 'CRITICAL') AS critical_alerts,
    COALESCE(SUM(CASE WHEN priority IN ('CRITICAL', 'HIGH') THEN revenue_at_risk END), 0)
      AS revenue_at_risk
  FROM IDENTIFIER(:queue_table)
)
SELECT
  ROUND(p.net_revenue, 2) AS net_revenue,
  ROUND(p.gross_margin, 2) AS gross_margin,
  p.units_sold,
  r.critical_alerts,
  ROUND(r.revenue_at_risk, 2) AS revenue_at_risk
FROM performance p
CROSS JOIN risk r
