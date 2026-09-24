# Troubleshooting · Radar Tributario

> Los datos son sintéticos y las alertas solo priorizan revisión.

## Unity Catalog

Si falla la creación de schemas o volume, confirme `USE CATALOG`,
`CREATE SCHEMA`, `CREATE VOLUME`, `READ VOLUME` y `WRITE VOLUME`. El catálogo
debe existir antes de Notebook 00.

## Rendimiento

Use `S` (~50k) para diagnóstico, `M` (~250k) para el taller y `L` (~1m) solo
con compute validado. Si `OPTIMIZE` consume tiempo, deje `optimize_tables=false`.

## Calidad

- Sin errores: confirme que Notebook 01 terminó y no cambió los módulos.
- Muchos RUC inválidos: verifique que la expresión de dígito se conservó.
- Silver vacío: revise joins por `taxpayer_id` y las cuarentenas.
- La fila recuperada debe permanecer en cuarentena como `REPROCESSED`.

## Metric view

Si `WITH METRICS` no está soportado, actualice runtime/warehouse. En consultas
use `MEASURE(...)`; no aplique `SUM()` directamente a medidas.

## Genie

El baseline debe permanecer sin instrucciones. Si ambas experiencias responden
igual, confirme que no se copiaron contexto o verified queries al baseline.
Si Genie afirma fraude, revise las instrucciones y repita E04, E10 y E14.

## App

La App debe apuntar a `risk_queue`, `tax_risk_metrics` y `action_tasks` del
participante. Si falla una escritura, compare el contrato de columnas y otorgue
`MODIFY` solo sobre ops. Este trabajo no modifica `app/**`; una App que aún
espere nombres retail necesita alineación separada antes del despliegue.

## Dashboard

Si aparecen RUC o rankings individuales, elimine ese widget y use agregados.
El dashboard complementa la App y debe suprimir grupos con menos de cinco filas.

## Contingencia

Prepare escala S, dos Spaces de respaldo, App desplegada y capturas sin datos
reales. Nunca sustituya la contingencia con información tributaria productiva.
