# Workshop: Genie Agents + Databricks Apps

Laboratorio hands-on de tres horas para construir una solución de decisiones de
retail de extremo a extremo sobre Databricks.

El caso, **Pulso Retail**, ayuda a un responsable de operaciones a
detectar sucursales y productos con riesgo de quiebre de stock, entender la
situación con Genie y convertir el análisis en una acción auditable desde una
Databricks App.

## Resultado del laboratorio

Cada participante:

1. Crea objetos gobernados en Unity Catalog.
2. Genera e ingiere datos sintéticos a escala con errores intencionales.
3. Implementa Bronze, Silver, Gold, reglas de calidad y cuarentena.
4. Publica una metric view como capa semántica.
5. Configura y evalúa un Genie Space con reglas de negocio.
6. Ejecuta una Databricks App con indicadores, Genie y write-back.
7. Registra una decisión y comprueba que Genie puede consultarla.
8. Genera un dashboard ejecutivo con Genie (Lab 3).

## Estructura

```text
.
├── notebooks/             Notebooks Databricks Source, en orden de ejecución
├── genie/                 Instrucciones, preguntas verificadas y evaluación
├── app/                   Databricks App (AppKit + React + TypeScript)
├── dashboard/             Lab 3: prompt para dashboard AI/BI con Genie
├── docs/                  Arquitectura, guía del instructor y troubleshooting
├── PREWORK.md             Requisitos y validación previa
└── Agenda Workshop...     Agenda original
```

## Orden de ejecución

| Paso | Recurso | Tiempo objetivo | Resultado |
|---|---|---:|---|
| 0 | `notebooks/00_setup_unity_catalog.py` | 5 min | Catálogo y schemas |
| 1 | `notebooks/01_ingesta_bronze.py` | 10–15 min | Datos raw y Bronze |
| 2 | `notebooks/02_calidad_cuarentena_silver.py` | 10 min | Silver y cuarentena |
| 3 | `notebooks/03_gold_semantic_layer.py` | 10 min | Gold, cola y metric view |
| 4 | `genie/README.md` | 35 min | Genie Space evaluado |
| 5 | `app/README.md` | 45 min | App con decisión persistida |
| 6 | `notebooks/04_validacion_writeback.py` | 5 min | Ciclo cerrado validado |
| 7 | `dashboard/README.md` | 20 min | Dashboard AI/BI generado con Genie |

> Los tiempos de las notebooks se mantienen cortos mediante código preparado.
> Los participantes ejecutan y validan cada etapa. La agenda completa de 180
> minutos, incluidas bienvenida, pausa, evaluación y readout, está en
> `docs/INSTRUCTOR_GUIDE.md`.

## Escala de datos

La notebook de ingesta ofrece tres tamaños:

- `S`: 500 mil eventos, para prueba técnica.
- `M`: 5 millones de eventos, recomendado para el workshop.
- `L`: 20 millones de eventos, para equipos con compute robusto.

El volumen no es trabajo artificial: genera lecturas, escrituras, joins,
agregaciones, controles de calidad y optimización sobre el mismo flujo que
utilizan Genie y la aplicación.

## Antes de ejecutar

Completar [PREWORK.md](PREWORK.md). En particular:

- Usar un workspace DEV o QA, no producción.
- Definir un catálogo único por participante o equipo.
- Tener cluster UC y SQL warehouse disponibles.
- Confirmar acceso a Genie y Databricks Apps.

## Principio de seguridad

Genie y las consultas analíticas son de lectura. La escritura se realiza por
una ruta explícita de la App, validada y parametrizada, únicamente sobre
`ops.action_tasks`. Ningún texto libre generado por el modelo se ejecuta como
SQL.

## Estado

Esta carpeta es la versión local para revisión. No despliega ni modifica ningún
workspace. El despliegue se realizará solamente después de validar el contenido.

Validación local sin Databricks:

```bash
python3 scripts/validate_content.py
```
