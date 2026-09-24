import { randomUUID } from 'node:crypto';
import type { IncomingHttpHeaders } from 'node:http';
import type { Application } from 'express';
import { sql } from '@databricks/appkit';
import type { SQLTypeMarker } from '@databricks/appkit-ui/js';
import { z } from 'zod';

interface WorkshopAppKit {
  analytics: {
    query(
      statement: string,
      parameters?: Record<string, SQLTypeMarker | null | undefined>,
    ): Promise<unknown>;
  };
  server: {
    extend(callback: (app: Application) => void): void;
  };
}

const CreateActionBody = z.object({
  alertId: z.string().length(64),
  decisionType: z.enum([
    'OPEN_INVESTIGATION',
    'REQUEST_CLARIFICATION',
    'DISMISS',
  ]),
  assignee: z.string().trim().email().max(254),
  notes: z.string().trim().min(8).max(1000),
});

const UpdateStatusBody = z.object({
  status: z.enum(['OPEN', 'IN_PROGRESS', 'DONE', 'CANCELLED']),
});

const TABLE_NAME_PATTERN =
  /^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$/;

function requiredTable(name: string): string {
  const value = process.env[name];
  if (!value || !TABLE_NAME_PATTERN.test(value)) {
    throw new Error(`${name} must be a three-part Unity Catalog table name`);
  }
  return value;
}

function requestActor(headers: IncomingHttpHeaders): string {
  const forwarded = headers['x-forwarded-email'];
  return typeof forwarded === 'string' && forwarded.length > 0
    ? forwarded
    : 'local-workshop-user';
}

function slaHours(decisionType: z.infer<typeof CreateActionBody>['decisionType']) {
  if (decisionType === 'OPEN_INVESTIGATION') return 24;
  if (decisionType === 'REQUEST_CLARIFICATION') return 72;
  return 72;
}

export function setupDecisionRoutes(appkit: WorkshopAppKit) {
  appkit.server.extend((app) => {
    app.get('/api/identity', (req, res) => {
      res.json({ email: requestActor(req.headers) });
    });

    app.get('/api/config', (_req, res) => {
      try {
        res.json({
          queueTable: requiredTable('GOLD_QUEUE_TABLE'),
          metricView: requiredTable('GOLD_METRIC_VIEW'),
          actionsTable: requiredTable('OPS_ACTIONS_TABLE'),
        });
      } catch (error) {
        console.error('[radar-tributario] Invalid table configuration', error);
        res.status(503).json({
          error:
            'La App no tiene configurados sus recursos de Unity Catalog.',
        });
      }
    });

    app.post('/api/actions', async (req, res) => {
      const parsed = CreateActionBody.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({
          error:
            'La acción requiere alerta, tipo de decisión, responsable válido y una justificación.',
        });
        return;
      }

      try {
        const actionsTable = requiredTable('OPS_ACTIONS_TABLE');
        const queueTable = requiredTable('GOLD_QUEUE_TABLE');
        const actionId = randomUUID();
        const actor = requestActor(req.headers);

        const statement = `
          MERGE INTO IDENTIFIER(:actions_table) AS target
          USING (
            SELECT
              :action_id AS action_id,
              q.alert_id,
              :decision_type AS decision_type,
              'OPEN' AS status,
              :assignee AS assignee,
              :notes AS notes,
              q.priority,
              q.taxpayer_id,
              q.taxpayer_name,
              q.ruc,
              q.risk_score,
              :actor AS created_by,
              current_timestamp() AS created_at,
              timestampadd(HOUR, :sla_hours, current_timestamp()) AS due_at,
              current_timestamp() AS updated_at
            FROM IDENTIFIER(:queue_table) q
            WHERE q.alert_id = :alert_id
          ) AS source
          ON target.alert_id = source.alert_id
             AND target.status IN ('OPEN', 'IN_PROGRESS')
          WHEN MATCHED THEN UPDATE SET
            target.action_id = source.action_id,
            target.decision_type = source.decision_type,
            target.status = source.status,
            target.assignee = source.assignee,
            target.notes = source.notes,
            target.priority = source.priority,
            target.taxpayer_id = source.taxpayer_id,
            target.taxpayer_name = source.taxpayer_name,
            target.ruc = source.ruc,
            target.risk_score = source.risk_score,
            target.created_by = source.created_by,
            target.created_at = source.created_at,
            target.due_at = source.due_at,
            target.updated_at = source.updated_at
          WHEN NOT MATCHED THEN INSERT (
            action_id, alert_id, decision_type, status, assignee, notes,
            priority, taxpayer_id, taxpayer_name, ruc, risk_score,
            created_by, created_at, due_at, updated_at
          ) VALUES (
            source.action_id, source.alert_id, source.decision_type,
            source.status, source.assignee, source.notes, source.priority,
            source.taxpayer_id, source.taxpayer_name, source.ruc,
            source.risk_score, source.created_by, source.created_at,
            source.due_at, source.updated_at
          )
        `;

        await appkit.analytics.query(statement, {
          actions_table: sql.string(actionsTable),
          queue_table: sql.string(queueTable),
          action_id: sql.string(actionId),
          alert_id: sql.string(parsed.data.alertId),
          decision_type: sql.string(parsed.data.decisionType),
          assignee: sql.string(parsed.data.assignee),
          notes: sql.string(parsed.data.notes),
          actor: sql.string(actor),
          sla_hours: sql.int(slaHours(parsed.data.decisionType)),
        });

        res.status(201).json({
          actionId,
          status: 'OPEN',
          message:
            'Decisión registrada. La tarea ya está disponible para seguimiento y para Genie.',
        });
      } catch (error) {
        console.error('[radar-tributario] Failed to create action', error);
        res.status(500).json({
          error:
            'No fue posible registrar la decisión. Verifica warehouse y permisos MODIFY.',
        });
      }
    });

    app.patch('/api/actions/:actionId', async (req, res) => {
      const actionId = z.string().uuid().safeParse(req.params.actionId);
      const body = UpdateStatusBody.safeParse(req.body);
      if (!actionId.success || !body.success) {
        res.status(400).json({ error: 'Acción o estado inválido.' });
        return;
      }

      try {
        const actionsTable = requiredTable('OPS_ACTIONS_TABLE');
        const statement = `
          UPDATE IDENTIFIER(:actions_table)
          SET status = :status, updated_at = current_timestamp()
          WHERE action_id = :action_id
        `;
        await appkit.analytics.query(statement, {
          actions_table: sql.string(actionsTable),
          action_id: sql.string(actionId.data),
          status: sql.string(body.data.status),
        });
        res.json({ actionId: actionId.data, status: body.data.status });
      } catch (error) {
        console.error('[radar-tributario] Failed to update action', error);
        res.status(500).json({ error: 'No fue posible actualizar la tarea.' });
      }
    });
  });
}
