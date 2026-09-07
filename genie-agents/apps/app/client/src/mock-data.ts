import type { ActionRow, AlertRow, KpiRow, TrendRow } from './types';

export const mockKpis: KpiRow[] = [
  {
    net_revenue: 284_560_320,
    gross_margin: 58_742_110,
    units_sold: 1_284_903,
    critical_alerts: 18,
    revenue_at_risk: 12_840_500,
  },
];

export const mockAlerts: AlertRow[] = [
  {
    alert_id: 'a'.repeat(64),
    priority: 'CRITICAL',
    store_name: 'Sucursal 047',
    province: 'Santa Fe',
    sku: 'SKU-00183',
    product_name: 'Producto 183',
    category: 'Frescos',
    on_hand_units: 8,
    in_transit_units: 0,
    avg_daily_units: 14.7,
    days_of_cover: 0.5,
    lead_time_days: 9,
    recommended_replenishment_units: 227,
    revenue_at_risk: 1_842_300,
    recommended_action: 'APPROVE_REPLENISHMENT',
  },
  {
    alert_id: 'b'.repeat(64),
    priority: 'CRITICAL',
    store_name: 'Sucursal 012',
    province: 'Entre Ríos',
    sku: 'SKU-00272',
    product_name: 'Producto 272',
    category: 'Bebidas',
    on_hand_units: 12,
    in_transit_units: 5,
    avg_daily_units: 11.2,
    days_of_cover: 1.5,
    lead_time_days: 7,
    recommended_replenishment_units: 140,
    revenue_at_risk: 978_420,
    recommended_action: 'APPROVE_REPLENISHMENT',
  },
  {
    alert_id: 'c'.repeat(64),
    priority: 'HIGH',
    store_name: 'Sucursal 091',
    province: 'Mendoza',
    sku: 'SKU-00064',
    product_name: 'Producto 064',
    category: 'Lácteos',
    on_hand_units: 22,
    in_transit_units: 10,
    avg_daily_units: 8.5,
    days_of_cover: 3.8,
    lead_time_days: 6,
    recommended_replenishment_units: 79,
    revenue_at_risk: 421_800,
    recommended_action: 'INVESTIGATE',
  },
  {
    alert_id: 'd'.repeat(64),
    priority: 'MEDIUM',
    store_name: 'Sucursal 105',
    province: 'Neuquén',
    sku: 'SKU-00321',
    product_name: 'Producto 321',
    category: 'Limpieza',
    on_hand_units: 45,
    in_transit_units: 8,
    avg_daily_units: 7.1,
    days_of_cover: 7.5,
    lead_time_days: 6,
    recommended_replenishment_units: 39,
    revenue_at_risk: 82_600,
    recommended_action: 'INVESTIGATE',
  },
];

export const mockTrend: TrendRow[] = Array.from({ length: 14 }, (_, index) => ({
  event_date: new Date(Date.now() - (13 - index) * 86_400_000)
    .toISOString()
    .slice(0, 10),
  net_revenue: 7_800_000 + index * 185_000 + (index % 3) * 410_000,
  gross_margin: 1_560_000 + index * 42_000,
}));

export const mockActions: ActionRow[] = [
  {
    action_id: '4a93d12a-719d-4e36-a6cd-90e509964145',
    alert_id: 'z'.repeat(64),
    decision_type: 'APPROVE_REPLENISHMENT',
    status: 'OPEN',
    assignee: 'operaciones@empresa.com',
    notes: 'Reposición prioritaria validada con responsable regional.',
    priority: 'CRITICAL',
    store_name: 'Sucursal 033',
    sku: 'SKU-00098',
    recommended_units: 184,
    created_by: 'participante@empresa.com',
    created_at: new Date(Date.now() - 35 * 60_000).toISOString(),
    due_at: new Date(Date.now() + 23 * 3_600_000).toISOString(),
    is_overdue: false,
  },
];
