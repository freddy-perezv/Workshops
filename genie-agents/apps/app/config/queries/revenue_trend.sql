-- @param metric_view STRING
SELECT
  event_date,
  MEASURE(net_revenue) AS net_revenue,
  MEASURE(gross_margin) AS gross_margin
FROM IDENTIFIER(:metric_view)
WHERE event_date >= date_sub(current_date(), 29)
GROUP BY ALL
ORDER BY event_date
