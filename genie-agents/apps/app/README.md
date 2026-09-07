# Laboratorio 2 · Databricks App

**Pulso Retail** es un centro de decisiones, no un dashboard con chat.

La experiencia combina:

- KPIs certificados desde una Unity Catalog Metric View.
- Cola priorizada de alertas de inventario.
- Genie Agent embebido con conversación multi-turn.
- Write-back explícito y parametrizado mediante Databricks SQL.
- Creación y seguimiento de tareas.

## Flujo del participante

1. Observa ingreso, margen, unidades e ingreso en riesgo.
2. Filtra la cola por prioridad.
3. Selecciona una alerta y revisa su evidencia.
4. Consulta a Genie para entender contexto y alternativas.
5. Elige `APPROVE_REPLENISHMENT`, `INVESTIGATE` o `DISMISS`.
6. Asigna responsable y justifica la decisión.
7. La App inserta una fila en `<catalog>.ops.action_tasks`.
8. La tarea aparece en la App y puede marcarse como completada.
9. Genie consulta `<catalog>.gold.current_actions` y cierra el ciclo.

## Seguridad del write-back

- El navegador no envía SQL.
- El backend valida el payload con Zod.
- El backend recupera prioridad, sucursal, producto y unidades desde
  `gold.decision_queue`; no confía en esos valores del cliente.
- Todos los valores se envían como parámetros tipados.
- Los nombres de tabla proceden de recursos de Databricks Apps y se validan
  como nombres UC de tres partes.
- Una alerta no recibe una segunda tarea mientras tenga otra `OPEN` o
  `IN_PROGRESS`.
- Genie solo lee y recomienda. La escritura requiere una confirmación explícita
  en la interfaz.

## Vista local para revisión

La vista local utiliza datos mock y no necesita conectarse a Databricks:

```bash
node --version # requiere Node.js 22 o superior
npm install
npm run dev:mock
```

Abrir `http://localhost:5173`. Las acciones se conservan únicamente en memoria.

## Desarrollo conectado

Después de validar y antes del despliegue:

1. Crear `.env` a partir de `.env.example`.
2. Completar host, warehouse, Genie Space y tablas.
3. Autenticarse con Databricks CLI.
4. Ejecutar:

```bash
npm install
npm run dev
```

## Recursos de la App

`databricks.yml` declara:

- SQL warehouse con `CAN_USE`.
- Genie Space con `CAN_RUN`.
- `gold.decision_queue` con `SELECT`.
- `gold.retail_performance_metrics` con `SELECT`.
- `ops.action_tasks` con `SELECT` y `MODIFY`.

Databricks Apps concede además `USE CATALOG` y `USE SCHEMA` para los securables
declarados.

## Configuración de despliegue

Antes de desplegar, reemplazar en `databricks.yml`:

- `workspace.host`
- `sql_warehouse_id`
- `genie_space_id`
- `catalog_name`

El despliegue no forma parte de la versión local. Se realizará después de la
revisión del workshop.

## Arquitectura del código

```text
app/
├── client/
│   └── src/
│       ├── components/         UI de KPIs, tendencia, Genie, cola y tareas
│       ├── App.tsx             Composición de la experiencia
│       ├── mock-data.ts        Preview local
│       └── use-workshop-data.ts
├── config/queries/             SQL parametrizado de lectura
├── server/
│   ├── routes/decision-routes.ts
│   └── server.ts
├── app.yaml
└── databricks.yml
```

## Consultas y ejecución

Las consultas en `config/queries` se ejecutan con el service principal de la
App. El backend utiliza AppKit `analytics.query()` para las mutaciones. Genie se
expone con alias `pulso-retail` y el componente `GenieChat`.

## Definición de “alto impacto”

La UI utiliza progresive disclosure:

- Primero muestra magnitud y riesgo.
- Después permite inspeccionar evidencia.
- Finalmente solicita decisión, responsable y justificación.

La operación nunca queda implícita: la pantalla confirma el `action_id` y la
tarea aparece en seguimiento.
