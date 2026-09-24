# Dashboard AI/BI · Radar Tributario

El dashboard complementa la App: muestra patrones agregados para gestión y
gobierno. **No replica la cola operativa**, no lista RUC ni contribuyentes y no
permite decidir casos individuales.

> Datos 100% sintéticos. Los gráficos muestran señales para revisión, no fraude
> probado ni resultados oficiales de fiscalización.

## Fuentes

- `<catalog>.gold_<id>.tax_risk_metrics`
- `<catalog>.gold_<id>.risk_queue`
- `<catalog>.gold_<id>.current_actions`
- `<catalog>.gold_<id>.data_quality_summary`
- `<catalog>.gold_<id>.taxpayer_activity_daily`

## Prompt para Genie

```text
Crea un dashboard AI/BI en español titulado “Radar Tributario · Patrones y
Gobierno”. Todos los datos son sintéticos. Presenta resultados como señales de
riesgo para revisión humana, nunca como prueba de fraude.

Usa solamente:
- <catalog>.gold_<id>.tax_risk_metrics
- <catalog>.gold_<id>.risk_queue
- <catalog>.gold_<id>.current_actions
- <catalog>.gold_<id>.data_quality_summary

Diseña cuatro secciones:

1. Panorama agregado: tarjetas con MEASURE(declared_sales),
MEASURE(assessed_tax), MEASURE(claimed_tax_credit) y
MEASURE(taxpayers_count), con periodo explícito y moneda PEN.

2. Patrones de señales: conteo y puntaje promedio por primary_signal y
priority; distribución geográfica por region; comparación por segment y
economic_activity. Usa solo agregados y suprime grupos con menos de 5 filas.

3. Calidad: fallas y pass_rate_pct por regla, destacando RUC inválido,
contribuyente desconocido, duplicados y montos negativos/imposibles.

4. Seguimiento de investigaciones: conteos de acciones por decision_type,
status y priority; abiertas, vencidas y evolución por created_at. No muestres
notes, assignee, taxpayer_id, taxpayer_name, ruc, alert_id ni action_id.

Filtros globales: fecha, región, segmento y actividad económica. Paleta sobria
con rojo/ámbar solo para prioridad. Incluye una nota visible: “Datos sintéticos;
las señales requieren revisión y no constituyen prueba de fraude”.

No crees una tabla de cola, ranking de contribuyentes ni vista caso por caso:
esa función pertenece a la App. El dashboard es de solo lectura.

En tax_risk_metrics usa MEASURE(...) y GROUP BY ALL para dimensiones. En las
otras fuentes usa agregaciones SQL normales. Si no hay datos, muestra un estado
vacío; no inventes cifras.
```

## Criterio de éxito

- Ningún identificador o nombre de contribuyente visible.
- Patrones por geografía, segmento y actividad.
- Calidad y estado agregado de investigaciones.
- Sin botones de decisión ni duplicación de la cola de la App.
- Disclaimer sintético visible.
