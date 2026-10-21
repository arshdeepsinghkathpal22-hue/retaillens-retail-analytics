"""Retain usable sale and credit lines; explain every excluded line."""
import numpy as np
import pandas as pd


def _identifier(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    return text.mask(text.str.lower().isin(["", "nan", "none", "null", "<na>"]))


def clean_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = raw.copy()
    if "source_row" not in df:
        raise ValueError("source_row is required for auditability")
    if df.empty:
        return _empty_fact(), raw.assign(rejection_reason=pd.Series(dtype="string")), {"rules": [], "notes": []}

    invoices = _identifier(df["InvoiceNo"])
    products = _identifier(df["StockCode"])
    customers = _identifier(df["CustomerID"])
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce", format="mixed")
    quantities = pd.to_numeric(df["Quantity"], errors="coerce")
    prices = pd.to_numeric(df["UnitPrice"], errors="coerce")
    countries = df["Country"].astype("string").str.strip()
    countries = countries.mask(countries.str.lower().isin(["", "nan", "none", "<na>"]), "Unknown")
    names = df["Description"].astype("string").str.strip()
    names = names.mask(names.str.lower().isin(["", "nan", "none", "<na>"]))

    # No primary key exists for invoice lines. Exact lookalikes may be legitimate.
    source_duplicates = df.drop(columns="source_row").duplicated(keep="first")
    credit_flag = invoices.str.upper().str.startswith("C").fillna(False)
    negative_qty = (quantities < 0).fillna(False)
    returned = credit_flag | negative_qty
    invalid = [
        ("missing_invoice", invoices.isna()),
        ("missing_stock_code", products.isna()),
        ("invalid_invoice_date", dates.isna()),
        ("invalid_quantity", quantities.isna() | ((quantities % 1) != 0)),
        ("zero_quantity", quantities == 0),
        ("invalid_price", prices.isna() | (prices < 0)),
        ("zero_price_noncommercial", prices == 0),
        ("credit_with_positive_quantity", credit_flag & (quantities > 0)),
    ]
    reason = pd.Series(pd.NA, index=df.index, dtype="string")
    for name, condition in invalid:
        reason = reason.mask(reason.isna() & condition.fillna(False), name)
    accepted = reason.isna()
    rejected = df.loc[~accepted].copy()
    rejected["rejection_reason"] = reason.loc[~accepted]
    if not accepted.any():
        log = {"rules": [{"reason": name, "excluded": int((reason == name).sum())} for name, _ in invalid],
               "notes": ["No valid priced transactions were retained."],
               "duplicate_rows_flagged_not_removed": int(source_duplicates.sum()),
               "returns_without_credit_prefix": 0, "reference_date": None}
        return _empty_fact(), rejected, log

    subset = df.loc[accepted]
    qty = quantities.loc[accepted].astype("int64")
    price = prices.loc[accepted].astype("float64")
    is_return = returned.loc[accepted]
    amount = (qty.abs() * price).round(2)
    fact = pd.DataFrame({
        "line_id": subset["source_row"].astype("int64"),
        "source_row": subset["source_row"].astype("int64"),
        "invoice_no": invoices.loc[accepted],
        "invoice_date": dates.loc[accepted].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date_key": dates.loc[accepted].dt.strftime("%Y-%m-%d"),
        "month_key": dates.loc[accepted].dt.strftime("%Y-%m"),
        "month_index": dates.loc[accepted].dt.year * 12 + dates.loc[accepted].dt.month,
        "customer_id": customers.loc[accepted],
        "product_id": products.loc[accepted],
        "country": countries.loc[accepted],
        "product_description": names.loc[accepted],
        "quantity": qty,
        "unit_price": price.round(4),
        "event_type": np.where(is_return, "return", "sale"),
        "gross_sales": np.where(is_return, 0.0, amount).round(2),
        "return_amount": np.where(is_return, amount, 0.0).round(2),
        "net_sales": np.where(is_return, -amount, amount).round(2),
        "units_sold": np.where(is_return, 0, qty),
        "units_returned": np.where(is_return, qty.abs(), 0),
        "duplicate_source_values": source_duplicates.loc[accepted].astype("int64"),
        "unmarked_return": (negative_qty.loc[accepted] & ~credit_flag.loc[accepted]).astype("int64"),
    }).reset_index(drop=True)
    fact["month_index"] = fact["month_index"].astype("int64")
    reference = dates.loc[accepted].max().normalize() + pd.Timedelta(days=1)
    fact["days_from_reference"] = (reference - dates.loc[accepted].dt.normalize()).dt.days.to_numpy(dtype="int64")
    log = {
        "rules": [{"reason": name, "excluded": int((reason == name).sum())} for name, _ in invalid],
        "notes": [
            "No customer ID is fabricated: anonymous revenue is kept but excluded from customer KPIs.",
            "A negative quantity is treated as a return even without a C invoice prefix; flagged for review.",
            "C-prefixed invoices with positive quantity are excluded as contradictory records.",
            "Zero-price lines are kept in rejected records: they do not represent priced merchandise.",
            "Exact lookalike source lines are flagged but retained because the source has no unique line key.",
            "Amounts are GBP transaction-line proxies; tax, shipping, discounts and original credit matches are unavailable.",
        ],
        "duplicate_rows_flagged_not_removed": int(source_duplicates.sum()),
        "returns_without_credit_prefix": int(fact["unmarked_return"].sum()),
        "reference_date": reference.strftime("%Y-%m-%d"),
    }
    return fact, rejected, log


def _empty_fact() -> pd.DataFrame:
    fields = ["line_id", "source_row", "invoice_no", "invoice_date", "date_key", "month_key", "month_index",
              "customer_id", "product_id", "country", "product_description", "quantity", "unit_price",
              "event_type", "gross_sales", "return_amount", "net_sales", "units_sold", "units_returned",
              "duplicate_source_values", "unmarked_return", "days_from_reference"]
    return pd.DataFrame(columns=fields)
