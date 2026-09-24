export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type DecisionType =
  | 'OPEN_INVESTIGATION'
  | 'REQUEST_CLARIFICATION'
  | 'DISMISS';
export type ActionStatus = 'OPEN' | 'IN_PROGRESS' | 'DONE' | 'CANCELLED';

export interface AppConfig {
  queueTable: string;
  metricView: string;
  actionsTable: string;
}

export interface KpiRow {
  declared_sales: string | number;
  assessed_tax: string | number;
  claimed_tax_credit: string | number;
  high_risk_taxpayers: string | number;
  exposure_amount: string | number;
}

export interface TrendRow {
  event_date: string;
  declared_sales: string | number;
  assessed_tax: string | number;
}

export interface AlertRow {
  alert_id: string;
  priority: Priority;
  taxpayer_id: string;
  taxpayer_name: string;
  ruc: string;
  segment: string;
  region: string;
  economic_activity: string;
  risk_score: string | number;
  declared_sales: string | number;
  third_party_sales: string | number;
  sales_gap: string | number;
  claimed_tax_credit: string | number;
  credit_ratio: string | number;
  amendment_count: string | number;
  signal_count: string | number;
  primary_signal: string;
  recommended_action: DecisionType;
  evidence_summary: string;
}

export interface ActionRow {
  action_id: string;
  alert_id: string;
  decision_type: DecisionType;
  status: ActionStatus;
  assignee: string;
  notes: string;
  priority: Priority;
  taxpayer_id: string;
  taxpayer_name: string;
  ruc: string;
  risk_score: string | number;
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
