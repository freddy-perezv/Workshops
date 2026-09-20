import {
  CircleDollarSign,
  PackageCheck,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react';
import type { KpiRow } from '../types';

interface KpiGridProps {
  data?: KpiRow;
}

const compactMoney = new Intl.NumberFormat('es-419', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
});
const integer = new Intl.NumberFormat('es-419', { maximumFractionDigits: 0 });

export function KpiGrid({ data }: KpiGridProps) {
  const kpis = [
    {
      label: 'Ingreso neto · 30d',
      value: compactMoney.format(Number(data?.net_revenue ?? 0)),
      detail: 'Datos certificados Gold',
      icon: CircleDollarSign,
      tone: 'violet',
    },
    {
      label: 'Margen bruto · 30d',
      value: compactMoney.format(Number(data?.gross_margin ?? 0)),
      detail: 'Después de costo estimado',
      icon: TrendingUp,
      tone: 'blue',
    },
    {
      label: 'Unidades vendidas',
      value: integer.format(Number(data?.units_sold ?? 0)),
      detail: 'Eventos validados',
      icon: PackageCheck,
      tone: 'green',
    },
    {
      label: 'Ingreso en riesgo',
      value: compactMoney.format(Number(data?.revenue_at_risk ?? 0)),
      detail: `${integer.format(Number(data?.critical_alerts ?? 0))} alertas críticas`,
      icon: ShieldAlert,
      tone: 'coral',
    },
  ];

  return (
    <section className="kpi-grid" aria-label="Indicadores principales">
      {kpis.map(({ label, value, detail, icon: Icon, tone }) => (
        <article className="kpi-card" key={label}>
          <div className={`kpi-card__icon kpi-card__icon--${tone}`}>
            <Icon size={19} />
          </div>
          <div className="kpi-card__body">
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{detail}</small>
          </div>
        </article>
      ))}
    </section>
  );
}
