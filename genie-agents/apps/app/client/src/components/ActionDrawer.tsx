import { useEffect, useState, type FormEvent } from 'react';
import {
  CheckCircle2,
  ClipboardCheck,
  SearchCheck,
  ShieldX,
  X,
} from 'lucide-react';
import type { ActionInput, AlertRow, DecisionType } from '../types';

interface ActionDrawerProps {
  alert: AlertRow | null;
  defaultAssignee: string;
  onClose: () => void;
  onSubmit: (input: ActionInput) => Promise<string>;
}

const money = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0,
});

const decisionOptions: Array<{
  value: DecisionType;
  label: string;
  detail: string;
  icon: typeof ClipboardCheck;
}> = [
  {
    value: 'APPROVE_REPLENISHMENT',
    label: 'Aprobar reposición',
    detail: 'Crea tarea con SLA de 24 horas',
    icon: ClipboardCheck,
  },
  {
    value: 'INVESTIGATE',
    label: 'Solicitar investigación',
    detail: 'Crea tarea con SLA de 8 horas',
    icon: SearchCheck,
  },
  {
    value: 'DISMISS',
    label: 'Descartar alerta',
    detail: 'Registra justificación y cierra el caso',
    icon: ShieldX,
  },
];

export function ActionDrawer({
  alert,
  defaultAssignee,
  onClose,
  onSubmit,
}: ActionDrawerProps) {
  const [decisionType, setDecisionType] =
    useState<DecisionType>('APPROVE_REPLENISHMENT');
  const [assignee, setAssignee] = useState(defaultAssignee);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successId, setSuccessId] = useState<string | null>(null);

  useEffect(() => {
    if (!alert) return;
    setDecisionType(
      alert.recommended_action === 'MONITOR'
        ? 'INVESTIGATE'
        : alert.recommended_action,
    );
    setAssignee(defaultAssignee);
    setNotes('');
    setError(null);
    setSuccessId(null);
  }, [alert, defaultAssignee]);

  if (!alert) return null;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!alert) return;
    setSubmitting(true);
    setError(null);
    try {
      const actionId = await onSubmit({
        alertId: alert.alert_id,
        decisionType,
        assignee,
        notes,
      });
      setSuccessId(actionId);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'No fue posible crear la acción.',
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="drawer-backdrop" role="presentation" onMouseDown={onClose}>
      <aside
        className="action-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="action-drawer__header">
          <div>
            <span className={`priority-pill priority-pill--${alert.priority}`}>
              {alert.priority}
            </span>
            <h2 id="drawer-title">Convertir alerta en acción</h2>
            <p>
              {alert.store_name} · {alert.sku}
            </p>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Cerrar">
            <X size={20} />
          </button>
        </div>

        {successId ? (
          <div className="drawer-success">
            <CheckCircle2 size={42} />
            <h3>Decisión registrada</h3>
            <p>
              La tarea ya está disponible para seguimiento y Genie podrá
              consultarla.
            </p>
            <code>{successId}</code>
            <button className="primary-button" onClick={onClose}>
              Volver al centro de decisiones
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="alert-evidence">
              <div>
                <span>Días de cobertura</span>
                <strong>{Number(alert.days_of_cover).toFixed(1)}</strong>
              </div>
              <div>
                <span>Lead time</span>
                <strong>{alert.lead_time_days} días</strong>
              </div>
              <div>
                <span>Ingreso en riesgo</span>
                <strong>{money.format(Number(alert.revenue_at_risk))}</strong>
              </div>
              <div>
                <span>Unidades sugeridas</span>
                <strong>
                  {Number(
                    alert.recommended_replenishment_units,
                  ).toLocaleString('es-AR')}
                </strong>
              </div>
            </div>

            <fieldset className="decision-options">
              <legend>Decisión</legend>
              {decisionOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <label
                    className={
                      decisionType === option.value
                        ? 'decision-option decision-option--selected'
                        : 'decision-option'
                    }
                    key={option.value}
                  >
                    <input
                      type="radio"
                      name="decision"
                      value={option.value}
                      checked={decisionType === option.value}
                      onChange={() => setDecisionType(option.value)}
                    />
                    <Icon size={19} />
                    <span>
                      <strong>{option.label}</strong>
                      <small>{option.detail}</small>
                    </span>
                  </label>
                );
              })}
            </fieldset>

            <label className="form-field">
              <span>Responsable</span>
              <input
                type="email"
                value={assignee}
                onChange={(event) => setAssignee(event.target.value)}
                required
              />
            </label>

            <label className="form-field">
              <span>Justificación</span>
              <textarea
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                minLength={8}
                maxLength={1000}
                rows={4}
                placeholder="Describe la evidencia y el resultado esperado…"
                required
              />
            </label>

            {error && <div className="form-error">{error}</div>}

            <div className="drawer-actions">
              <button type="button" className="secondary-button" onClick={onClose}>
                Cancelar
              </button>
              <button
                type="submit"
                className="primary-button"
                disabled={submitting}
              >
                {submitting ? 'Registrando…' : 'Confirmar y crear tarea'}
              </button>
            </div>
          </form>
        )}
      </aside>
    </div>
  );
}
