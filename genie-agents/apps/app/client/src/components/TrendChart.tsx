import type { TrendRow } from '../types';

interface TrendChartProps {
  data: TrendRow[];
}

const money = new Intl.NumberFormat('es-419', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
});

export function TrendChart({ data }: TrendChartProps) {
  const width = 720;
  const height = 210;
  const padding = 18;
  const values = data.map((row) => Number(row.net_revenue));
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = Math.max(max - min, 1);
  const points = values.map((value, index) => {
    const x =
      padding + (index / Math.max(values.length - 1, 1)) * (width - padding * 2);
    const y =
      height -
      padding -
      ((value - min) / range) * (height - padding * 2);
    return { x, y, value };
  });
  const line = points.map((point) => `${point.x},${point.y}`).join(' ');
  const area = points.length
    ? `M ${points[0].x} ${height - padding} L ${points
        .map((point) => `${point.x} ${point.y}`)
        .join(' L ')} L ${points.at(-1)?.x ?? padding} ${height - padding} Z`
    : '';

  return (
    <div className="trend-chart">
      <div className="trend-chart__summary">
        <div>
          <span>Ingreso diario</span>
          <strong>{money.format(values.at(-1) ?? 0)}</strong>
        </div>
        <span className="trend-chart__period">Últimos 30 días</span>
      </div>
      {points.length === 0 ? (
        <div className="empty-state">No hay datos de tendencia.</div>
      ) : (
        <svg
          className="trend-chart__svg"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Tendencia de ingreso neto"
        >
          <defs>
            <linearGradient id="trend-fill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#5b5bd6" stopOpacity="0.34" />
              <stop offset="100%" stopColor="#5b5bd6" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={area} fill="url(#trend-fill)" />
          <polyline
            points={line}
            fill="none"
            stroke="#6565dd"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {points.map((point, index) => (
            <circle
              key={`${point.x}-${index}`}
              cx={point.x}
              cy={point.y}
              r={index === points.length - 1 ? 5 : 2}
              fill={index === points.length - 1 ? '#ffffff' : '#6565dd'}
              stroke="#6565dd"
              strokeWidth={index === points.length - 1 ? 3 : 0}
            />
          ))}
        </svg>
      )}
    </div>
  );
}
