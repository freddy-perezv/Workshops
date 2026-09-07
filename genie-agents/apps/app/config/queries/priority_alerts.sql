-- @param queue_table STRING
-- @param priority STRING
-- @param row_limit INT
SELECT
  alert_id,
  priority,
  store_name,
  province,
  sku,
  product_name,
  category,
  on_hand_units,
  in_transit_units,
  avg_daily_units,
  days_of_cover,
  lead_time_days,
  recommended_replenishment_units,
  revenue_at_risk,
  recommended_action
FROM IDENTIFIER(:queue_table)
WHERE (:priority = 'ALL' OR priority = :priority)
ORDER BY
  CASE priority
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    ELSE 4
  END,
  revenue_at_risk DESC,
  alert_id
LIMIT :row_limit
