"""Source reader: keeps source row numbering so each decision is traceable."""
from pathlib import Path
import pandas as pd
from .config import RAW_COLUMNS


def load_transactions(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path, engine="openpyxl")
    elif path.suffix.lower() == ".csv":
        df = pd.read_csv(path, dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"})
    else:
        raise ValueError("Expected an .xlsx or .csv source file")
    missing = sorted(set(RAW_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required source columns: {', '.join(missing)}")
    df = df.loc[:, list(RAW_COLUMNS)].copy()
    df.insert(0, "source_row", range(2, len(df) + 2))
    return df
