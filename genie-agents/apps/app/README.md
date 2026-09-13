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

| Modo | Comando | Conexión a Databricks | Uso |
| --- | --- | --- | --- |
| Mock local | `npm run dev:mock` | No | Opcional — revisar UI sin backend real |
| Desarrollo conectado | `npm run dev` | Sí (`.env`) | Solo desarrollo local |
| **Asset Bundle (workshop)** | **`bundle deploy` + `bundle run`** | **Sí (CLI en tu laptop)** | **Camino del lab** |

> **En el workshop se usa el Asset Bundle.** `.env` no despliega. El login del
> navegador (workspace) no autentica el CLI. Los comandos se corren en la
> **terminal de tu máquina**, no en una notebook ni en Genie.

El CLI local **no ve** la carpeta Git del workspace de Databricks. O usas el
clone en tu laptop, o en la UI de Apps apuntas a la carpeta `app/` del
workspace. No hay un `cd` a `/Workspace/...` desde Terminal.app.

---

## Despliegue con Asset Bundle (camino del workshop)

Prerrequisito: [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
instalado. Comprueba:

```bash
databricks -v
```

Todos los comandos se ejecutan **en la terminal de tu laptop**, desde la
carpeta `app/` (donde está `databricks.yml`). Ejemplo desde la raíz del repo:

```bash
cd genie-agents/apps/app
pwd
ls databricks.yml
```

En esta máquina la ruta completa es:

`/Users/<tu-usuario>/.../Workshops/Repository/genie-agents/apps/app`

Si aparece `unable to locate bundle root: databricks.yml not found`, no sigas:
estás en otra carpeta (raíz del repo, `apps/` o el Git folder de Databricks).

**Perfil del CLI:** si `auth login` o `bundle validate` pide `--profile`, o
aparece `Multiple profiles match host`, agrega `--profile <nombre>` a **todos**
los comandos de abajo (`validate`, `deploy`, `run`). El nombre sale en el
error (por ejemplo `ey-chile-demo`). No uses `databricks auth env` (deprecado).

### Paso 1 — Autenticar el CLI

El host es la URL de tu workspace **tal cual en la barra del navegador**,
incluido `.net` si aplica. No asumas Azure: copia la URL real, sin `/genie/`
ni otras rutas.

```bash
databricks auth login --host https://<tu-workspace>
```

Si pregunta **Databricks profile name**, pulsa **Enter** (deja el default) o
escribe un nombre corto (`pulso`). No escribas ahí otros comandos: si pegas
`databricks current-user me` como nombre de perfil, vas a crear un perfil
basura y luego `Multiple profiles match host`.

Verifica con:

```bash
databricks current-user me
```

(`databricks auth env` está deprecado; no lo uses.)

Si `bundle validate` dice **Multiple profiles match host**, elige uno:

```bash
databricks bundle validate --profile <nombre-del-perfil>
```

y usa el mismo `--profile` en `deploy` y `run`.

### Paso 2 — Completar `databricks.yml`

Edita **solo el bloque de abajo**, `targets:` → `dev:`. No toques los
`${var....}` de la sección `resources`.

| Variable | Dónde encontrarla |
| --- | --- |
| `workspace.host` | URL del workspace (completa, sin typo: `.net` no `.ne`) |
| `sql_warehouse_id` | SQL Warehouses → el warehouse → ID en la URL (`/sql/warehouses/<id>`), no el nombre |
| `genie_space_id` | Genie **con instrucciones y tablas del lab** → ID en `/genie/rooms/<id>` |
| `catalog_name` | Catálogo de las notebooks 00–04. Aunque no diga `REPLACE`, cámbialo si no es el tuyo |
| `app_name` | Nombre de la App: **2–30 caracteres**, minúsculas y guiones, **único** en el workspace |

El nombre **no** puede ser `pulso-retail-` + tu correo: Databricks rechaza más
de 30 caracteres (`pulso-retail-freddyalan_perezvelazquez` falla). Usa algo
corto: `pulso-eq01`, `pulso-ana`, `pulso-retail-fpv`.

El Genie Space debe ser el que tiene contexto del workshop, no uno vacío. El
`genie_space_name` de más arriba puede quedar; manda el **ID**.

No subas `.env` ni tokens a git. Cada participante rellena sus IDs **en su
copia local** de `databricks.yml`; en el repo deben quedar los
`REPLACE_WITH_...`, no host ni warehouse de un workspace real.

### Paso 3 — Validar

Siempre desde `app/`:

```bash
databricks bundle validate
# si hace falta: databricks bundle validate --profile <nombre>
```

Corrige YAML, host o referencias antes de continuar. Si el host está
truncado (`.ne` en lugar de `.net`) o faltan `REPLACE_WITH_...`, el CLI falla
aquí.

### Paso 4 — Crear la App y los recursos

```bash
databricks bundle deploy
# si hace falta: databricks bundle deploy --profile <nombre>
```

Esto crea (o actualiza) la App, sube archivos al workspace
(`.bundle/.../files`) y asigna warehouse, Genie y tablas.

**Todavía no está lista para usarse.** En Apps vas a ver el nombre de
`app_name`, recursos a la derecha, compute a veces **Active**, y a la vez:

- App status **Unavailable**
- **No source code**
- **No active deployment**

Eso es normal. `deploy` armó el cascarón; falta publicar el código.

### Paso 5 — Publicar el código (el paso que faltaba en el runbook)

Sigue en `app/`:

```bash
databricks bundle run pulso_retail
# si hace falta: databricks bundle run pulso_retail --profile <nombre>
```

`pulso_retail` es la clave del recurso en el YAML, **no** el `app_name`.

Si cambias código de la App (`App.tsx`, `app.yaml`, etc.) después de un
deploy, vuelve a correr **Paso 4 y Paso 5**. Un `deploy` solo no actualiza
la experiencia que ya está Running.

El primer arranque tarda varios minutos (`npm install` / build). Espera a
**Running**, no solo compute Active.

**Alternativa en la UI** (si no usas `bundle run`): en la App, botón
**Deploy**. Esa pantalla **no ve tu Mac**. Elige una carpeta del
**workspace** que contenga `app.yaml`, por ejemplo:

`/Workspace/Users/<tu-usuario>/Workshops/genie-agents/apps/app`

No elijas la raíz del repo. GitHub solo sincroniza; Apps quiere un path de
Workspace.

### Paso 6 — Abrir y comprobar

Workspace → **Apps** → el valor de `app_name` (en `mode: development` puede
aparecer con prefijo `[dev ...]`). Abre la URL cuando el status sea Running.

Deberías ver:

- **KPIs** — ingreso, margen, unidades, ingreso en riesgo.
- **Cola de alertas** — filtrada por prioridad, con evidencia por alerta.
- **Genie** — panel de conversación embebido (multi-turn).
- **Write-back** — acciones que insertan en `<catalog>.ops.action_tasks`.
- **Seguimiento** — tareas que se pueden completar.

Si la App abre pero no hay datos, ve a troubleshooting.

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

No uses aliases de la UI (`table`, `table-2`, `table-3`): el bundle no los
crea y la App muestra *No se pudo leer la configuración* aunque Genie esté
en línea. No edites esos `valueFrom` en el workshop; solo `catalog_name` y
los IDs del bloque `targets`.

---

## Si algo falla

Los permisos están en `databricks.yml` →
`resources.apps.pulso_retail.resources` (cada ítem trae `permission:`). No
busques `resources.apps.*.permissions` ni `*.config`: en este repo no existen.

| Recurso | Permiso requerido |
| --- | --- |
| SQL Warehouse | `CAN_USE` |
| Genie Space | `CAN_RUN` |
| `gold.decision_queue` | `SELECT` |
| `gold.retail_performance_metrics` | `SELECT` |
| `ops.action_tasks` | `SELECT` + `MODIFY` |

Problemas frecuentes:

- **`databricks.yml not found`** → el comando no se corrió desde `app/`.
- **`cannot configure default credentials`** → falta `auth login` contra el
  **mismo** host (completo). El Chrome logueado no alcanza.
- **`Multiple profiles match host`** → agrega `--profile <nombre>`.
- **App name must be between 2 and 30 characters** → acorta `app_name`.
- **Unavailable / No source code** → corriste `bundle deploy` pero no
  `bundle run` (ni Deploy en la UI sobre la carpeta `app/`).
- **No se pudo leer la configuración** (Genie en línea, KPIs vacíos) →
  `app.yaml` `valueFrom` no coincide con los `name` del bundle. Tienen que
  ser `queue-table`, `metric-view`, `actions-table-read`, no `table` /
  `table-2`. Después: `bundle deploy` + `bundle run` otra vez.
- **Genie no aparece embebido** → `genie_space_id` correcto y scope
  `dashboards.genie`.
- **Warehouse no responde** → warehouse encendido; el valor es el **ID**, no
  el nombre.
- **Host metadata / URL rara** → revisa que `workspace.host` no esté
  truncado (`.ne` en lugar de `.net`).

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
