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

## Apertura de la presentación (4–5 minutos)

Estas cinco diapositivas deben mostrarse antes de comenzar el workshop. Su
objetivo es presentar al instructor, dar contexto de negocio y explicar el
recorrido que seguirá el grupo antes de entrar en Databricks.

### Diapositiva 1 · Bienvenida

**Contenido en pantalla**

- **De datos a decisiones con Genie Agents + Databricks Apps**
- Workshop hands-on
- Pulso Retail Argentina

**Guion**

“Bienvenidos. Hoy vamos a recorrer un caso de negocio de extremo a extremo:
partiremos de datos operativos con problemas de calidad y terminaremos con una
decisión registrada, auditable y disponible para análisis.”

### Diapositiva 2 · Quién soy (20 segundos)

**Contenido en pantalla**

- **[Nombre y apellido]**
- [Posición o cargo] · [Rol en este workshop]
- [Empresa]
- **Algo que pocos saben de mí:** [dato atípico, personal o disruptivo]

**Guion de 20 segundos**

“Soy **[nombre]**, trabajo como **[posición]** en **[empresa]** y hoy mi rol
será acompañarlos como **[rol en el workshop]**. Para romper el hielo, algo que
muy pocos saben de mí es **[dato breve]**. Ahora sí, veamos el problema que
vamos a resolver juntos.”

> Completar los campos antes de presentar. Elegir un dato breve y apropiado
> para la audiencia: una afición inesperada, un proyecto personal, una
> experiencia poco conocida o una habilidad fuera del trabajo.

### Diapositiva 3 · El problema: vemos el quiebre demasiado tarde

**Contenido en pantalla**

- 120 sucursales y 400 productos.
- Ventas e inventario distribuidos en distintas fuentes.
- Datos con duplicados, faltantes y valores inválidos.
- Alertas tardías y priorización manual.
- Decisiones que no siempre dejan evidencia auditable.

**Mensaje central**

> El problema no es la falta de datos; es convertir datos imperfectos en una
> decisión oportuna y confiable.

**Guion**

“Pulso Retail opera 120 sucursales en Argentina. Tiene datos de ventas e
inventario, pero detecta tarde qué combinación de sucursal y producto está en
riesgo de quedarse sin stock. Además, los datos no llegan perfectos y el
equipo debe revisar señales dispersas, decidir qué atender primero y registrar
lo que hizo. Esto genera pérdida potencial de ventas, trabajo reactivo y poca
trazabilidad.”

### Diapositiva 4 · Qué buscamos resolver

**Contenido en pantalla**

- Detectar riesgo de quiebre con anticipación.
- Priorizar por cobertura, lead time e ingreso en riesgo.
- Permitir preguntas en lenguaje natural con métricas consistentes.
- Mantener control humano sobre la decisión.
- Registrar cada acción para consulta y auditoría.

**Criterio de éxito**

> Una persona identifica la alerta prioritaria, entiende por qué importa,
> toma una decisión y puede demostrar qué ocurrió.

**Guion**

“No buscamos construir solamente un dashboard ni un chatbot. Buscamos reducir
el tiempo entre una señal operativa y una acción informada. El usuario debe
poder encontrar la alerta más importante, comprender la evidencia con Genie,
confirmar una decisión desde una aplicación y dejar un registro que luego
pueda consultarse y auditarse.”

### Diapositiva 5 · Cómo lo resolveremos

**Contenido en pantalla**

1. **Gobernar:** Unity Catalog define activos, permisos y linaje.
2. **Confiar:** Bronze, Silver y cuarentena hacen visible la calidad.
3. **Priorizar:** Gold y la capa semántica traducen datos a riesgo de negocio.
4. **Comprender:** Genie responde con métricas e instrucciones verificadas.
5. **Actuar:** Databricks App registra una decisión controlada.
6. **Comunicar:** AI/BI Dashboard presenta el estado ejecutivo.

**Flujo de cierre**

> Dato → calidad → semántica → pregunta → evidencia → decisión → tarea

**Guion**

“Resolveremos el caso como un ciclo completo. Primero gobernaremos y
prepararemos los datos; después publicaremos reglas de negocio y métricas
consistentes. Genie nos ayudará a explorar y explicar la situación, pero no
tomará la decisión por nosotros. La persona confirmará la acción en una
Databricks App, la tarea quedará persistida y finalmente mostraremos el
resultado en una vista ejecutiva. Ese es el recorrido que construiremos hoy.”

**Transición al workshop**

“Con el problema, el objetivo y el recorrido claros, abramos el entorno y
comencemos por la base: datos gobernados y confiables.”

## Agenda operativa (180 minutos)

| Tiempo | Bloque | Resultado |
|---:|---|---|
| 00:00–00:10 | Bienvenida y criterio de éxito | Caso y entorno alineados |
| 00:10–00:40 | Notebooks 00–03 | UC, Bronze, Silver, Gold y semántica |
| 00:40–01:15 | Lab 1: Genie Agent | Space configurado y evaluado |
| 01:15–01:25 | Pausa | — |
| 01:25–02:10 | Lab 2: Databricks App | App conectada y acción persistida |
| 02:10–02:15 | Notebook 04: validación | Ciclo cerrado confirmado |
| 02:15–02:35 | Lab 3: AI/BI Dashboard | Vista ejecutiva generada con Genie |
| 02:35–02:50 | Evaluación y producción | Benchmark, permisos y observabilidad |
| 02:50–03:00 | Readout | Resultado, backlog y plan de 30 días |

El recorrido end-to-end no es un bloque separado: se demuestra dentro del Lab
2 con el flujo KPI → alerta → evidencia → decisión → tarea → consulta desde
Genie. Así se protege el tiempo hands-on y el dashboard cabe dentro de las tres
horas.

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

## Lab 3 · AI/BI Dashboard

Seguir `dashboard/README.md`.

### Qué decir

“La App convierte una señal en una decisión; el dashboard comunica el estado
ejecutivo. No compiten: ambos usan las mismas fuentes Gold gobernadas.”

### Recorrido de 20 minutos

1. Crear un AI/BI Dashboard y asociar el SQL warehouse.
2. Reemplazar `<catalog>` en el prompt del laboratorio.
3. Pegar el prompt en Genie y revisar los widgets propuestos.
4. Confirmar KPIs de 30 días, moneda ARS, riesgo, calidad y seguimiento.
5. Corregir la metric view con `MEASURE(...)`, nunca con `SUM(...)`.
6. Publicar o dejar listo para continuidad.

### Criterio de salida

- Solo fuentes Gold del workshop.
- Periodo y moneda explícitos.
- Ningún dataset, tabla o metric view eliminado.
- Si un widget falla, se corrige su consulta; no se inventan cifras.

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
