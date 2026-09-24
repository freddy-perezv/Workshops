# Prework · Radar Tributario

Completar 48 horas antes en un workspace DEV/QA, nunca producción.

## Requisitos

- Cluster con Unity Catalog y Databricks Runtime LTS compatible con metric views.
- Catálogo creado por el instructor y permiso para crear schemas y volumes.
- SQL warehouse con `CAN USE`.
- Acceso a AI/BI Genie, Databricks Apps y AI/BI Dashboards.
- Capacidad para crear `bronze_<id>`, `silver_<id>`, `gold_<id>` y `ops_<id>`.

Privilegios mínimos: `USE CATALOG`, `CREATE SCHEMA`; dentro de los schemas,
`USE SCHEMA`, `CREATE TABLE`, `CREATE VOLUME`, `SELECT`, `MODIFY`,
`READ VOLUME` y `WRITE VOLUME` según la identidad que ejecuta cada paso.

## Compute recomendado

- Escala `S` (~50k): cluster pequeño.
- Escala `M` (~250k): recomendada; Photon, 2–4 workers.
- Escala `L` (~1m): validar cuota y duración antes del taller.
- SQL warehouse Serverless Small/Medium, auto-stop de 45 minutos.

## Prueba piloto

1. Ejecutar `SELECT current_user()` y `SELECT 1`.
2. Crear y borrar una tabla de prueba en el catálogo asignado.
3. Crear un managed volume de prueba.
4. Crear dos Genie Spaces vacíos.
5. Confirmar creación de App y Dashboard.
6. Ejecutar escala `M` completa y medir duración.

## Seguridad y datos

No cargar RUC, declaraciones, comprobantes ni expedientes reales. El workshop
genera únicamente datos sintéticos. Las señales y puntajes no deben usarse para
acusar, sancionar ni afirmar fraude; requieren validación humana y fuentes
autorizadas antes de cualquier actuación real.

No se requiere acceso al MVP SIRE ni integración con sus datos.
