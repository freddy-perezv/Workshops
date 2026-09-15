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
# MAGIC Cada participante trabajará en un catálogo propio con cuatro schemas:
# MAGIC
# MAGIC - `bronze`: datos raw, tal como llegan.
# MAGIC - `silver`: datos validados y normalizados.
# MAGIC - `gold`: tablas y métricas para Genie y la App.
# MAGIC - `ops`: decisiones y tareas generadas por la App.
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
# MAGIC Cambia `catalog_name` por un nombre único. Solo se permiten letras,
# MAGIC números y guion bajo. Si la empresa ya asignó un catálogo, selecciona
# MAGIC `create_catalog = false`.

# COMMAND ----------

dbutils.widgets.text("catalog_name", "workshop_argentina_equipo_01", "01. Catálogo")
dbutils.widgets.dropdown("create_catalog", "true", ["true", "false"], "02. Crear catálogo")
dbutils.widgets.dropdown("scale", "M", ["S", "M", "L"], "03. Escala")

# COMMAND ----------

import re

CATALOG = dbutils.widgets.get("catalog_name").strip().lower()
CREATE_CATALOG = dbutils.widgets.get("create_catalog") == "true"
SCALE = dbutils.widgets.get("scale")

if not re.fullmatch(r"[a-z][a-z0-9_]{2,62}", CATALOG):
    raise ValueError(
        "catalog_name debe iniciar con letra, contener solo a-z, 0-9 o _, "
        "y tener entre 3 y 63 caracteres."
    )

SCALE_ROWS = {
    "S": 500_000,
    "M": 5_000_000,
    "L": 20_000_000,
}

EVENT_ROWS = SCALE_ROWS[SCALE]
CURRENT_USER = spark.sql("SELECT current_user() AS user").first()["user"]
spark.conf.set("spark.sql.session.timeZone", "America/Argentina/Buenos_Aires")

print(f"Usuario: {CURRENT_USER}")
print(f"Catálogo: {CATALOG}")
print(f"Escala: {SCALE} ({EVENT_ROWS:,} eventos)")
print("Zona horaria de negocio: America/Argentina/Buenos_Aires")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Crear el catálogo y los schemas
# MAGIC
# MAGIC `CREATE CATALOG` requiere un privilegio a nivel de metastore. Si la
# MAGIC organización no lo concede, el administrador debe crear previamente el
# MAGIC catálogo y otorgar `USE CATALOG` + `CREATE SCHEMA`.

# COMMAND ----------

if CREATE_CATALOG:
    from databricks.sdk import WorkspaceClient
    _w = WorkspaceClient()
    # Discover the first non-internal external location
    _ext_locs = [
        loc for loc in _w.external_locations.list()
        if not loc.name.startswith("__")
    ]
    if not _ext_locs:
        raise RuntimeError(
            "No se encontró ninguna external location disponible. "
            "Pide a un administrador crear una, o crea el catálogo "
            "manualmente desde la UI."
        )
    _managed_url = f"{_ext_locs[0].url.rstrip('/')}/{CATALOG}"
    print(f"External location: {_ext_locs[0].name} → {_managed_url}")
    spark.sql(
        f"CREATE CATALOG IF NOT EXISTS `{CATALOG}` MANAGED LOCATION '{_managed_url}'"
    )
    spark.sql(
        f"""
        COMMENT ON CATALOG `{CATALOG}` IS
        'Workshop Argentina: datos gobernados, Genie Agent y Databricks App'
        """
    )

spark.sql(f"USE CATALOG `{CATALOG}`")

for schema in ("bronze", "silver", "gold", "ops"):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`{schema}`")

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
    CREATE VOLUME IF NOT EXISTS `{CATALOG}`.`bronze`.`landing`
    COMMENT 'Archivos raw del laboratorio Pulso Retail Argentina'
    """
)

VOLUME_PATH = f"/Volumes/{CATALOG}/bronze/landing"
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
    CREATE TABLE IF NOT EXISTS `{CATALOG}`.`ops`.`workshop_config` (
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

spark.sql(f"DELETE FROM `{CATALOG}`.`ops`.`workshop_config`")
spark.sql(
    f"""
    INSERT INTO `{CATALOG}`.`ops`.`workshop_config`
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
        WHERE schema_name IN ('bronze', 'silver', 'gold', 'ops')
        ORDER BY schema_name
        """
    )
)

display(spark.sql(f"SHOW VOLUMES IN `{CATALOG}`.`bronze`"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Resultado esperado
# MAGIC
# MAGIC ✅ Catálogo gobernado, schemas por capa y volume de landing.
# MAGIC
# MAGIC **Siguiente:** `01_ingesta_bronze` para generar e ingerir datos a
# MAGIC escala con errores controlados.