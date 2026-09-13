# Laboratorio 3 · Dashboard ejecutivo generado con Genie

Tiempo objetivo: **20–25 minutos**.

> **La idea que engancha:** en el Lab 1 Genie *respondió* preguntas; en el Lab 2
> la App *ejecutó* decisiones. En el Lab 3, Genie **diseña la vista ejecutiva
> completa** a partir de una sola instrucción. El "wow" no es que haya gráficas:
> es que en menos de dos minutos alguien sin escribir SQL obtiene un tablero
> que un equipo de BI tardaría días en armar — y sobre los **mismos datos
> gobernados** que ya certificamos.

## Resultado

Un dashboard AI/BI construido **100% con Genie / lenguaje natural**, que:

- Usa las tablas Gold y la metric view del workshop (nada de datos nuevos).
- Presenta KPIs, tendencias, ranking por provincia, riesgo y calidad.
- Tiene una jerarquía visual clara, buena paleta y mini-charts.
- Puede embeberse o enlazarse desde la Databricks App como “vista ejecutiva”.

## Fuentes de datos (no inventar otras)

Reemplaza `<catalog>` por tu catálogo de las notebooks 00–04:

- `<catalog>.gold.retail_performance_metrics` — metric view certificada (ingreso neto, margen bruto, unidades).
- `<catalog>.gold.decision_queue` — alertas priorizadas e ingreso en riesgo.
- `<catalog>.gold.current_actions` — decisiones y tareas (write-back de la App).
- `<catalog>.gold.data_quality_summary` — calidad por regla.
- `<catalog>.gold.sales_daily` — detalle diario para tendencias.

## Cómo usarlo

1. En Databricks, abre **Dashboards** (AI/BI) → **Create dashboard**, o pídeselo
   a **Genie** desde el Space del Lab 1.
2. Asocia el **SQL warehouse** del workshop.
3. Pega el prompt de abajo **reemplazando `<catalog>`** por el tuyo.
4. Deja que Genie proponga los widgets; luego pídele ajustes finos en lenguaje
   natural (colores, orden, formato de moneda, agregar un mini-chart, etc.).
5. Publica y, si quieres, enlaza el dashboard desde la App como acceso directo.

> **Tip:** Genie mejora cuando el prompt define **audiencia, decisiones,
> métricas exactas, layout y estilo**. El prompt siguiente ya trae todo eso;
> ajústalo, no lo recortes.

---

## Prompt para pegar en Genie

```text
Actúa como un diseñador senior de dashboards ejecutivos de BI. Crea un
dashboard AI/BI completo, en español (Argentina), para un Responsable de
Operaciones de retail llamado "Pulso Retail · Vista Ejecutiva". El objetivo es
pasar de la señal de riesgo a la decisión en una sola pantalla, con impacto
visual inmediato.

CONTEXTO DE NEGOCIO
El negocio prioriza el riesgo de quiebre de stock por sucursal y producto en
Argentina, cuida el ingreso en riesgo y da seguimiento a decisiones auditables.
Toda cifra monetaria es en pesos argentinos (ARS) y debe mostrarse con formato
de moneda compacto (por ejemplo, ARS 2,4 MM). Los periodos son explícitos:
usa los últimos 30 días salvo que el widget indique otra cosa.

FUENTES DE DATOS (usa solo estas, no inventes tablas ni columnas)
- <catalog>.gold.retail_performance_metrics (metric view: MEASURE(net_revenue),
  MEASURE(gross_margin), MEASURE(units_sold); dimensiones: event_date, province,
  channel, category)
- <catalog>.gold.decision_queue (priority, province, store_name, sku, category,
  days_of_cover, lead_time_days, revenue_at_risk, recommended_replenishment_units)
- <catalog>.gold.current_actions (created_at, decision_type, status, assignee,
  due_at, is_overdue, priority, store_name, sku, recommended_units)
- <catalog>.gold.data_quality_summary (rule_id, rule_description, failed_rows,
  total_rows, pass_rate_pct)
- <catalog>.gold.sales_daily (detalle diario para tendencia)

LAYOUT (de arriba hacia abajo, con jerarquía visual clara)
1. Fila de 4 KPIs grandes con número principal, etiqueta y micro-tendencia
   (sparkline) de 30 días:
   - Ingreso neto (30d)
   - Margen bruto (30d)
   - Unidades vendidas (30d)
   - Ingreso en riesgo (alertas CRITICAL + HIGH)
   Cada KPI muestra variación vs. periodo anterior con color e ícono (verde
   sube, rojo baja) y un delta en porcentaje.
2. Fila central de dos columnas:
   - Izquierda: gráfico de líneas de ingreso neto y margen bruto por día
     (últimos 30 días) con área suave y leyenda clara.
   - Derecha: barras horizontales "Ingreso neto por provincia (Top 10)",
     ordenado descendente.
3. Fila de riesgo:
   - Tabla "Cola de decisiones" con las 10 alertas de mayor revenue_at_risk:
     prioridad (chip de color), sucursal, provincia, SKU, días de cobertura,
     lead time e ingreso en riesgo. Resalta CRITICAL.
   - Mapa o barras "Ingreso en riesgo por provincia" (CRITICAL + HIGH).
4. Fila de calidad y seguimiento:
   - Barras "Pass rate por regla de calidad" (rule_description, pass_rate_pct)
     con umbral visual.
   - Tarjetas/serie "Decisiones tomadas hoy" y "Tareas vencidas" desde
     current_actions (cuenta por status y is_overdue).

ESTILO Y UX/UI (busca impacto "wow", pero legible y ejecutivo)
- Paleta profesional y accesible: un color de acento para lo positivo (teal o
  azul), rojo/ámbar reservados para riesgo y alertas, gris neutro para el resto.
  Contraste AA, nada de arcoíris.
- Jerarquía tipográfica: números de KPI grandes y en negrita; etiquetas
  secundarias en tono atenuado.
- Espaciado generoso, tarjetas con esquinas redondeadas y separación consistente.
- Formatos: moneda ARS compacta, porcentajes con 1 decimal, miles con separador
  es-AR.
- Usa mini-charts (sparklines) en los KPIs y micro-indicadores de tendencia.
- Estados vacíos claros ("Sin alertas para este filtro") y sin inventar filas.
- Incluye filtros globales por provincia, categoría y rango de fechas.

REGLAS
- No ejecutes ni sugieras escrituras: el dashboard es de solo lectura.
- Usa las medidas certificadas de la metric view; no confundas margen con ingreso.
- Si un dato no existe, indícalo; no rellenes con valores ficticios.

Entrega el dashboard con los widgets ya dispuestos según el layout, títulos en
español, y deja los filtros globales aplicados. Luego propón 3 preguntas de
seguimiento que un ejecutivo haría sobre este tablero.
```

---

## Ajustes finos (pídeselos a Genie después)

- “Cambia las barras de provincia a Top 8 y ordena por ingreso en riesgo.”
- “Agrega un sparkline de unidades vendidas al KPI correspondiente.”
- “Usa ámbar para HIGH y rojo para CRITICAL en la tabla.”
- “Formatea todos los montos como ARS compacto (MM/mil).”
- “Agrega un filtro por canal y por rango de fechas.”

## Criterio de éxito

- El tablero usa **solo** las fuentes Gold del workshop.
- KPIs con periodo explícito (30 días) y moneda ARS.
- Jerarquía visual clara, paleta coherente y al menos un mini-chart.
- Riesgo (CRITICAL/HIGH) y calidad (pass rate) presentes.
- Cero cifras inventadas; estados vacíos manejados.

## Conexión con la App (opcional)

Enlaza el dashboard publicado como “Vista ejecutiva” desde la Databricks App,
o compártelo con el equipo. Así el ciclo queda completo: Genie explica (Lab 1),
la App decide y persiste (Lab 2) y el dashboard comunica el estado ejecutivo
(Lab 3), todo sobre los mismos datos gobernados.
