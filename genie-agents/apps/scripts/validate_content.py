#!/usr/bin/env python3
"""Validaciones locales que no requieren acceso a Databricks."""

from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PREWORK.md",
    "notebooks/00_setup_unity_catalog.py",
    "notebooks/01_ingesta_bronze.py",
    "notebooks/02_calidad_cuarentena_silver.py",
    "notebooks/03_gold_semantic_layer.py",
    "notebooks/04_validacion_writeback.py",
    "genie/instructions.md",
    "genie/verified-queries.sql",
    "genie/evaluation-questions.csv",
    "app/app.yaml",
    "app/databricks.yml",
    "app/package.json",
    "app/client/src/App.tsx",
    "app/server/routes/decision-routes.ts",
    "docs/INSTRUCTOR_GUIDE.md",
]


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Faltan archivos requeridos: {', '.join(missing)}")


def check_notebooks() -> None:
    for notebook in sorted((ROOT / "notebooks").glob("*.py")):
        source = notebook.read_text(encoding="utf-8")
        if not source.startswith("# Databricks notebook source"):
            raise AssertionError(f"{notebook.name} no es Databricks Source")
        ast.parse(source, filename=str(notebook))


def check_package_json() -> None:
    payload = json.loads((ROOT / "app/package.json").read_text(encoding="utf-8"))
    assert payload["scripts"]["build"], "package.json no declara build"
    assert "@databricks/appkit" in payload["dependencies"]
    assert "@databricks/appkit-ui" in payload["dependencies"]


def check_genie_evaluation() -> None:
    with (ROOT / "genie/evaluation-questions.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 15, "Se requieren al menos 15 preguntas de evaluación"
    assert sum(row["severity"] == "critical" for row in rows) >= 5


def check_parameterized_writeback() -> None:
    route = (ROOT / "app/server/routes/decision-routes.ts").read_text(
        encoding="utf-8"
    )
    required_markers = [
        "IDENTIFIER(:actions_table)",
        "IDENTIFIER(:queue_table)",
        "CreateActionBody.safeParse",
        "x-forwarded-email",
    ]
    for marker in required_markers:
        assert marker in route, f"Falta protección de write-back: {marker}"
    assert not re.search(r"`[^`]*\$\{parsed\.data", route), (
        "No interpolar input del usuario dentro de SQL"
    )


def main() -> None:
    check_required_files()
    check_notebooks()
    check_package_json()
    check_genie_evaluation()
    check_parameterized_writeback()
    print("OK · Estructura, notebooks, evaluación y write-back validados.")


if __name__ == "__main__":
    main()
