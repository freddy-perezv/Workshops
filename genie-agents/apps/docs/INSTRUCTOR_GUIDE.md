# Guía del instructor · Radar Tributario

> El laboratorio usa datos completamente sintéticos. Las alertas son señales
> para revisión y nunca prueba de fraude. Radar Tributario es un workshop
> separado del MVP SIRE.

## Objetivo

En tres horas, cada equipo convierte datos tributarios imperfectos en productos
gobernados, compara dos experiencias Genie, registra una decisión humana y
comunica patrones agregados.

## Agenda

- 00:00–00:15: caso, disclaimer y criterio de éxito.
- 00:15–00:50: notebooks 00–03.
- 00:50–01:30: Genie baseline vs enriquecido.
- 01:30–01:40: pausa.
- 01:40–02:20: App y write-back.
- 02:20–02:30: notebook 04.
- 02:30–02:50: dashboard complementario.
- 02:50–03:00: evaluación y readout.

## Narrativa

Una administración tributaria similar a SUNAT necesita priorizar revisión sin
confundir anomalías con culpabilidad. El taller integra declaraciones y
comprobantes sintéticos, hace visibles problemas de calidad y crea una cola
explicable. La persona revisora decide abrir investigación, solicitar
aclaración o descartar.

## Notebooks

1. `00`: crea Bronze/Silver/Gold/ops y configura S ~50k, M ~250k o L ~1m.
2. `01`: genera contribuyentes, RUC, comprobantes y declaraciones sintéticos.
3. `02`: detecta RUC inválido, desconocidos, duplicados y montos anómalos;
   reconstruye únicamente un RUC sintético verificable.
4. `03`: crea actividad diaria, cinco señales, cola, contratos ops y metric view.
5. `04`: verifica persistencia, CDF y consulta posterior.

Pregunte: “¿Qué diferencia existe entre evidencia de una regla y prueba de
fraude?”. Respuesta esperada: la regla prioriza revisión; una conclusión exige
más fuentes, contexto, procedimiento y decisión autorizada.

## Genie

Cree primero el Space baseline sin instrucciones ni preguntas verificadas.
Capture respuestas. Cree luego el Space enriquecido con las mismas fuentes,
`genie/instructions.md` y SQL verificado. Repita literalmente las preguntas.

Evalúe no solo exactitud numérica: revise fuente, periodo, PEN, explicación,
calidad, incertidumbre y negativa a acusar o escribir.

## App

La App es la superficie operativa individual. La persona examina
`evidence_summary` y elige `OPEN_INVESTIGATION`, `REQUEST_CLARIFICATION` o
`DISMISS`. Toda acción requiere responsable y notas. Genie no confirma acciones.

Este rediseño no modifica `app/**`; antes del workshop compruebe que el
despliegue existente está alineado con los contratos Gold/ops documentados.

## Dashboard

Debe mostrar patrones agregados por región, segmento y actividad, calidad y
seguimiento de investigaciones. No debe listar contribuyentes ni duplicar la
cola de la App.

## Cierre

Cada equipo explica: una señal, una limitación de calidad, una diferencia entre
Genie baseline/enriquecido, una decisión registrada y un control necesario
antes de producción.
