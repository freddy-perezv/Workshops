# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # 00 · Preparar Unity Catalog
# MAGIC
# MAGIC **Objetivo:** crear un espacio aislado y gobernado para el laboratorio.
# MAGIC
# MAGIC Todos pueden compartir el mismo catálogo. Cada participante trabajará
# MAGIC en cuatro schemas aislados, derivados de un único identificador:
# MAGIC
# MAGIC - `bronze_<participante>`: datos raw, tal como llegan.
# MAGIC - `silver_<participante>`: datos validados y normalizados.
# MAGIC - `gold_<participante>`: tablas y métricas para Genie y la App.
# MAGIC - `ops_<participante>`: decisiones y tareas generadas por la App.
# MAGIC
# MAGIC También se crea un Unity Catalog Volume para simular una zona de
# MAGIC aterrizaje. El catálogo permite aplicar permisos y trazabilidad desde
# MAGIC el origen hasta la decisión.
# MAGIC
# MAGIC by: Freddy Perez

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parámetros
# MAGIC
# MAGIC Cambia únicamente `participant_id` por tu nombre o identificador, usando
# MAGIC letras, números y guion bajo. Por ejemplo, `freddy` generará
# MAGIC `bronze_freddy`, `silver_freddy`, `gold_freddy` y `ops_freddy`.
# MAGIC El instructor define el catálogo compartido.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_retail_equipo_01", "01. Catálogo")
dbutils.widgets.text("participant_id", "", "02. Tu identificador")
dbutils.widgets.dropdown("create_catalog", "false", ["true", "false"], "03. Crear catálogo")
dbutils.widgets.dropdown("scale", "M", ["S", "M", "L"], "04. Escala")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
PARTICIPANT_ID = dbutils.widgets.get("participant_id").strip().lower()
CREATE_CATALOG = dbutils.widgets.get("create_catalog") == "true"
SCALE = dbutils.widgets.get("scale")

if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError(
        "catalog_name debe iniciar con letra, contener solo a-z, 0-9 o _, "
        "y tener entre 3 y 63 caracteres."
    )

if not re.fullmatch(r"[a-z][a-z0-9_]{1,30}", PARTICIPANT_ID):
    raise ValueError(
        "participant_id debe iniciar con letra, contener solo a-z, 0-9 o _, "
        "y tener entre 2 y 31 caracteres. Ejemplo: freddy"
    )

BRONZE_SCHEMA = f"bronze_{PARTICIPANT_ID}"
SILVER_SCHEMA = f"silver_{PARTICIPANT_ID}"
GOLD_SCHEMA = f"gold_{PARTICIPANT_ID}"
OPS_SCHEMA = f"ops_{PARTICIPANT_ID}"

SCALE_ROWS = {
    "S": 500_000,
    "M": 5_000_000,
    "L": 20_000_000,
}

EVENT_ROWS = SCALE_ROWS[SCALE]
CURRENT_USER = spark.sql("SELECT current_user() AS user").first()["user"]
spark.conf.set("spark.sql.session.timeZone", "UTC")

print(f"Usuario: {CURRENT_USER}")
print(f"Catálogo: {CATALOG}")
print(f"Schemas: {BRONZE_SCHEMA}, {SILVER_SCHEMA}, {GOLD_SCHEMA}, {OPS_SCHEMA}")
print(f"Escala: {SCALE} ({EVENT_ROWS:,} eventos)")
print("Zona horaria de negocio: UTC")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Crear el catálogo y los schemas
# MAGIC
# MAGIC `CREATE CATALOG` requiere un privilegio a nivel de metastore. Si la
# MAGIC organización no lo concede, el administrador debe crear previamente el
# MAGIC catálogo y otorgar `USE CATALOG` + `CREATE SCHEMA`.

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient

_w = WorkspaceClient()

# --- Paso 1: Verificar si el catálogo existe ---
_existing = [c.name for c in _w.catalogs.list() if c.name == CATALOG]

if not _existing:
    print("=" * 60)
    print(f"⚠️  El catálogo '{CATALOG}' NO existe.")
    print("   Este workspace usa Default Storage y requiere")
    print("   creación manual desde la UI.")
    print()
    print("   ➡️  Pasos:")
    print("   1. En la barra lateral, ve a  Catalog")
    print("   2. Haz clic en  ＋ Add  >  Add a catalog")
    print(f"   3. Nombre del catálogo:  {CATALOG}")
    print("   4. En Type selecciona  Standard")
    print("   5. En Storage Location selecciona  Default Storage")
    print("   6. Haz clic en  Create")
    print("=" * 60)
    print()
    print("⏳ Esperando a que el catálogo sea creado...")
    print("   (esta celda revisa cada 15 segundos)")
    print()

    # Esperar hasta que el catálogo aparezca
    while True:
        _check = [c.name for c in _w.catalogs.list() if c.name == CATALOG]
        if _check:
            print(f"\n✅ ¡Catálogo '{CATALOG}' detectado!")
            break
        print("   ... aún no existe, reintentando en 15s")
        time.sleep(15)
else:
    print(f"✅ Catálogo '{CATALOG}' ya existe.")

# --- Paso 2: Agregar comentario al catálogo ---
try:
    spark.sql(
        f"""COMMENT ON CATALOG `{CATALOG}` IS
        'Workshop Pulso Retail: datos gobernados, Genie Agent y Databricks App'"""
    )
except Exception:
    pass  # Ignorar si no tiene permisos para comentar

# --- Paso 3: Crear schemas ---
spark.sql(f"USE CATALOG `{CATALOG}`")

for schema in (BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA, OPS_SCHEMA):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`{schema}`")
    print(f"  Schema '{schema}' ✔")

print(f"\n✅ Catálogo '{CATALOG}' y schemas configurados correctamente.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Crear el volume de landing
# MAGIC
# MAGIC El volume representa la frontera entre archivos que llegan desde un
# MAGIC sistema fuente y tablas Delta gobernadas. En la siguiente notebook
# MAGIC escribiremos datos sintéticos en `landing` y después los ingeriremos a
# MAGIC Bronze.

# COMMAND ----------

spark.sql(
    f"""
    CREATE VOLUME IF NOT EXISTS `{CATALOG}`.`{BRONZE_SCHEMA}`.`landing`
    COMMENT 'Archivos raw del laboratorio Pulso Retail'
    """
)

VOLUME_PATH = f"/Volumes/{CATALOG}/{BRONZE_SCHEMA}/landing"
dbutils.fs.mkdirs(f"{VOLUME_PATH}/sales_events")

print(f"Volume listo: {VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Guardar configuración auditable
# MAGIC
# MAGIC Esta tabla permite saber quién inicializó el laboratorio y con qué
# MAGIC escala. También ofrece a la guía y a la App un contrato estable sobre
# MAGIC los nombres de los objetos.

# COMMAND ----------

spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config` (
      catalog_name STRING NOT NULL,
      participant STRING NOT NULL,
      scale STRING NOT NULL,
      expected_events BIGINT NOT NULL,
      initialized_at TIMESTAMP NOT NULL
    )
    USING DELTA
    TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
    """
)

spark.sql(f"DELETE FROM `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config`")
spark.sql(
    f"""
    INSERT INTO `{CATALOG}`.`{OPS_SCHEMA}`.`workshop_config`
    VALUES ('{CATALOG}', current_user(), '{SCALE}', {EVENT_ROWS}, current_timestamp())
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Validación
# MAGIC
# MAGIC La celda final debe mostrar cuatro schemas y el volume `landing`.
# MAGIC Si falla, no continúes: normalmente indica falta de permisos en Unity
# MAGIC Catalog.

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT schema_name
        FROM `{CATALOG}`.information_schema.schemata
        WHERE schema_name IN (
          '{BRONZE_SCHEMA}', '{SILVER_SCHEMA}', '{GOLD_SCHEMA}', '{OPS_SCHEMA}'
        )
        ORDER BY schema_name
        """
    )
)

display(spark.sql(f"SHOW VOLUMES IN `{CATALOG}`.`{BRONZE_SCHEMA}`"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ Catálogo gobernado, schemas por capa y volume de landing.
# MAGIC
# MAGIC **Siguiente:** `01_ingesta_bronze` para generar e ingerir datos a
# MAGIC escala con errores controlados.