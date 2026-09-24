#!/usr/bin/env python3
"""Valida contratos y narrativa de Radar Tributario sin Databricks."""

from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "PREWORK.md",
    "REVIEW_CHECKLIST.md",
    "notebooks/00_setup_unity_catalog.py",
    "notebooks/01_ingesta_bronze.py",
    "notebooks/02_calidad_cuarentena_silver.py",
    "notebooks/03_gold_semantic_layer.py",
    "notebooks/04_validacion_writeback.py",
    "notebooks/99_cleanup.py",
    "genie/README.md",
    "genie/instructions.md",
    "genie/verified-queries.sql",
    "genie/evaluation-questions.csv",
    "dashboard/README.md",
    "docs/ARCHITECTURE.md",
    "docs/INSTRUCTOR_GUIDE.md",
    "docs/TROUBLESHOOTING.md",
    "docs/READOUT_TEMPLATE.md",
    "app/app.yaml",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def check_files_and_notebooks() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    assert not missing, f"Faltan archivos: {', '.join(missing)}"
    for notebook in sorted((ROOT / "notebooks").glob("*.py")):
        source = notebook.read_text(encoding="utf-8")
        assert source.startswith("# Databricks notebook source"), notebook.name
        ast.parse(source, filename=str(notebook))


def check_scale_and_quality() -> None:
    setup = read("notebooks/00_setup_unity_catalog.py")
    assert '"S": 50_000' in setup and '"M": 250_000' in setup
    assert '"L": 1_000_000' in setup
    quality = read("notebooks/02_calidad_cuarentena_silver.py")
    for marker in (
        "DQ001_INVALID_RUC",
        "DQ002_UNKNOWN_TAXPAYER",
        "DQ003_DUPLICATE_DOCUMENT",
        "DQ004_NEGATIVE_AMOUNT",
        "DQ005_IMPOSSIBLE_AMOUNT",
        "REPROCESSED_SYNTHETIC_RUC",
    ):
        assert marker in quality, f"Falta control DQ: {marker}"


def check_gold_contracts() -> None:
    gold = read("notebooks/03_gold_semantic_layer.py")
    for asset in (
        "taxpayer_activity_daily",
        "risk_queue",
        "current_actions",
        "data_quality_summary",
        "tax_risk_metrics",
    ):
        assert asset in gold, f"Falta activo Gold: {asset}"
    for column in (
        "alert_id",
        "priority",
        "taxpayer_id",
        "taxpayer_name",
        "ruc",
        "segment",
        "region",
        "economic_activity",
        "risk_score",
        "declared_sales",
        "third_party_sales",
        "sales_gap",
        "claimed_tax_credit",
        "credit_ratio",
        "amendment_count",
        "signal_count",
        "primary_signal",
        "recommended_action",
        "evidence_summary",
    ):
        assert column in gold, f"Falta columna risk_queue: {column}"
    for column in (
        "action_id",
        "alert_id",
        "decision_type",
        "status",
        "assignee",
        "notes",
        "priority",
        "taxpayer_id",
        "taxpayer_name",
        "ruc",
        "risk_score",
        "created_by",
        "created_at",
        "due_at",
        "updated_at",
    ):
        assert column in gold, f"Falta columna action_tasks: {column}"
    for marker in (
        "OPEN_INVESTIGATION",
        "REQUEST_CLARIFICATION",
        "DISMISS",
        "SALES_MISMATCH",
        "EXCESSIVE_TAX_CREDIT",
        "UNUSUAL_AMENDMENTS",
        "DORMANT_OR_INACTIVE_ISSUANCE",
        "DUPLICATE_DOCUMENTS",
    ):
        assert marker in gold, f"Falta señal/decisión: {marker}"


def check_genie_and_disclaimers() -> None:
    genie = read("genie/README.md").lower()
    assert "baseline" in genie and "sin instrucciones" in genie
    assert "enriquecida" in genie and "verified-queries.sql" in genie
    with (ROOT / "genie/evaluation-questions.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 15
    assert sum(row["severity"] == "critical" for row in rows) >= 5
    for relative in (
        "README.md",
        "PREWORK.md",
        "genie/README.md",
        "genie/instructions.md",
        "dashboard/README.md",
        "docs/ARCHITECTURE.md",
        "docs/INSTRUCTOR_GUIDE.md",
        "docs/TROUBLESHOOTING.md",
        "docs/READOUT_TEMPLATE.md",
    ):
        text = read(relative).lower()
        assert "sintétic" in text, f"Falta disclaimer sintético en {relative}"
    dashboard = read("dashboard/README.md").lower()
    assert "no replica la cola" in dashboard


def main() -> None:
    check_files_and_notebooks()
    check_scale_and_quality()
    check_gold_contracts()
    check_genie_and_disclaimers()
    print("OK · Radar Tributario: estructura, contratos, Genie y disclaimers validados.")


if __name__ == "__main__":
    main()
