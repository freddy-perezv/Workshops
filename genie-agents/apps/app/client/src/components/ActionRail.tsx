import { Check, CircleDot, ClockAlert, ListTodo } from 'lucide-react';
import type { ActionRow, ActionStatus } from '../types';

interface ActionRailProps {
  actions: ActionRow[];
  onUpdate: (actionId: string, status: ActionStatus) => Promise<void>;
}

function isTrue(value: boolean | string) {
  return value === true || value === 'true';
}

const decisionLabels = {
  OPEN_INVESTIGATION: 'Investigación abierta',
  REQUEST_CLARIFICATION: 'Aclaración solicitada',
  DISMISS: 'Señal descartada',
};

export function ActionRail({ actions, onUpdate }: ActionRailProps) {
  return (
    <section className="panel action-rail">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Casos con write-back</p>
          <h2>Tareas recientes</h2>
        </div>
        <ListTodo size={20} />
      </div>

      <div className="action-list">
        {actions.length === 0 ? (
          <div className="empty-state">
            Las decisiones confirmadas aparecerán aquí.
          </div>
        ) : (
          actions.slice(0, 6).map((action) => (
            <article className="action-card" key={action.action_id}>
              <div className="action-card__status">
                {isTrue(action.is_overdue) ? (
                  <ClockAlert size={15} />
                ) : (
                  <CircleDot size={15} />
                )}
                <span>{isTrue(action.is_overdue) ? 'VENCIDA' : action.status}</span>
              </div>
              <strong>{action.taxpayer_name}</strong>
              <span>
                RUC {action.ruc} · {decisionLabels[action.decision_type]}
              </span>
              <small>{action.assignee}</small>
              {action.status !== 'DONE' && action.status !== 'CANCELLED' && (
                <button
                  className="text-button"
                  onClick={() => void onUpdate(action.action_id, 'DONE')}
                >
                  <Check size={14} /> Marcar completada
                </button>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}
