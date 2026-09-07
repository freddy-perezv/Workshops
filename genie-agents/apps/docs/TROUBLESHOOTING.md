# Troubleshooting

## Unity Catalog

### No puede crear el catálogo

**Síntoma:** `PERMISSION_DENIED` en `CREATE CATALOG`.

**Acción:** utilizar un catálogo creado por el administrador, seleccionar
`create_catalog=false` y confirmar `USE CATALOG` + `CREATE SCHEMA`.

### No puede crear el volume

Confirmar `CREATE VOLUME` sobre `bronze`. Para external volumes también se
requiere acceso a la external location; el laboratorio utiliza managed volume.

## Notebooks

### La escala M o L tarda demasiado

- Confirmar que el cluster tiene workers activos.
- Utilizar Photon.
- Cambiar temporalmente a escala `S`.
- Ejecutar Notebook 03 con `optimize_tables=false`.

No reduzcas filas modificando el código a mitad del pipeline: vuelve a ejecutar
Notebook 00 con la escala deseada y después Notebook 01.

### Falla `CREATE VIEW ... WITH METRICS`

La versión del runtime o SQL warehouse no soporta la sintaxis requerida.
Actualizar al runtime LTS acordado. Como contingencia, comentar únicamente la
celda de metric view y utilizar `gold.sales_daily`; la experiencia pierde
semántica certificada, pero el resto puede continuar.

### Las métricas de calidad están vacías

Verificar que Notebook 01 terminó y que `bronze.sales_events` contiene errores.
La columna `invalid_store` de la validación debe ser mayor que cero.

### La cuarentena supera ampliamente lo esperado

Validar que el código de provincia no fue modificado. La provincia reportada
está diseñada para coincidir con la provincia maestra, salvo errores
intencionales.

## Genie

### Genie no ve una tabla

Confirmar:

- `USE CATALOG`.
- `USE SCHEMA` en `gold`.
- `SELECT` sobre el activo.
- El SQL warehouse asociado está encendido o puede iniciar.

### Genie confunde moneda o margen

Verificar que se copiaron las instrucciones completas y que la metric view está
agregada al Space. Registrar Q01 y Q09 de `verified-queries.sql`.

### Genie intenta escribir

No ejecutar SQL sugerido. Copiar la sección “Decisiones y seguridad” de
`instructions.md` y repetir E13. La escritura debe ocurrir solo desde la App.

## Databricks App

### La App inicia pero no carga KPIs

Confirmar recursos y variables:

- `DATABRICKS_WAREHOUSE_ID`
- `GOLD_QUEUE_TABLE`
- `GOLD_METRIC_VIEW`
- `OPS_ACTIONS_TABLE`

Los nombres de tabla deben tener exactamente tres partes.

### Error de permisos al consultar

La App necesita:

- `CAN_USE` en el warehouse.
- `SELECT` en queue, metric view y actions.
- `USE CATALOG` y `USE SCHEMA` en los padres.

### Error de permisos al confirmar una decisión

Agregar `MODIFY` sobre `ops.action_tasks` al service principal de la App. No
conceder `MODIFY` sobre las tablas Gold.

### La acción no aparece inmediatamente

Esperar a que termine la escritura y volver a cargar la consulta de tareas. Si
el warehouse estaba detenido, el primer acceso puede incluir cold start.

### Genie no se renderiza dentro de la App

- Confirmar recurso Genie con `CAN_RUN`.
- Confirmar `DATABRICKS_GENIE_SPACE_ID`.
- Confirmar scope `dashboards.genie`.
- Verificar que el alias del plugin y del componente sea `pulso-retail`.

## Contingencia del workshop

Mantener preparados:

1. Un catálogo escala `S` completamente materializado.
2. Un Genie Space de respaldo.
3. Una App desplegada de respaldo.
4. Capturas de KPIs, cola, confirmación y tarea.

La contingencia permite explicar un paso que falle sin convertir la sesión en
resolución de permisos.
