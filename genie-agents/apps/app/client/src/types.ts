export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type DecisionType =
  | 'APPROVE_REPLENISHMENT'
  | 'INVESTIGATE'
  | 'DISMISS';
export type ActionStatus = 'OPEN' | 'IN_PROGRESS' | 'DONE' | 'CANCELLED';

export interface AppConfig {
  queueTable: string;
  metricView: string;
  actionsTable: string;
}

export interface KpiRow {
  net_revenue: string | number;
  gross_margin: string | number;
  units_sold: string | number;
  critical_alerts: string | number;
  revenue_at_risk: string | number;
}

export interface TrendRow {
  event_date: string;
  net_revenue: string | number;
  gross_margin: string | number;
}

export interface AlertRow {
  alert_id: string;
  priority: Priority;
  store_name: string;
  region: string;
  sku: string;
  product_name: string;
  category: string;
  on_hand_units: string | number;
  in_transit_units: string | number;
  avg_daily_units: string | number;
  days_of_cover: string | number;
  lead_time_days: string | number;
  recommended_replenishment_units: string | number;
  revenue_at_risk: string | number;
  recommended_action: DecisionType | 'MONITOR';
}

export interface ActionRow {
  action_id: string;
  alert_id: string;
  decision_type: DecisionType;
  status: ActionStatus;
  assignee: string;
  notes: string;
  priority: Priority;
  store_name: string;
  sku: string;
  recommended_units: string | number;
  created_by: string;
  created_at: string;
  due_at: string;
  is_overdue: boolean | string;
}

export interface ActionInput {
  alertId: string;
  decisionType: DecisionType;
  assignee: string;
  notes: string;
}
