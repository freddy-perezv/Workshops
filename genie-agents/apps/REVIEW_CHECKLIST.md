# Checklist de revisión local

Esta revisión ocurre antes de conectar o desplegar en Databricks.

## Historia y alcance

- [ ] El caso Pulso Retail es adecuado para la audiencia de Argentina.
- [ ] Reposición de inventario es una decisión suficientemente relevante.
- [ ] La agenda conserva el foco principal en Genie y Apps.
- [ ] Escala `M` (5 millones) es adecuada; ajustar si se prefiere `S` o `L`.

## Notebooks

- [ ] Las explicaciones Markdown permiten conducir cada bloque.
- [ ] Las reglas de calidad representan problemas realistas.
- [ ] La corrección automática se limita a provincia faltante.
- [ ] Las fórmulas de cobertura e ingreso en riesgo son aceptables.
- [ ] Catálogo por equipo coincide con el modelo de permisos del cliente.

## Genie

- [ ] Instrucciones y glosario utilizan la terminología deseada.
- [ ] Las 12 consultas verificadas cubren las preguntas prioritarias.
- [ ] Las 15 preguntas de evaluación reflejan el criterio de éxito.
- [ ] Genie recomienda, pero no escribe.

## Databricks App

- [ ] La interfaz es adecuada para una demostración ejecutiva.
- [ ] Los KPIs y la cola contienen la información correcta.
- [ ] Las decisiones permitidas son suficientes.
- [ ] Responsable, justificación y SLA son obligatorios.
- [ ] “Tareas recientes” completa el flujo, no solo confirma un clic.

## Seguridad y producción

- [ ] La App solo recibe datos mínimos desde el browser.
- [ ] Los datos críticos de la alerta se recuperan desde Gold.
- [ ] Los permisos declarados siguen mínimo privilegio.
- [ ] Change Data Feed es una extensión adecuada para integraciones.

## Pruebas locales

Ejecutar:

```bash
python3 scripts/validate_content.py
cd app
npm install
npm run typecheck
npm run build
npm run dev:mock
```

La instalación npm requiere conectividad con `registry.npmjs.org`.

## Decisión

- [ ] Aprobado para pruebas en Databricks.
- [ ] Requiere ajustes antes de desplegar.

Comentarios:

```text

```
