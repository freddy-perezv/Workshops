# Prework y validación técnica

Completar esta validación al menos 48 horas antes del workshop. El laboratorio
debe realizarse en un workspace **DEV o QA**, nunca en producción.

## Requisitos por participante o equipo

| Prioridad | Requisito | Uso durante el laboratorio | Validación previa |
|---|---|---|---|
| P0 | Acceso al workspace DEV/QA | Ejecutar todo el laboratorio | Iniciar sesión correctamente |
| P0 | Cluster compatible con Unity Catalog | Generar, transformar y validar datos | Iniciar cluster y ejecutar `SELECT current_user()` |
| P0 | Unity Catalog | Crear catálogo, schemas, tablas y volume | Crear un catálogo de prueba o usar uno previamente asignado |
| P0 | SQL warehouse | Consultas de Genie y write-back de la App | Ejecutar `SELECT 1` |
| P0 | AI/BI Genie | Crear y probar el Genie Space | Abrir Genie y crear un espacio vacío |
| P0 | Databricks Apps | Crear y desplegar la aplicación | Abrir Apps y confirmar permiso de creación |
| P1 | Git folder o Workspace files | Importar el contenido del repositorio | Clonar el repositorio público o cargar la carpeta |

## Privilegios mínimos de Unity Catalog

### Opción A: catálogo compartido y schemas por participante (diseño principal)

- El administrador crea un catálogo compartido.
- Cada participante recibe `USE CATALOG` y `CREATE SCHEMA`.
- La notebook 00 crea `bronze_<id>`, `silver_<id>`, `gold_<id>` y `ops_<id>`,
  además de un volume de landing aislado.

### Opción B: catálogo por participante o equipo

Cuando la política de gobierno no permita `CREATE CATALOG`, el administrador
el administrador puede crear un catálogo dedicado para cada equipo y conceder:

- `USE CATALOG` y `CREATE SCHEMA` sobre el catálogo.
- Si los schemas ya existen: `USE SCHEMA`, `CREATE TABLE`, `CREATE VOLUME`,
  `SELECT`, `MODIFY`, `READ VOLUME` y `WRITE VOLUME`.

## Especificación recomendada del cluster

| Propiedad | Valor recomendado |
|---|---|
| Databricks Runtime | 16.4 LTS o versión LTS superior compatible |
| Aceleración | Photon activado |
| Access mode | Standard/Shared compatible con Unity Catalog |
| Driver | 32–64 GB RAM |
| Workers | Autoscaling, mínimo 2 y máximo 8 |
| Instancias | On-demand para evitar interrupciones durante el workshop |
| Autotermination | 60 minutos |

Para `S` puede utilizarse un cluster menor. Para `L`, validar cuotas y tiempo de
ejecución previamente.

## Especificación recomendada del SQL warehouse

| Propiedad | Valor recomendado |
|---|---|
| Tipo | Serverless, cuando esté disponible |
| Tamaño | Medium |
| Auto-stop | 45–60 minutos |
| Permiso del participante | CAN USE |
| Permiso de la App | CAN USE |

No es necesario un warehouse exclusivo por persona si el workspace dispone de
un warehouse compartido con capacidad suficiente para la concurrencia esperada.

## Validación funcional

Un usuario piloto debe confirmar:

1. Puede crear o utilizar el catálogo asignado.
2. Puede crear schemas, tablas y volumes.
3. Puede iniciar y adjuntar el cluster a una notebook.
4. Puede ejecutar una consulta en el SQL warehouse.
5. Puede crear y ejecutar un Genie Space.
6. Puede crear una Databricks App y asignarle un SQL warehouse y un Genie Space.

## No requerido

- Lakebase.
- Model Serving o Vector Search.
- Credenciales de GitHub para un repositorio público.
- Acceso a producción.
