# Checklist de revisión · Radar Tributario

## Alcance y ética

- [ ] Es un workshop distinto del MVP SIRE.
- [ ] Todos los datos y RUC son inequívocamente sintéticos.
- [ ] Puntajes y alertas se describen como señales, nunca prueba de fraude.
- [ ] La decisión final requiere revisión humana.

## Datos

- [ ] Escalas: S ~50k, M ~250k recomendada, L ~1m.
- [ ] Bronze conserva fuente; Silver aplica reglas y cuarentena.
- [ ] DQ cubre RUC inválido, desconocidos, duplicados y montos imposibles/negativos.
- [ ] Solo se recupera el RUC sintético reconstruible.
- [ ] Reejecutar notebooks no duplica datos.

## Gold y App

- [ ] Existen `taxpayer_activity_daily`, `risk_queue`, `current_actions`,
  `data_quality_summary` y `tax_risk_metrics`.
- [ ] `risk_queue` cumple todos los campos esperados por la App.
- [ ] `action_tasks` cumple el contrato de 15 columnas.
- [ ] Decisiones: `OPEN_INVESTIGATION`, `REQUEST_CLARIFICATION`, `DISMISS`.
- [ ] No se modificó `app/**`.

## Genie y dashboard

- [ ] Se crean dos Spaces: baseline vacío y enriquecido.
- [ ] Ambos reciben las mismas preguntas para comparación.
- [ ] Verified queries y evaluación usan PEN, periodo y fuente correctos.
- [ ] Dashboard usa agregados y no duplica la cola operativa.
- [ ] Disclaimer sintético visible en README, Genie y dashboard.

## Validación

```bash
python3 scripts/validate_content.py
```

- [ ] Validación local exitosa.
- [ ] Escala M probada en Databricks.
- [ ] Consultas verificadas ejecutadas sobre el catálogo del taller.
