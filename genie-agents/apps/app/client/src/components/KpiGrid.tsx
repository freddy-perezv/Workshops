import {
  CircleDollarSign,
  ReceiptText,
  ShieldAlert,
  Landmark,
} from 'lucide-react';
import type { KpiRow } from '../types';

interface KpiGridProps {
  data?: KpiRow;
}

const compactMoney = new Intl.NumberFormat('es-419', {
  style: 'currency',
  currency: 'PEN',
  notation: 'compact',
  maximumFractionDigits: 1,
});
const integer = new Intl.NumberFormat('es-419', { maximumFractionDigits: 0 });

export function KpiGrid({ data }: KpiGridProps) {
  const kpis = [
    {
      label: 'Ventas declaradas · 30d',
      value: compactMoney.format(Number(data?.declared_sales ?? 0)),
      detail: 'Base imponible observada',
      icon: CircleDollarSign,
      tone: 'violet',
    },
    {
      label: 'Impuesto determinado',
      value: compactMoney.format(Number(data?.assessed_tax ?? 0)),
      detail: 'Acumulado últimos 30 días',
      icon: Landmark,
      tone: 'blue',
    },
    {
      label: 'Crédito fiscal declarado',
      value: compactMoney.format(Number(data?.claimed_tax_credit ?? 0)),
      detail: 'Comprobantes consolidados',
      icon: ReceiptText,
      tone: 'green',
    },
    {
      label: 'Exposición priorizada',
      value: compactMoney.format(Number(data?.exposure_amount ?? 0)),
      detail: `${integer.format(Number(data?.high_risk_taxpayers ?? 0))} contribuyentes de riesgo alto`,
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
