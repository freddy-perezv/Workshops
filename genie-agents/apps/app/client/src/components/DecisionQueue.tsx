import { ArrowUpRight, Filter, ScanSearch } from 'lucide-react';
import type { AlertRow, Priority } from '../types';

interface DecisionQueueProps {
  alerts: AlertRow[];
  priority: Priority | 'ALL';
  onPriorityChange: (priority: Priority | 'ALL') => void;
  onSelect: (alert: AlertRow) => void;
}

const money = new Intl.NumberFormat('es-419', {
  style: 'currency',
  currency: 'PEN',
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
          <p className="eyebrow">Triage tributario</p>
          <h2>Contribuyentes priorizados</h2>
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
          <span>Contribuyente / señal</span>
          <span>Segmento / región</span>
          <span>Score</span>
          <span>Brecha de ventas</span>
          <span aria-hidden="true" />
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">
            No existen señales de riesgo para esta prioridad.
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
                  <strong>{alert.taxpayer_name}</strong>
                  <small>
                    RUC {alert.ruc} · {alert.primary_signal}
                  </small>
                </span>
              </span>
              <span>
                <strong>{alert.segment}</strong>
                <small>{alert.region} · {alert.economic_activity}</small>
              </span>
              <span>
                <strong>{Number(alert.risk_score).toFixed(0)} / 100</strong>
                <small className="inline-detail">
                  <ScanSearch size={12} /> {alert.signal_count} señales
                </small>
              </span>
              <span>
                <strong>{money.format(Number(alert.sales_gap))}</strong>
                <small>
                  Terceros {money.format(Number(alert.third_party_sales))}
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
