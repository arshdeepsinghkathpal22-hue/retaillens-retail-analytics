"""Execute every analytical SQL file and save actual results, not mock tables."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT


def run_sql_queries(db_path: Path, sql_dir: Path, output_dir: Path) -> dict:
    if not db_path.is_file():
        raise FileNotFoundError(f"Missing warehouse database: {db_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    outcomes = {}
    with sqlite3.connect(db_path) as conn:
        for path in sorted(sql_dir.glob("*.sql")):
            try:
                frame = pd.read_sql_query(path.read_text(encoding="utf-8"), conn)
                frame.to_csv(output_dir / f"{path.stem}.csv", index=False)
                outcomes[path.name] = {"status": "passed", "rows": int(len(frame)), "columns": list(frame.columns)}
            except Exception as exc:
                outcomes[path.name] = {"status": "failed", "error": str(exc)}
        issues = pd.read_sql_query((sql_dir / "01_data_quality_checks.sql").read_text(), conn)
        severe = {"duplicate_line_ids", "missing_invoice", "missing_date", "missing_product", "nonpositive_price",
                  "orphan_products", "orphan_geographies", "orphan_named_customers"}
        outcomes["blocking_warehouse_issues"] = int(issues.loc[issues.check_name.isin(severe), "issue_count"].sum())
    (output_dir / "sql_execution_log.json").write_text(json.dumps(outcomes, indent=2), encoding="utf-8")
    return outcomes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=ROOT / "data/processed/retail.sqlite")
    parser.add_argument("--out", type=Path, default=ROOT / "data/outputs")
    args = parser.parse_args()
    summary = run_sql_queries(args.db, ROOT / "sql", args.out)
    print(json.dumps(summary, indent=2))
    if any(v.get("status") == "failed" for v in summary.values() if isinstance(v, dict)) or summary["blocking_warehouse_issues"]:
        sys.exit(1)
