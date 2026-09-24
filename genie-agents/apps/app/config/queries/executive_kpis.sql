-- @param metric_view STRING
-- @param queue_table STRING
WITH tax_activity AS (
  SELECT
    ROUND(MEASURE(declared_sales), 2) AS declared_sales,
    ROUND(MEASURE(assessed_tax), 2) AS assessed_tax,
    ROUND(MEASURE(claimed_tax_credit), 2) AS claimed_tax_credit
  FROM IDENTIFIER(:metric_view)
  WHERE event_date >= date_sub(current_date(), 29)
),
risk AS (
  SELECT
    COUNT_IF(priority IN ('CRITICAL', 'HIGH')) AS high_risk_taxpayers,
    ROUND(
      COALESCE(
        SUM(
          CASE
            WHEN priority IN ('CRITICAL', 'HIGH')
              THEN GREATEST(sales_gap, 0) + claimed_tax_credit
            ELSE 0
          END
        ),
        0
      ),
      2
    ) AS exposure_amount
  FROM IDENTIFIER(:queue_table)
)
SELECT
  a.declared_sales,
  a.assessed_tax,
  a.claimed_tax_credit,
  r.high_risk_taxpayers,
  r.exposure_amount
FROM tax_activity a
CROSS JOIN risk r
