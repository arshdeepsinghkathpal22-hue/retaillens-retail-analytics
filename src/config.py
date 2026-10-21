"""Paths and column names used throughout the project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_COLUMNS = (
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country",
)


def ensure_output_dirs(root: Path = ROOT) -> None:
    for path in ("data/processed", "data/outputs", "reports/figures"):
        (root / path).mkdir(parents=True, exist_ok=True)
