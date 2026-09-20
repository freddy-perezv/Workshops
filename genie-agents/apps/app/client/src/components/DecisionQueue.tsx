import { ArrowUpRight, Clock3, Filter } from 'lucide-react';
import type { AlertRow, Priority } from '../types';

interface DecisionQueueProps {
  alerts: AlertRow[];
  priority: Priority | 'ALL';
  onPriorityChange: (priority: Priority | 'ALL') => void;
  onSelect: (alert: AlertRow) => void;
}

const money = new Intl.NumberFormat('es-419', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
});

const labels: Record<Priority | 'ALL', string> = {
  ALL: 'Todas',
  CRITICAL: 'Críticas',
  HIGH: 'Altas',
  MEDIUM: 'Medias',
  LOW: 'Bajas',
};

export function DecisionQueue({
  alerts,
  priority,
  onPriorityChange,
  onSelect,
}: DecisionQueueProps) {
  return (
    <section className="panel decision-queue">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Prioridad operativa</p>
          <h2>Cola de decisiones</h2>
        </div>
        <label className="filter-select">
          <Filter size={15} />
          <select
            aria-label="Filtrar por prioridad"
            value={priority}
            onChange={(event) =>
              onPriorityChange(event.target.value as Priority | 'ALL')
            }
          >
            {Object.entries(labels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="decision-table" role="table">
        <div className="decision-table__head" role="row">
          <span>Prioridad / producto</span>
          <span>Sucursal</span>
          <span>Cobertura</span>
          <span>Ingreso en riesgo</span>
          <span aria-hidden="true" />
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">
            No existen alertas para esta prioridad.
          </div>
        ) : (
          alerts.map((alert) => (
            <button
              className="decision-row"
              key={alert.alert_id}
              onClick={() => onSelect(alert)}
              role="row"
            >
              <span className="decision-row__product">
                <i className={`priority-dot priority-dot--${alert.priority}`} />
                <span>
                  <strong>{alert.sku}</strong>
                  <small>
                    {alert.category} · {alert.priority}
                  </small>
                </span>
              </span>
              <span>
                <strong>{alert.store_name}</strong>
                <small>{alert.region}</small>
              </span>
              <span>
                <strong>{Number(alert.days_of_cover).toFixed(1)} días</strong>
                <small className="inline-detail">
                  <Clock3 size={12} /> lead time {alert.lead_time_days}d
                </small>
              </span>
              <span>
                <strong>{money.format(Number(alert.revenue_at_risk))}</strong>
                <small>
                  {Number(alert.recommended_replenishment_units).toLocaleString(
                    'es-419',
                  )}{' '}
                  unidades
                </small>
              </span>
              <span className="decision-row__open">
                <ArrowUpRight size={17} />
              </span>
            </button>
          ))
        )}
      </div>
    </section>
  );
}
