-- @param queue_table STRING
-- @param priority STRING
-- @param row_limit INT
SELECT
  alert_id,
  priority,
  taxpayer_id,
  taxpayer_name,
  ruc,
  segment,
  region,
  economic_activity,
  risk_score,
  declared_sales,
  third_party_sales,
  sales_gap,
  claimed_tax_credit,
  credit_ratio,
  amendment_count,
  signal_count,
  primary_signal,
  recommended_action,
  evidence_summary
FROM IDENTIFIER(:queue_table)
WHERE (:priority = 'ALL' OR priority = :priority)
ORDER BY
  CASE priority
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    ELSE 4
  END,
  risk_score DESC,
  alert_id
LIMIT :row_limit
