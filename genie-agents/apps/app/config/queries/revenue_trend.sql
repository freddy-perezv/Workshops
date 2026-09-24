-- @param metric_view STRING
SELECT
  event_date,
  MEASURE(declared_sales) AS declared_sales,
  MEASURE(assessed_tax) AS assessed_tax
FROM IDENTIFIER(:metric_view)
WHERE event_date >= date_sub(current_date(), 29)
GROUP BY ALL
ORDER BY event_date
