"""End-to-end ETL: traceable cleaning, star tables, SQLite queries and reports."""
from pathlib import Path
import hashlib
import json
import sqlite3
import pandas as pd
from .data_loader import load_transactions
from .data_cleaning import clean_transactions
from .data_validation import profile_source, check_cleaned, save_json
from .feature_engineering import build_dimensions, calculate_rfm, calculate_cohorts
from .database import create_database
from .reporting import create_reports
from .config import ROOT


def run_pipeline(input_path: Path, output_root: Path, demo: bool = False) -> dict:
    input_path = Path(input_path)
    output_root = Path(output_root)
    processed = output_root / "data/processed"
    outputs = output_root / "data/outputs"
    processed.mkdir(parents=True, exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)

    raw = load_transactions(input_path)
    profile = profile_source(raw)
    fact, rejected, cleaning = clean_transactions(raw)
    validation = check_cleaned(raw, fact, rejected)
    if not validation["passed"]:
        raise ValueError(f"Clean data failed pre-load checks: {validation}")
    if fact.empty:
        raise ValueError("No valid priced transactions available. Inspect rejected_records.csv")
    dims = build_dimensions(fact)
    rfm = calculate_rfm(fact)
    cohorts, last_complete = calculate_cohorts(fact)
    dims["customer_rfm"] = rfm
    dims["cohort_retention"] = cohorts
    dims["rejected_records"] = rejected
    for name, frame in dims.items():
        frame.to_csv(processed / f"{name}.csv", index=False)
    save_json(profile, outputs / "source_profile.json")
    save_json(cleaning, outputs / "cleaning_decisions.json")
    save_json(validation, outputs / "data_quality.json")

    last_complete_index = pd.Period(last_complete, "M")
    meta = {
        "last_complete_month_index": int(last_complete_index.year * 12 + last_complete_index.month),
        "last_complete_month": last_complete,
        "snapshot_date": cleaning["reference_date"],
        "is_synthetic_fixture": int(demo),
    }
    warehouse_tables = {k: v for k, v in dims.items() if k != "rejected_records"}
    database_path = processed / "retail.sqlite"
    create_database(database_path, warehouse_tables, meta)
    # Import after the tables exist; reporting never substitutes for SQL execution.
    from scripts.run_sql_checks import run_sql_queries
    outcomes = run_sql_queries(database_path, ROOT / "sql", outputs)
    failures = [name for name, result in outcomes.items()
                if isinstance(result, dict) and result.get("status") == "failed"]
    if failures or outcomes["blocking_warehouse_issues"]:
        raise ValueError(f"SQL checks failed: {failures}; warehouse issues={outcomes['blocking_warehouse_issues']}")

    with sqlite3.connect(database_path) as con:
        summary = pd.read_sql_query((ROOT / "sql/08_executive_summary.sql").read_text(), con).iloc[0]
        sql_rfm = pd.read_sql_query((ROOT / "sql/06_rfm_analysis.sql").read_text(), con)
        sql_cohort = pd.read_sql_query((ROOT / "sql/05_cohort_retention.sql").read_text(), con)
    checks = {
        "gross_python_vs_sql": abs(float(fact.gross_sales.sum()) - summary.gross_sales_gbp) < 0.02,
        "returns_python_vs_sql": abs(float(fact.return_amount.sum()) - summary.returns_gbp) < 0.02,
        "net_python_vs_sql": abs(float(fact.net_sales.sum()) - summary.net_sales_gbp) < 0.02,
        "order_count_python_vs_sql": int(fact.loc[fact.event_type == "sale", "invoice_no"].nunique()) == int(summary.orders),
        "rfm_customer_counts_match": len(sql_rfm) == len(rfm),
        "cohort_rows_match": len(sql_cohort) == len(cohorts),
    }
    if not all(checks.values()):
        raise ValueError(f"Metric reconciliation failed: {checks}")
    # Equal-size checks aren't enough to guarantee segmentation or retention correctness.
    merged_rfm = rfm.merge(sql_rfm, on="customer_id", suffixes=("_py", "_sql"), how="outer", indicator=True)
    checks["rfm_scores_and_segments_agree"] = bool(
        merged_rfm["_merge"].eq("both").all()
        and all(merged_rfm[f"{name}_py"].eq(merged_rfm[f"{name}_sql"]).all()
                for name in ["r_score", "f_score", "m_score", "segment"])
    )
    if len(cohorts):
        sql_cmp = sql_cohort[["cohort_month", "months_since_acquisition", "active_customers", "cohort_size", "retention_percent"]]
        join = cohorts.merge(sql_cmp, on=["cohort_month", "months_since_acquisition"], how="outer", suffixes=("_py", "_sql"), indicator=True)
        checks["cohort_counts_and_rates_agree"] = bool(
            join["_merge"].eq("both").all()
            and all((join[f"{c}_py"] - join[f"{c}_sql"]).abs().max() < 0.001
                    for c in ["active_customers", "cohort_size", "retention_percent"])
        )
    else:
        checks["cohort_counts_and_rates_agree"] = sql_cohort.empty
    if not all(checks.values()):
        raise ValueError(f"Cross-tool checks failed: {checks}")
    save_json(checks, outputs / "metric_reconciliation.json")
    create_reports(output_root, fact, rejected, profile, cleaning, validation, dims, last_complete, demo)
    file_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    def display_path(path: Path) -> str:
        # Keep bundled JSON logs portable instead of writing build-machine paths.
        try:
            return path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            return str(path)

    run_log = {
        "dataset": "SYNTHETIC showcase data" if demo else "External input: verify source identity",
        "input_file": display_path(input_path), "sha256": file_hash,
        "source_attribution": ("SYNTHETIC generated fixture; no real-world source" if demo
                               else "External user-supplied input: independently verify its origin; UCI candidate Chen (2015), DOI 10.24432/C5BW33"),
        "rows_raw": len(raw), "rows_accepted": len(fact), "rows_rejected": len(rejected),
        "sql_queries_passed": sum(v.get("status") == "passed" for v in outcomes.values() if isinstance(v, dict)),
        "metric_reconciliation": checks, "last_complete_cohort_month": last_complete,
        "snapshot_date": cleaning["reference_date"], "warehouse": display_path(database_path),
        "note": "No .pbix file or Power BI visual has been built or tested in this environment.",
    }
    save_json(run_log, outputs / "run_log.json")
    return run_log
