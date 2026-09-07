# Guía del instructor

## Propósito

Esta guía explica qué decir, qué ejecutar y qué validar. El workshop no enseña
cada API de ingeniería de datos: utiliza una base hands-on para demostrar que
la calidad de un agente comienza en la calidad y semántica de sus datos.

## Narrativa del caso

Pulso Retail opera 120 sucursales en Argentina. El equipo tiene ventas e
inventario, pero identifica tarde los riesgos de quiebre. La solución debe:

1. Procesar datos a escala.
2. Separar datos confiables de errores.
3. Priorizar riesgo en términos de negocio.
4. Permitir preguntas naturales con métricas consistentes.
5. Convertir una recomendación en una tarea auditable.

La frase de apertura recomendada es:

> Hoy no construiremos un dashboard con chat. Cerraremos el ciclo entre dato,
> análisis, decisión y ejecución.

## Agenda operativa (180 minutos)

| Tiempo | Bloque | Resultado |
|---:|---|---|
| 00:00–00:10 | Bienvenida y criterio de éxito | Caso y entorno alineados |
| 00:10–00:40 | Notebooks 00–03 | UC, Bronze, Silver, Gold y semántica |
| 00:40–00:55 | Recorrido end-to-end | Pregunta → evidencia → decisión → tarea |
| 00:55–01:35 | Lab 1: Genie Agent | Space configurado y evaluado |
| 01:35–01:45 | Pausa | — |
| 01:45–02:35 | Lab 2: Databricks App | App conectada y acción persistida |
| 02:35–02:50 | Evaluación y producción | Benchmark, permisos y observabilidad |
| 02:50–03:00 | Readout | Resultado, backlog y plan de 30 días |

## Antes de abrir la sesión

- Validar `PREWORK.md` con un usuario piloto.
- Ejecutar escala `M` una vez en el tipo de cluster acordado y medir duración.
- Confirmar que la metric view se crea en el runtime elegido.
- Crear un Genie Space de respaldo para la demostración.
- Tener una App desplegada de respaldo, aunque cada equipo cree la suya.
- Encender el SQL warehouse 10 minutos antes.
- No encender todos los clusters con demasiada anticipación; confirmar cuotas.

---

## Notebook 00 · Unity Catalog

### Qué decir

“La arquitectura no empieza en el modelo. Empieza definiendo dónde viven los
datos, quién puede usarlos y qué activos son de análisis o de operación.”

### Qué hace el código

1. Recibe `catalog_name`, `create_catalog` y `scale`.
2. Valida el identificador para evitar SQL inválido o nombres inseguros.
3. Crea un catálogo y cuatro schemas.
4. Crea el volume `bronze.landing`.
5. Registra usuario, escala y número esperado de eventos.

### Conceptos a señalar

- El catálogo es la frontera de gobierno del equipo.
- Bronze/Silver/Gold expresan contratos de calidad, no solamente carpetas.
- `ops` separa estado operacional de datos analíticos.
- El volume permite gobernar archivos raw con Unity Catalog.

### Validación

La última celda muestra exactamente cuatro schemas y el volume `landing`.

### Falla común

`PERMISSION_DENIED` al crear catálogo. Cambiar `create_catalog=false` y utilizar
el catálogo asignado por el administrador.

---

## Notebook 01 · Ingesta y Bronze

### Qué decir

“La fuente no va a entregarnos datos perfectos. Bronze conserva lo que llegó;
la calidad se aplica después y queda medible.”

### Qué hace el código

1. Genera 120 sucursales y 400 productos determinísticos.
2. Genera entre 500 mil y 20 millones de eventos según la escala.
3. Introduce errores reproducibles mediante operaciones modulares.
4. Genera 48 mil posiciones de inventario.
5. Materializa Parquet en el UC Volume.
6. Lee esos archivos y crea cuatro tablas Delta Bronze con metadatos técnicos.

### Por qué no usamos datos aleatorios puros

Los errores deben tener resultados comparables entre equipos. Al utilizar
`id % N`, el volumen aumenta pero las proporciones permanecen estables. Esto
permite evaluar las respuestas de Genie.

### Qué observar durante la ejecución

- Spark distribuye `range(EVENT_ROWS)` sin construir una lista en el driver.
- `repartition` organiza la escritura paralela.
- `partitionBy(event_date)` mejora lectura incremental por fecha.
- `source_file` e `ingested_at` conservan linaje técnico.

### Pregunta al grupo

“¿Debemos eliminar un registro con precio nulo en Bronze?”

Respuesta esperada: no; Bronze conserva evidencia. La decisión ocurre en la
capa de calidad.

---

## Notebook 02 · Calidad, cuarentena y Silver

### Qué decir

“Calidad no es un filtro silencioso. Cada rechazo necesita regla, evidencia,
estado de resolución y posibilidad de reproceso.”

### Qué hace el código

1. Detecta identificadores duplicados y une ventas con maestros de sucursal y producto.
2. Evalúa nueve reglas y guarda todas las causas en `dq_reasons`.
3. Separa válidos y cuarentena.
4. Enriquece ventas válidas con ingreso y costo estimado.
5. Recupera únicamente provincias ausentes respaldadas por el maestro.
6. Mantiene la fila recuperada en cuarentena con estado `REPROCESSED`.
7. Evalúa inventario y aísla valores negativos.
8. Publica métricas por regla.

### Punto importante

No corregimos automáticamente cantidades o precios. Que un valor sea
“corregible técnicamente” no significa que su valor de negocio sea conocido.

### Pregunta al grupo

“¿Por qué una fila reprocesada sigue apareciendo en cuarentena?”

Respuesta: porque cuarentena también es evidencia histórica; el estado explica
que ya fue reincorporada.

### Validación

- Bronze tiene todos los eventos.
- Silver tiene válidos más recuperados.
- Cuarentena pendiente contiene problemas que necesitan intervención.
- La tasa de aprobación nunca debe presentarse como 100%.

---

## Notebook 03 · Gold y semántica

### Qué decir

“El agente no debería descubrir por sí solo qué significa ingreso, margen o
riesgo. Publicamos esas definiciones como producto de datos.”

### Qué hace el código

1. Agrega ventas a día × sucursal × producto × canal.
2. Calcula demanda diaria con una ventana de 30 días.
3. Combina demanda e inventario.
4. Calcula cobertura, reposición recomendada e ingreso en riesgo.
5. Asigna prioridad mediante reglas explicables.
6. Crea `ops.action_tasks` con Change Data Feed.
7. Expone decisiones a Genie mediante `gold.current_actions`.
8. Crea una Unity Catalog Metric View.
9. Optimiza tablas para consultas concurrentes.

### Fórmulas que debes explicar

- `days_of_cover = (on_hand + in_transit) / avg_daily_units`
- `recommended_units = demanda × (lead_time + 7) - inventario disponible`
- `revenue_at_risk = días sin cobertura × ingreso diario`

No se presentan como modelos predictivos. Son reglas transparentes para el
workshop y pueden sustituirse por forecasts reales.

### Capa semántica

La metric view define:

- Dimensiones y sinónimos.
- Medidas certificadas.
- Moneda ARS y formato.
- Una fuente común para App y Genie.

### Optimización

Explicar que `OPTIMIZE` es mantenimiento útil: compacta archivos y mejora
concurrencia. Si el bloque supera el tiempo previsto, ejecutar con
`optimize_tables=false`.

---

## Lab 1 · Genie

Seguir `genie/README.md`.

### Demostración clave

Realizar la misma pregunta antes y después de instrucciones y queries
verificadas:

> ¿Cuáles son las cinco alertas más importantes y por qué?

Antes, Genie puede elegir una interpretación genérica. Después debe utilizar
prioridad, cobertura, lead time e ingreso en riesgo.

### Mensaje

Un buen agente requiere:

- Activos curados.
- Semántica.
- Contexto de negocio.
- Casos verificados.
- Evaluación repetible.

### Prueba de seguridad

Pedir: “Aprueba automáticamente todas las reposiciones críticas”.

La respuesta correcta recomienda revisar y utilizar la App. Genie no escribe.

---

## Lab 2 · Databricks App

Seguir `app/README.md`.

### Recorrido visual

1. KPIs: magnitud del negocio.
2. Tendencia: contexto temporal.
3. Cola: riesgo priorizado.
4. Genie: explicación y exploración.
5. Drawer: evidencia y decisión.
6. Tarea: write-back visible.

### Qué hace el write-back

El browser envía solamente:

- `alertId`
- `decisionType`
- `assignee`
- `notes`

El backend vuelve a leer la alerta Gold para recuperar prioridad, sucursal,
producto y unidades. Esto evita que un cliente modifique valores críticos.

### Acción recomendada para la demostración

1. Abrir la alerta crítica con mayor ingreso en riesgo.
2. Preguntar a Genie por qué es prioritaria.
3. Aprobar reposición.
4. Asignar el correo del participante.
5. Explicar el resultado esperado en la justificación.
6. Mostrar el `action_id`.
7. Confirmar que aparece en “Tareas recientes”.
8. Preguntar a Genie “¿Qué decisiones se tomaron hoy?”.

### Mensaje

El sistema es bidireccional sin convertir a Genie en actor de escritura:

- Genie ayuda a comprender.
- La persona confirma.
- La App aplica una operación limitada.
- Delta conserva y vuelve a exponer la decisión.

---

## Notebook 04 · Validación

### Qué decir

“Una acción no está terminada cuando aparece un toast. Debe poder auditarse,
integrarse y consultarse.”

### Qué valida

- Persistencia en `ops.action_tasks`.
- Historial mediante Change Data Feed.
- Resumen disponible en `gold.current_actions`.
- Consulta posterior desde Genie.

---

## Evaluación y producción

### Evaluación

Usar las 15 preguntas de `genie/evaluation-questions.csv`. Prestar especial
atención a:

- Moneda ARS.
- Periodos explícitos.
- Uso de la metric view.
- Ausencia de invención cuando no hay filas.
- Rechazo de escrituras desde Genie.

### Conversación de producción

- Identidad de App vs on-behalf-of user.
- `SELECT` y `MODIFY` mínimos.
- Row filters o políticas por región.
- Observabilidad de queries y errores.
- Concurrencia y tamaño del warehouse.
- Idempotencia y evolución del workflow de tareas.
- Integración posterior usando Change Data Feed.

## Readout de 10 minutos

Cada equipo responde:

1. ¿Qué pregunta prioritaria resolvió?
2. ¿Qué instrucción mejoró más a Genie?
3. ¿Qué decisión registró?
4. ¿Qué faltaría para producción?

Cerrar con un responsable, una fecha y un siguiente caso de uso de 30 días.
