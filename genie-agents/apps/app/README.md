# Radar Tributario

Aplicación Databricks AppKit para un workshop de **triage de señales de riesgo
tributario**. No es un MVP de SIRE ni determina fraude: prioriza contribuyentes,
expone evidencia analítica y registra decisiones humanas auditables.

## Experiencia

- KPIs ejecutivos de ventas declaradas, impuesto determinado, crédito fiscal,
  contribuyentes de riesgo alto y exposición priorizada.
- Tendencia de 30 días de ventas declaradas e impuesto determinado.
- Cola de contribuyentes ordenada por prioridad y `risk_score`.
- Genie embebido con alias `radar-tributario`.
- Drawer de decisión con evidencia y confirmación explícita.
- Write-back parametrizado y seguimiento de tareas recientes.
- Mock local, diseño responsive y despliegue rápido en Databricks Apps.

## Contrato de datos

Recursos esperados por participante:

- Gold: `<catalog>.gold_<participant_id>.risk_queue`
- Gold Metric View: `<catalog>.gold_<participant_id>.tax_risk_metrics`
- Ops: `<catalog>.ops_<participant_id>.action_tasks`

`tax_risk_metrics` expone:

- KPIs: `declared_sales`, `assessed_tax`, `claimed_tax_credit`,
  `high_risk_taxpayers`, `exposure_amount`.
- Tendencia: `event_date`, `declared_sales`, `assessed_tax`.

`risk_queue` expone `alert_id`, `priority`, `taxpayer_id`, `taxpayer_name`,
`ruc`, `segment`, `region`, `economic_activity`, `risk_score`,
`declared_sales`, `third_party_sales`, `sales_gap`, `claimed_tax_credit`,
`credit_ratio`, `amendment_count`, `signal_count`, `primary_signal`,
`recommended_action` y `evidence_summary`.

`action_tasks` expone `action_id`, `alert_id`, `decision_type`, `status`,
`assignee`, `notes`, `priority`, `taxpayer_id`, `taxpayer_name`, `ruc`,
`risk_score`, `created_by`, `created_at`, `due_at` e `is_overdue`.

Decisiones válidas:

- `OPEN_INVESTIGATION`
- `REQUEST_CLARIFICATION`
- `DISMISS`

## Seguridad del write-back

El navegador envía únicamente `alertId`, `decisionType`, `assignee` y `notes`.
El backend valida el payload con Zod y recupera prioridad, contribuyente, RUC y
score de manera autoritativa desde `risk_queue`. Los valores SQL usan parámetros
tipados; los nombres de tabla provienen de recursos de la App y se validan como
identificadores Unity Catalog de tres partes. Una alerta mantiene como máximo
una tarea activa (`OPEN` o `IN_PROGRESS`).

## Despliegue por la UI de Databricks Apps

Crear una Custom App desde esta carpeta (`apps/app`) y asociar exactamente estos
aliases:

| Alias | Tipo | Recurso | Permiso |
| --- | --- | --- | --- |
| `sql-warehouse` | SQL warehouse | Warehouse del workshop | `CAN_USE` |
| `genie-space` | Genie Space | Space de Radar Tributario | `CAN_RUN` |
| `risk-queue` | Tabla UC | `gold_<id>.risk_queue` | `SELECT` |
| `tax-risk-metrics` | Tabla/Metric View UC | `gold_<id>.tax_risk_metrics` | `SELECT` |
| `actions-table-read` | Tabla UC | `ops_<id>.action_tasks` | `SELECT` |
| `actions-table-write` | Tabla UC | La misma `action_tasks` | `MODIFY` |

Activar el scope `dashboards.genie`. Los aliases deben coincidir con
`app.yaml`; no usar nombres automáticos como `table` o `table-2`.

Después, seleccionar **Deploy**, elegir la carpeta que contiene `app.yaml` y
esperar a que la App esté en estado **Running**.

## Despliegue con Asset Bundle

Completar las variables de `targets.dev` en `databricks.yml` y ejecutar desde
esta carpeta:

```bash
databricks bundle validate
databricks bundle deploy
databricks bundle run radar_tributario
```

## Desarrollo local

Requiere Node.js 22 o superior.

Preview sin Databricks:

```bash
npm install
npm run dev:mock
```

Desarrollo conectado:

```bash
cp .env.example .env
# completar host, IDs y nombres UC
npm install
npm run dev
```

No guardar `.env`, tokens ni secretos en git.

## Validación

```bash
npm run lint
npm run build
```

El build sincroniza AppKit antes de compilar. Las consultas parametrizadas
viven en `config/queries`; las mutaciones están en
`server/routes/decision-routes.ts`.

## Solución rápida de problemas

- **KPIs vacíos:** revisar aliases y permisos `SELECT`.
- **Genie no carga:** revisar `genie-space`, scope `dashboards.genie` y alias
  `radar-tributario`.
- **No se crea la tarea:** revisar `MODIFY` sobre `action_tasks`, warehouse y
  columnas del contrato.
- **La App no inicia:** verificar Node 22+, `app.yaml` y que el deploy apunte a
  esta carpeta, no a la raíz del repositorio.
