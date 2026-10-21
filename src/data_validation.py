"""Data profiling and checks independent of the cleaning procedure."""
import json
from pathlib import Path
import pandas as pd


def profile_source(raw: pd.DataFrame) -> dict:
    content = raw.drop(columns=["source_row"], errors="ignore")
    dates = pd.to_datetime(content.get("InvoiceDate", pd.Series(dtype="object")), errors="coerce")
    quantity = pd.to_numeric(content.get("Quantity", pd.Series(dtype="object")), errors="coerce")
    price = pd.to_numeric(content.get("UnitPrice", pd.Series(dtype="object")), errors="coerce")
    # Quantiles are diagnostics only; outliers are not deleted automatically.
    positive_quantity = quantity[quantity > 0]
    positive_price = price[price > 0]
    def unusual_count(series: pd.Series) -> int:
        if len(series) < 4:
            return 0
        low, high = series.quantile([0.25, 0.75])
        return int((series > high + 1.5 * (high - low)).sum())

    return {
        "suspected_high_quantity_outliers": unusual_count(positive_quantity),
        "suspected_high_unit_price_outliers": unusual_count(positive_price),
        "row_count": int(len(raw)), "column_count": int(len(content)),
        "columns": {c: str(content[c].dtype) for c in content.columns},
        "missing": {c: int(content[c].isna().sum()) for c in content.columns},
        "missing_percent": {c: round(100 * content[c].isna().mean(), 2) if len(content) else 0 for c in content.columns},
        "exact_duplicate_rows": int(content.duplicated().sum()),
        "duplicate_invoice_numbers": int(content["InvoiceNo"].duplicated().sum()) if "InvoiceNo" in content else 0,
        "min_invoice_date": str(dates.min()) if dates.notna().any() else None,
        "max_invoice_date": str(dates.max()) if dates.notna().any() else None,
        "negative_quantity_rows": int((quantity < 0).sum()),
        "zero_quantity_rows": int((quantity == 0).sum()),
        "negative_price_rows": int((price < 0).sum()),
        "zero_price_rows": int((price == 0).sum()),
        "unique_invoices": int(content["InvoiceNo"].nunique()) if "InvoiceNo" in content else 0,
        "unique_products": int(content["StockCode"].nunique()) if "StockCode" in content else 0,
        "unique_customers": int(content["CustomerID"].nunique()) if "CustomerID" in content else 0,
        "unique_countries": int(content["Country"].nunique()) if "Country" in content else 0,
    }


def check_cleaned(raw: pd.DataFrame, cleaned: pd.DataFrame, rejected: pd.DataFrame) -> dict:
    checks = {
        "all_rows_accounted_for": len(raw) == len(cleaned) + len(rejected),
        "line_ids_unique": bool(cleaned["line_id"].is_unique),
        "no_nonpositive_prices": bool((cleaned["unit_price"] > 0).all()),
        "no_zero_quantities": bool((cleaned["quantity"] != 0).all()),
        "no_missing_invoices": bool(cleaned["invoice_no"].notna().all()),
        "no_missing_products": bool(cleaned["product_id"].notna().all()),
        "no_missing_dates": bool(cleaned["invoice_date"].notna().all()),
        "net_sales_reconcile": bool(((cleaned["gross_sales"] - cleaned["return_amount"] - cleaned["net_sales"]).abs() < 0.01).all()),
    }
    return {"checks": checks, "passed": all(checks.values()),
            "original_rows": len(raw), "accepted_rows": len(cleaned), "rejected_rows": len(rejected)}


def save_json(payload: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False, default=lambda x: x.item() if hasattr(x, "item") else str(x)), encoding="utf-8")
