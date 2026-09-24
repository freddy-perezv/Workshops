import { useEffect, useMemo, useState } from 'react';
import { useAnalyticsQuery } from '@databricks/appkit-ui/react';
import { sql } from '@databricks/appkit-ui/js';
import { mockActions, mockAlerts, mockKpis, mockTrend } from './mock-data';
import type {
  ActionInput,
  ActionRow,
  ActionStatus,
  AlertRow,
  AppConfig,
  KpiRow,
  Priority,
  TrendRow,
} from './types';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';
const MOCK_CONFIG: AppConfig = {
  queueTable: 'workshop_tax.gold.risk_queue',
  metricView: 'workshop_tax.gold.tax_risk_metrics',
  actionsTable: 'workshop_tax.ops.action_tasks',
};

export function useWorkshopData(priority: Priority | 'ALL') {
  const [config, setConfig] = useState<AppConfig | null>(
    MOCK_MODE ? MOCK_CONFIG : null,
  );
  const [configError, setConfigError] = useState<string | null>(null);
  const [identity, setIdentity] = useState('responsable@empresa.com');
  const [refreshToken, setRefreshToken] = useState(() => crypto.randomUUID());
  const [mockActionRows, setMockActionRows] = useState(mockActions);

  useEffect(() => {
    if (MOCK_MODE) return;

    Promise.all([
      fetch('/api/config').then(async (response) => {
        if (!response.ok) throw new Error('No se pudo leer la configuración.');
        return (await response.json()) as AppConfig;
      }),
      fetch('/api/identity').then(async (response) => {
        if (!response.ok) return null;
        return (await response.json()) as { email: string };
      }),
    ])
      .then(([appConfig, user]) => {
        setConfig(appConfig);
        if (user?.email) setIdentity(user.email);
      })
      .catch((error: unknown) => {
        setConfigError(
          error instanceof Error ? error.message : 'Configuración no disponible.',
        );
      });
  }, []);

  const kpiParameters = useMemo(
    () => ({
      metric_view: sql.string(config?.metricView ?? ''),
    }),
    [config?.metricView],
  );
  const alertParameters = useMemo(
    () => ({
      queue_table: sql.string(config?.queueTable ?? ''),
      priority: sql.string(priority),
      row_limit: sql.int(30),
    }),
    [config, priority],
  );
  const trendParameters = useMemo(
    () => ({
      metric_view: sql.string(config?.metricView ?? ''),
    }),
    [config],
  );
  const actionParameters = useMemo(
    () => ({
      actions_table: sql.string(config?.actionsTable ?? ''),
      row_limit: sql.int(20),
      refresh_token: sql.string(refreshToken),
    }),
    [config, refreshToken],
  );

  const kpisQuery = useAnalyticsQuery<KpiRow[]>(
    'executive_kpis',
    kpiParameters,
    { autoStart: !MOCK_MODE && Boolean(config) },
  );
  const alertsQuery = useAnalyticsQuery<AlertRow[]>(
    'priority_alerts',
    alertParameters,
    { autoStart: !MOCK_MODE && Boolean(config) },
  );
  const trendQuery = useAnalyticsQuery<TrendRow[]>(
    'revenue_trend',
    trendParameters,
    { autoStart: !MOCK_MODE && Boolean(config) },
  );
  const actionsQuery = useAnalyticsQuery<ActionRow[]>(
    'recent_actions',
    actionParameters,
    { autoStart: !MOCK_MODE && Boolean(config) },
  );

  const alerts = MOCK_MODE
    ? mockAlerts.filter((alert) => priority === 'ALL' || alert.priority === priority)
    : (alertsQuery.data ?? []);

  async function createAction(input: ActionInput): Promise<string> {
    if (MOCK_MODE) {
      const alert = mockAlerts.find((item) => item.alert_id === input.alertId);
      if (!alert) throw new Error('Alerta no encontrada.');
      const actionId = crypto.randomUUID();
      setMockActionRows((rows) => [
        {
          action_id: actionId,
          alert_id: alert.alert_id,
          decision_type: input.decisionType,
          status: 'OPEN',
          assignee: input.assignee,
          notes: input.notes,
          priority: alert.priority,
          taxpayer_id: alert.taxpayer_id,
          taxpayer_name: alert.taxpayer_name,
          ruc: alert.ruc,
          risk_score: alert.risk_score,
          created_by: identity,
          created_at: new Date().toISOString(),
          due_at: new Date(Date.now() + 24 * 3_600_000).toISOString(),
          is_overdue: false,
        },
        ...rows,
      ]);
      return actionId;
    }

    const response = await fetch('/api/actions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    const payload = (await response.json()) as {
      actionId?: string;
      error?: string;
    };
    if (!response.ok || !payload.actionId) {
      throw new Error(payload.error ?? 'No fue posible crear la acción.');
    }
    setRefreshToken(crypto.randomUUID());
    return payload.actionId;
  }

  async function updateAction(
    actionId: string,
    status: ActionStatus,
  ): Promise<void> {
    if (MOCK_MODE) {
      setMockActionRows((rows) =>
        rows.map((row) =>
          row.action_id === actionId ? { ...row, status } : row,
        ),
      );
      return;
    }

    const response = await fetch(`/api/actions/${actionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (!response.ok) {
      const payload = (await response.json()) as { error?: string };
      throw new Error(payload.error ?? 'No fue posible actualizar la tarea.');
    }
    setRefreshToken(crypto.randomUUID());
  }

  return {
    mockMode: MOCK_MODE,
    identity,
    kpis: MOCK_MODE ? mockKpis : (kpisQuery.data ?? []),
    alerts,
    trend: MOCK_MODE ? mockTrend : (trendQuery.data ?? []),
    actions: MOCK_MODE ? mockActionRows : (actionsQuery.data ?? []),
    loading:
      !MOCK_MODE &&
      (kpisQuery.loading ||
        alertsQuery.loading ||
        trendQuery.loading ||
        actionsQuery.loading),
    error:
      configError ??
      kpisQuery.error ??
      alertsQuery.error ??
      trendQuery.error ??
      actionsQuery.error,
    createAction,
    updateAction,
  };
}
