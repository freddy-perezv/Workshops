# Laboratorio 2 · Databricks App — Runbook de despliegue

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

---

## Tres modos de ejecución

| Modo | Acción / comando | Conexión a Databricks | Uso |
| --- | --- | --- | --- |
| **UI de Apps + Git folder (workshop)** | **Workspace → Apps → Create → Deploy** | **Sí (navegador)** | **Camino del lab** |
| Asset Bundle (CLI) | `bundle deploy` + `bundle run` | Sí (CLI en tu laptop) | Alternativa si ya tienes CLI |
| Mock local | `npm run dev:mock` | No | Opcional — revisar UI sin backend |
| Desarrollo conectado | `npm run dev` | Sí (`.env`) | Solo desarrollo local |

> **En el workshop se usa la UI de Apps.** No necesitas Databricks CLI, terminal
> de laptop ni editar `databricks.yml`. El login del navegador (workspace) es
> suficiente. El código debe estar en el workspace (Git folder / Repos).

---

## Despliegue por UI de Apps (camino del workshop)

No necesitas Databricks CLI, terminal de laptop ni editar `databricks.yml`.
El login del navegador (workspace) es suficiente.

### Paso 1 — Prerrequisitos

Antes de crear la App, verifica que todo esté en su sitio:

- Notebooks 00–03 ejecutadas con **tu catálogo**.
- Tablas existentes:
  - `<catalogo>.gold.decision_queue`
  - `<catalogo>.gold.retail_performance_metrics`
  - `<catalogo>.ops.action_tasks`
- Lab 1 completado: Genie Space configurado con esas tablas e instrucciones
  (no un space vacío).
- SQL warehouse encendido, con permiso `CAN_USE`.
- Código del repositorio disponible en el workspace (Git folder / Repos).

Anota estos datos; los necesitarás al crear la App:

| Dato | Dónde encontrarlo |
| --- | --- |
| Nombre de catálogo | El catálogo que usaste en las notebooks 00–03 |
| ID del warehouse | SQL Warehouses → tu warehouse → ID en la URL `/sql/warehouses/<id>` (no el nombre) |
| ID del Genie Space | Genie → el space del Lab 1 → ID en la URL `/genie/rooms/<id>` |
| Nombre de la App | Un nombre corto que cumpla las reglas del paso 2 |

### Paso 2 — Nombre de la App

- **2–30 caracteres**, solo minúsculas y guiones.
- **Único** en el workspace.
- No uses tu correo (supera 30 caracteres). Ejemplos: `pulso-ana`,
  `pulso-eq01`, `pulso-retail-fpv`.

### Paso 3 — Crear la App

1. En el workspace: **Apps** → **Create App**.
2. Selecciona **Custom** / from code.
3. Asigna el nombre elegido en el paso 2.

No cierres la pantalla: a continuación vas a agregar los recursos.

### Paso 4 — Resources

Aquí se conecta la App con el warehouse, Genie y las tablas. Esto **sustituye**
editar `databricks.yml` (que no se toca en este camino).

> **Importante:** el **nombre** (alias) de cada recurso en la UI **debe**
> coincidir letra por letra con el `valueFrom` declarado en `app.yaml`. Si la
> UI propone nombres genéricos (`table`, `table-2`, …), **renómbralos**. Si no
> coinciden, la App abre pero muestra *“No se pudo leer la configuración”*.

| Nombre del recurso (alias) | Tipo | Qué seleccionar | Permiso |
| --- | --- | --- | --- |
| `sql-warehouse` | SQL warehouse | El warehouse del lab | `CAN_USE` |
| `genie-space` | Genie Space | El space del Lab 1 | `CAN_RUN` |
| `queue-table` | Tabla UC | `<catalogo>.gold.decision_queue` | `SELECT` |
| `metric-view` | Tabla UC | `<catalogo>.gold.retail_performance_metrics` | `SELECT` |
| `actions-table-read` | Tabla UC | `<catalogo>.ops.action_tasks` | `SELECT` |
| `actions-table-write` | Tabla UC | La **misma** `<catalogo>.ops.action_tasks` | `MODIFY` |

Las tablas Gold/ops se llaman igual para todos los equipos; lo único que cambia
es el catálogo.

Si la UI muestra **User authorization / scopes**, activa **Genie**
(`dashboards.genie`). Sin esto el chat embebido no autentica.

### Paso 5 — Deploy

1. Botón **Deploy**.
2. La UI pide un path de workspace. Elige la carpeta que contiene `app.yaml`,
   por ejemplo:

   `/Workspace/Users/<tu-usuario>/Workshops/genie-agents/apps/app`

   **No** elijas la raíz del repo (`genie-agents/`) ni `apps/`. La carpeta
   correcta es `app/`.

3. Espera a que el status cambie a **Running** (tarda varios minutos en el
   primer arranque: `npm install` + build). **Compute Active no alcanza**;
   la App necesita estar en Running.

### Paso 6 — Comprobar

Abre la URL de la App cuando el status sea **Running**. Deberías ver:

- **KPIs** — ingreso, margen, unidades, ingreso en riesgo.
- **Cola de alertas** — filtrada por prioridad, con evidencia por alerta.
- **Genie** — panel de conversación embebido (multi-turn).
- **Write-back** — selecciona una alerta, elige acción, asigna responsable.
  La tarea debe aparecer en seguimiento.

Si Genie responde pero los KPIs están vacíos: los alias de los recursos no
coinciden con los `valueFrom` de `app.yaml` (ver tabla del paso 4).

### Qué NO hacer en este camino

- **No** instalar Databricks CLI ni correr `bundle deploy` / `bundle run`.
- **No** editar `databricks.yml` ni los `REPLACE_WITH_...`.
- **No** crear `.env`.
- **No** cambiar los `valueFrom` de `app.yaml`.
- **No** hacer Deploy sobre la raíz del repo (debe ser la carpeta `app/`).

---

## Alternativa: CLI / Asset Bundle

> Solo si ya tienes Databricks CLI en tu laptop y prefieres línea de comandos.
> Si seguiste el camino por UI de Apps, salta esta sección.

Prerrequisito: [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
instalado (`databricks -v`). Todos los comandos se ejecutan **en la terminal
de tu laptop**, desde la carpeta `app/` (donde está `databricks.yml`).

**1. Autenticar**

```bash
databricks auth login --host https://<tu-workspace>
databricks current-user me
```

Si aparece **Multiple profiles match host**, agrega `--profile <nombre>` a
todos los comandos siguientes.

**2. Editar `targets.dev` en `databricks.yml`**

Completa solo el bloque `targets:` → `dev:`. No toques los `${var....}` de
`resources`.

| Variable | Dónde encontrarla |
| --- | --- |
| `workspace.host` | URL del workspace (completa, incluido `.net`) |
| `sql_warehouse_id` | ID del warehouse (URL `/sql/warehouses/<id>`) |
| `genie_space_id` | ID del Genie Space (URL `/genie/rooms/<id>`) |
| `catalog_name` | Catálogo de las notebooks 00–04 |
| `app_name` | Nombre corto (2–30 caracteres, minúsculas y guiones) |

**3. Validar, deployar, publicar**

```bash
databricks bundle validate
databricks bundle deploy
databricks bundle run pulso_retail
```

`pulso_retail` es la clave del recurso en el YAML, **no** el `app_name`.
Si cambias código después del deploy, repite `bundle deploy` + `bundle run`.
El primer arranque tarda varios minutos. Si aparece `--profile`, úsalo en los
tres comandos.

### Cómo se conectan `app.yaml` y `databricks.yml`

`valueFrom` **no es el nombre de la tabla** en Unity Catalog. Es el `name` del
recurso declarado en el bundle. Databricks inyecta el valor real (ID de
warehouse, ID de Genie, o `catalog.schema.tabla`) en la variable de entorno.

Las tablas Gold/`ops` **sí se llaman igual para todos** (`gold.decision_queue`,
etc.). Lo único que cambia por equipo es `catalog_name` en `targets.dev`.

| Variable de entorno (`app.yaml`) | `valueFrom` (alias) | Recurso en `databricks.yml` | Valor que termina usando la App |
| --- | --- | --- | --- |
| `DATABRICKS_WAREHOUSE_ID` | `sql-warehouse` | `sql_warehouse.id` | ID del warehouse |
| `DATABRICKS_GENIE_SPACE_ID` | `genie-space` | `genie_space.space_id` | ID del Space |
| `GOLD_QUEUE_TABLE` | `queue-table` | `${catalog}.gold.decision_queue` | Nombre UC de 3 partes |
| `GOLD_METRIC_VIEW` | `metric-view` | `${catalog}.gold.retail_performance_metrics` | Nombre UC de 3 partes |
| `OPS_ACTIONS_TABLE` | `actions-table-read` | `${catalog}.ops.action_tasks` | Nombre UC de 3 partes |

No uses aliases genéricos de la UI (`table`, `table-2`, `table-3`): ni el
bundle ni la App los reconocen, y la App muestra *No se pudo leer la
configuración*.

---

## Si algo falla

| Recurso | Permiso requerido |
| --- | --- |
| SQL Warehouse | `CAN_USE` |
| Genie Space | `CAN_RUN` |
| `gold.decision_queue` | `SELECT` |
| `gold.retail_performance_metrics` | `SELECT` |
| `ops.action_tasks` | `SELECT` + `MODIFY` |

Si usaste la **UI de Apps**, los permisos se asignan en los recursos del
paso 4. Si usaste **CLI / Asset Bundle**, están en `databricks.yml` →
`resources.apps.pulso_retail.resources`.

Problemas frecuentes:

- **App Unavailable / No source code** → no se hizo Deploy. En la UI: botón
  Deploy sobre la carpeta `app/` con `app.yaml` y recursos bien aliasados.
  En CLI: falta `bundle run pulso_retail` después de `bundle deploy`.
- **No se pudo leer la configuración** (Genie en línea, KPIs vacíos) →
  los nombres (alias) de los recursos no coinciden con los `valueFrom` de
  `app.yaml`. Deben ser `sql-warehouse`, `genie-space`, `queue-table`,
  `metric-view`, `actions-table-read`, `actions-table-write` — no `table` /
  `table-2`. Corrige los alias y vuelve a hacer Deploy.
- **Genie no aparece embebido** → verifica que el ID del Genie Space sea
  correcto y que el scope `dashboards.genie` esté activo.
- **Warehouse no responde** → verifica que esté encendido y que el recurso
  use el **ID** (no el nombre).
- **App name must be between 2 and 30 characters** → acorta el nombre.
- **(Solo CLI) `databricks.yml not found`** → el comando no se corrió desde
  `app/`.
- **(Solo CLI) `cannot configure default credentials`** → falta
  `auth login` contra el mismo host.
- **(Solo CLI) `Multiple profiles match host`** → agrega
  `--profile <nombre>`.
- **Host metadata / URL rara** → revisa que el host no esté truncado
  (`.ne` en lugar de `.net`).

Para más detalle: [`../docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md).

---

## Modos auxiliares (no son el camino del workshop)

### Mock local (opcional)

```bash
node --version   # requiere Node.js 22 o superior
npm install
npm run dev:mock
```

Abrir `http://localhost:5173`. Datos ficticios; acciones solo en memoria.

### Desarrollo conectado (solo dev local)

1. Crear `.env` a partir de `.env.example`.
2. Completar host, warehouse, Genie Space y tablas.
3. Autenticarse con Databricks CLI.
4. Ejecutar:

```bash
npm install
npm run dev
```

> **`.env` es solo para desarrollo local.** No lo uses como despliegue y no lo
> subas a git.

---

## Recursos declarados en la App

`databricks.yml` declara:

- SQL warehouse con `CAN_USE`.
- Genie Space con `CAN_RUN`.
- `gold.decision_queue` con `SELECT`.
- `gold.retail_performance_metrics` con `SELECT`.
- `ops.action_tasks` con `SELECT` y `MODIFY`.

Databricks Apps concede además `USE CATALOG` y `USE SCHEMA` para los securables
declarados.

---

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
