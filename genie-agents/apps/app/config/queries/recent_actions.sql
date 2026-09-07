-- @param actions_table STRING
-- @param row_limit INT
-- @param refresh_token STRING
SELECT
  action_id,
  alert_id,
  decision_type,
  status,
  assignee,
  notes,
  priority,
  store_name,
  sku,
  recommended_units,
  created_by,
  created_at,
  due_at,
  CASE
    WHEN status NOT IN ('DONE', 'CANCELLED') AND due_at < current_timestamp()
      THEN true
    ELSE false
  END AS is_overdue
FROM IDENTIFIER(:actions_table)
WHERE :refresh_token IS NOT NULL
ORDER BY created_at DESC
LIMIT :row_limit
