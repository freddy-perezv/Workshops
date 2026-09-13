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
| **Asset Bundle (workshop)** | **`databricks bundle deploy`** | **Sí (CLI auth)** | **Camino del lab — despliega la App en el workspace** |

> **En el workshop se usa el Asset Bundle.** Los otros dos modos son auxiliares;
> `.env` no es el mecanismo de despliegue y no debe subirse a git.

---

## Despliegue con Asset Bundle (camino del workshop)

Todos los comandos se ejecutan desde la carpeta `app/`.

### Paso 1 — Autenticarse

```bash
databricks auth login --host https://<workspace>.azuredatabricks.net
```

Verifica con:

```bash
databricks auth env --host https://<workspace>.azuredatabricks.net
```

No hace falta pegar tokens en ningún archivo. El CLI almacena la sesión de
forma segura. **No guardes credenciales en git.**

### Paso 2 — Completar `databricks.yml`

Reemplaza los siguientes placeholders:

| Variable | Dónde encontrarla |
| --- | --- |
| `workspace.host` | URL de tu workspace: `https://<workspace>.azuredatabricks.net` |
| `sql_warehouse_id` | Workspace → SQL Warehouses → selecciona el warehouse → copia el ID de la URL (`/sql/warehouses/<id>`) |
| `genie_space_id` | Workspace → Genie → abre el Space con contexto del lab → copia el ID de la URL (`/genie/rooms/<id>`) |
| `catalog_name` | El catálogo de Unity Catalog que creaste en los notebooks 00–04 (ej. `workshop_<usuario>`) |

> **Tip:** El Genie Space debe ser el que tiene las instrucciones y tablas del
> workshop, no uno vacío.

### Paso 3 — Validar

```bash
databricks bundle validate
```

Corrige cualquier error de YAML o de referencia antes de continuar.

### Paso 4 — Desplegar

```bash
databricks bundle deploy
```

El CLI empaqueta el código, crea (o actualiza) la App en el workspace y asigna
los permisos declarados en `databricks.yml`.

### Paso 5 — Abrir la App

En el workspace, ve a **Apps** en la barra lateral y busca `pulso-retail`
(o el nombre declarado en `databricks.yml`). Haz clic para abrir.

Deberías ver:

- **KPIs** — ingreso, margen, unidades, ingreso en riesgo.
- **Cola de alertas** — filtrada por prioridad, con evidencia por alerta.
- **Genie** — panel de conversación embebido (multi-turn).
- **Write-back** — botones de acción que insertan tareas en
  `<catalog>.ops.action_tasks`.
- **Seguimiento** — lista de tareas abiertas que se pueden completar.

Si la App aparece pero los datos no cargan, revisa la sección de
troubleshooting.

---

## Si algo falla

Verifica estos permisos en `databricks.yml` → `resources.apps.*.permissions` y
`resources.apps.*.config`:

| Recurso | Permiso requerido |
| --- | --- |
| SQL Warehouse | `CAN_USE` |
| Genie Space | `CAN_RUN` |
| `gold.decision_queue` | `SELECT` |
| `gold.retail_performance_metrics` | `SELECT` |
| `ops.action_tasks` | `SELECT` + `MODIFY` |

Problemas frecuentes:

- **Genie no aparece embebido** → confirma que `genie_space_id` es correcto y
  que el scope `dashboards.genie` está habilitado.
- **Error de permisos en tablas** → Databricks Apps concede `USE CATALOG` y
  `USE SCHEMA` automáticamente para los securables declarados, pero verifica que
  el catálogo y esquemas existan.
- **Warehouse no responde** → asegúrate de que el warehouse esté encendido y que
  el ID sea el correcto (no el nombre).

Para diagnósticos más detallados, consulta
[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

---

## Modos auxiliares (no son el camino del workshop)

### Mock local (opcional)

Revisa la UI sin conexión a Databricks. Los datos son ficticios y las acciones
se conservan solo en memoria.

```bash
node --version   # requiere Node.js 22 o superior
npm install
npm run dev:mock
```

Abrir `http://localhost:5173`.

### Desarrollo conectado (solo dev local)

Conecta a tu workspace desde tu máquina, útil para iterar antes de desplegar.

1. Crear `.env` a partir de `.env.example`.
2. Completar host, warehouse, Genie Space y tablas.
3. Autenticarse con Databricks CLI.
4. Ejecutar:

```bash
npm install
npm run dev
```

> **`.env` es solo para desarrollo local.** No lo uses como mecanismo de
> despliegue y no lo subas a git.

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
