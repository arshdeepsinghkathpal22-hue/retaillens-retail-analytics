import json
from pathlib import Path
from src.config import ROOT
from src.pipeline import run_pipeline


def test_end_to_end_demo_creates_real_sql_outputs(tmp_path):
    result = run_pipeline(ROOT / "data/samples/synthetic_retail_fixture.csv", tmp_path, demo=True)
    assert result["rows_accepted"] == 20
    assert result["sql_queries_passed"] == 10
    assert all(result["metric_reconciliation"].values())
    assert (tmp_path / "data/outputs/05_cohort_retention.csv").is_file()
    assert (tmp_path / "data/processed/retail.sqlite").is_file()
    assert (tmp_path / "reports/business_insights.md").is_file()
    assert "SYNTHETIC TEST FIXTURE" in (tmp_path / "reports/business_insights.md").read_text()


def test_pipeline_is_repeatable(tmp_path):
    fixture = ROOT / "data/samples/synthetic_retail_fixture.csv"
    first = run_pipeline(fixture, tmp_path, demo=True)
    first_metrics = (tmp_path / "data/outputs/08_executive_summary.csv").read_text()
    second = run_pipeline(fixture, tmp_path, demo=True)
    assert first_metrics == (tmp_path / "data/outputs/08_executive_summary.csv").read_text()
    assert first["rows_accepted"] == second["rows_accepted"]
    assert first["sha256"] == second["sha256"]
