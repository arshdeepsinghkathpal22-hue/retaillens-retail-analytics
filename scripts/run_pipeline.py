"""Examples: python scripts/run_pipeline.py --demo / --input data/raw/Online Retail.xlsx"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.pipeline import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean transactions, model customers and execute warehouse SQL")
    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument("--demo", action="store_true", help="Run the labeled synthetic showcase (not the tiny unit-test fixture)")
    files.add_argument("--input", type=Path, help="Original UCI .xlsx or a schema-equivalent .csv")
    parser.add_argument("--output-root", type=Path, help="Destination root; defaults to demo_run or repository root")
    args = parser.parse_args()
    input_file = ROOT / "data/samples/synthetic_showcase.csv" if args.demo else args.input
    output_root = args.output_root or (ROOT / "demo_run" if args.demo else ROOT)
    try:
        result = run_pipeline(input_file, output_root, demo=args.demo)
    except Exception as exc:
        raise SystemExit(f"Pipeline error: {exc}")
    print(json.dumps(result, indent=2, default=lambda x: x.item() if hasattr(x, "item") else str(x)))
