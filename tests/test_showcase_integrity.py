"""Make sure the version-controlled Cloud demo is complete and reproducible."""
import hashlib
import json
from pathlib import Path

import pandas as pd

from scripts.generate_showcase_data import generate

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data/samples/synthetic_showcase.csv"
DEMO = ROOT / "demo_run"


def test_showcase_generator_is_reproducible(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    generated = generate(a)
    generate(b)
    expected = hashlib.sha256(SAMPLE.read_bytes()).hexdigest()
    assert hashlib.sha256(a.read_bytes()).hexdigest() == expected
    assert a.read_bytes() == b.read_bytes()
    assert len(generated) > 5000
    assert generated.InvoiceDate.astype(str).str.startswith("2024-").any()
    assert generated.InvoiceDate.astype(str).str.startswith("2025-").any()


def test_bundled_demo_sql_and_lineage_are_complete():
    run = json.loads((DEMO / "data/outputs/run_log.json").read_text())
    log = json.loads((DEMO / "data/outputs/sql_execution_log.json").read_text())
    quality = json.loads((DEMO / "data/outputs/data_quality.json").read_text())
    assert run["dataset"].startswith("SYNTHETIC")
    assert run["source_attribution"].startswith("SYNTHETIC")
    assert run["sha256"] == hashlib.sha256(SAMPLE.read_bytes()).hexdigest()
    assert run["input_file"] == "data/samples/synthetic_showcase.csv"
    assert run["rows_raw"] == run["rows_accepted"] + run["rows_rejected"]
    assert run["rows_raw"] > 5000
    assert run["sql_queries_passed"] == 10
    assert all(run["metric_reconciliation"].values())
    assert quality["passed"]
    assert log["blocking_warehouse_issues"] == 0
    for sql in (ROOT / "sql").glob("[0-9][0-9]_*.sql"):
        assert log[sql.name]["status"] == "passed"
        assert (DEMO / "data/outputs" / (sql.stem + ".csv")).is_file()
    for file in ["fact_sales.csv", "dim_product.csv", "dim_geography.csv", "customer_rfm.csv",
                 "cohort_retention.csv", "rejected_records.csv"]:
        assert (DEMO / "data/processed" / file).is_file()
    summary = pd.read_csv(DEMO / "data/outputs/08_executive_summary.csv").iloc[0]
    assert round(summary.gross_sales_gbp - summary.returns_gbp, 2) == round(summary.net_sales_gbp, 2)
