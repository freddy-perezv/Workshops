import { useState } from 'react';
import {
  ResourceStatusIndicator,
  ResourceStatusProvider,
} from '@databricks/appkit-ui/react';
import { LayoutDashboard } from 'lucide-react';
import { ActionDrawer } from './components/ActionDrawer';
import { ActionRail } from './components/ActionRail';
import { DecisionQueue } from './components/DecisionQueue';
import { GeniePanel } from './components/GeniePanel';
import { KpiGrid } from './components/KpiGrid';
import { TrendChart } from './components/TrendChart';
import type { AlertRow, Priority } from './types';
import { useWorkshopData } from './use-workshop-data';

function WorkshopApp() {
  const [priority, setPriority] = useState<Priority | 'ALL'>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<AlertRow | null>(null);
  const data = useWorkshopData(priority);

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Navegación principal">
        <div className="brand-mark">
          <span>RT</span>
        </div>
        <nav>
          <span
            className="nav-button nav-button--active"
            aria-label="Radar tributario"
            aria-current="page"
          >
            <LayoutDashboard size={20} />
          </span>
        </nav>
        <div className="sidebar__footer">
          <span>AT</span>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div className="topbar__title">
            <div>
              <p>Radar Tributario</p>
              <span>Triage de señales de riesgo</span>
            </div>
          </div>
          <div className="topbar__actions">
            {data.mockMode && <span className="demo-badge">Vista local</span>}
            <span className="quality-badge">
              <i /> Datos certificados
            </span>
            <div className="user-chip">
              <span>{data.identity.slice(0, 2).toUpperCase()}</span>
              <div>
                <strong>{data.identity.split('@')[0]}</strong>
                <small>Analista tributario</small>
              </div>
            </div>
          </div>
        </header>

        <main>
          <section className="hero">
            <div>
              <p className="eyebrow">Priorización analítica y responsable</p>
              <h1>Del dato tributario a una revisión focalizada.</h1>
              <p>
                Identifica una señal de riesgo, contrasta evidencia con Genie y
                activa una tarea auditable. Una señal orienta el análisis; no
                afirma fraude.
              </p>
            </div>
            <div className="hero__pulse">
              <span className="pulse-ring">
                <i />
              </span>
              <div>
                <strong>Pipeline actualizado</strong>
                <small>Gold + decisiones en línea</small>
              </div>
            </div>
          </section>

          {data.error && (
            <div className="global-error">
              <strong>No se pudo cargar toda la información.</strong>
              <span>{data.error}</span>
            </div>
          )}

          <KpiGrid data={data.kpis[0]} />

          <div className="main-grid">
            <div className="main-column">
              <section className="panel trend-panel">
                <div className="panel__header">
                  <div>
                    <p className="eyebrow">Panorama de 30 días</p>
                    <h2>Ventas declaradas e impuesto</h2>
                  </div>
                  <span className="semantic-badge">Metric View</span>
                </div>
                <TrendChart data={data.trend} />
              </section>

              <DecisionQueue
                alerts={data.alerts}
                priority={priority}
                onPriorityChange={setPriority}
                onSelect={setSelectedAlert}
              />
            </div>

            <div className="insight-column">
              <GeniePanel mockMode={data.mockMode} />
              <ActionRail
                actions={data.actions}
                onUpdate={data.updateAction}
              />
            </div>
          </div>

          {data.loading && (
            <div className="loading-bar" role="status">
              Consultando el SQL warehouse…
            </div>
          )}
        </main>
      </div>

      <ActionDrawer
        alert={selectedAlert}
        defaultAssignee={data.identity}
        onClose={() => setSelectedAlert(null)}
        onSubmit={data.createAction}
      />
    </div>
  );
}

export default function App() {
  return (
    <ResourceStatusProvider>
      <ResourceStatusIndicator position="top-right" />
      <WorkshopApp />
    </ResourceStatusProvider>
  );
}
