"""Generate a richer, reproducible SYNTHETIC dashboard dataset.

All names, customers, invoices and sales figures are invented.  This file is
separate from the small fixture used for deterministic unit tests.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/samples/synthetic_showcase.csv"
PRODUCTS = [
    ("P101", "Ceramic Storage Jar", 13.50),
    ("P102", "Patterned Tea Towel", 7.25),
    ("P103", "Glass Flower Vase", 19.95),
    ("P104", "Scented Candle Set", 16.25),
    ("P105", "Cotton Table Runner", 22.50),
    ("P106", "Wooden Picture Frame", 9.75),
    ("P107", "Printed Coffee Mug", 11.99),
    ("P108", "Kitchen Utensil Holder", 18.50),
    ("P109", "Linen Cushion Cover", 17.25),
    ("P110", "Desk Organizer", 14.75),
    ("P111", "Floral Gift Wrap Pack", 4.95),
    ("P112", "Decorative Wall Hooks", 12.75),
    ("P113", "Woven Market Basket", 24.00),
    ("P114", "Felt Coaster Set", 8.25),
    ("P115", "Enamel Serving Tray", 31.50),
    ("P116", "Reusable Lunch Bag", 13.25),
    ("P117", "Brass Bookend Pair", 32.00),
    ("P118", "Striped Bath Mat", 19.00),
    ("P119", "Canvas Tote Bag", 12.50),
    ("P120", "Printed Notepad Trio", 6.75),
    ("P121", "Mini Planter Set", 15.00),
    ("P122", "Velvet Storage Box", 27.50),
    ("P123", "Handmade Soap Duo", 9.99),
    ("P124", "Ceramic Soap Dish", 10.25),
    ("P125", "Fairy Light Garland", 21.00),
    ("P126", "Garden Seed Labels", 6.95),
    ("P127", "Reusable Gift Pouch", 5.50),
    ("P128", "Stainless Bottle", 25.75),
    ("P129", "Floral Recipe Cards", 7.95),
    ("P130", "Bamboo Serving Board", 29.50),
    ("P131", "Small Knit Blanket", 34.00),
    ("P132", "Stoneware Serving Bowl", 28.25),
    ("P133", "Travel Wash Bag", 19.75),
    ("P134", "Compact Picnic Mat", 35.00),
    ("P135", "Canvas Pencil Case", 8.95),
    ("P136", "Porcelain Dessert Plate", 15.95),
]
COUNTRIES = ["United Kingdom", "Germany", "France", "Spain", "Ireland", "Netherlands", "Belgium", "Australia"]
WEIGHTS = np.array([0.64, 0.09, 0.08, 0.06, 0.05, 0.04, 0.025, 0.015])


def generate(path: Path = DEST) -> pd.DataFrame:
    rng = np.random.default_rng(20261021)
    months = pd.period_range("2024-01", "2025-09", freq="M")
    rows: list[dict] = []
    invoices = 500001
    product_weights = 1.0 / np.power(np.arange(1, len(PRODUCTS) + 1), 0.53)
    product_weights /= product_weights.sum()
    sales_for_possible_returns: list[dict] = []

    def add_invoice(customer: str | None, country: str, month: pd.Period, lines: int):
        nonlocal invoices
        current_no = str(invoices)
        invoices += 1
        month_start = month.to_timestamp()
        day = int(rng.integers(1, month.days_in_month + 1))
        hour = int(rng.integers(8, 21))
        minute = int(rng.integers(0, 60))
        date = month_start.replace(day=day, hour=hour, minute=minute)
        chosen = rng.choice(len(PRODUCTS), size=min(lines, len(PRODUCTS)), replace=False, p=product_weights)
        for idx in chosen:
            code, label, base = PRODUCTS[int(idx)]
            qty = int(rng.choice([1, 1, 1, 2, 2, 3, 4, 6, 8]))
            # Small seasonal effects, consistently priced within an invoice line.
            value = round(float(base) * (1.12 if month.month in (11, 12) else 1.0), 2)
            line = dict(InvoiceNo=current_no, StockCode=code, Description=label,
                        Quantity=qty, InvoiceDate=date.strftime("%Y-%m-%d %H:%M:%S"),
                        UnitPrice=value, CustomerID=customer, Country=country)
            rows.append(line)
            sales_for_possible_returns.append(line)

    for customer_n in range(320):
        customer = str(11000 + customer_n)
        country = str(rng.choice(COUNTRIES, p=WEIGHTS))
        acquisition = int(rng.integers(0, 17))
        if customer_n % 13 == 0:
            count = 1  # Includes genuine one-purchase customers.
        else:
            count = int(min(32, 2 + rng.poisson(6 + customer_n % 5)))
        offsets = [acquisition]
        if count > 1:
            offsets.extend(int(rng.integers(acquisition, len(months))) for _ in range(count - 1))
        for pos in sorted(offsets):
            add_invoice(customer, country, months[pos], int(rng.integers(1, 5)))

    # Sales from unidentifiable buyers contribute to revenue but not RFM.
    for _ in range(125):
        add_invoice(None, str(rng.choice(COUNTRIES, p=WEIGHTS)),
                    months[int(rng.integers(0, len(months)))], int(rng.integers(1, 4)))

    # Credit entries mimic negative-line refunds; no fictitious original matching logic.
    for original in rng.choice(len(sales_for_possible_returns), size=220, replace=False):
        source = sales_for_possible_returns[int(original)]
        old_month = pd.Period(source["InvoiceDate"][:7], "M")
        return_month = months[min(len(months) - 1, months.get_loc(old_month) + int(rng.integers(0, 3)))]
        credit = source.copy()
        credit["InvoiceNo"] = "C" + str(invoices)
        invoices += 1
        credit["Quantity"] = -min(int(source["Quantity"]), int(rng.integers(1, 4)))
        credit["InvoiceDate"] = return_month.to_timestamp().replace(day=min(20, return_month.days_in_month)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append(credit)

    # Explicit invalid-source cases support the rejection audit visualization.
    bad = rows[0].copy()
    for field, value in [("InvoiceNo", None), ("StockCode", None), ("InvoiceDate", "not a date"),
                         ("Quantity", 0), ("Quantity", 1.5), ("UnitPrice", -9.0),
                         ("UnitPrice", 0), ("UnitPrice", "missing")]:
        line = bad.copy()
        line[field] = value
        rows.append(line)
    contradictory = bad.copy()
    contradictory["InvoiceNo"] = "C" + str(invoices)
    contradictory["Quantity"] = 2
    rows.append(contradictory)
    # An exact lookalike without a unique source-line identifier is flagged, not dropped.
    rows.append(rows[3].copy())
    rng.shuffle(rows)
    frame = pd.DataFrame(rows, columns=["InvoiceNo", "StockCode", "Description", "Quantity",
                                             "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate labeled synthetic showcase transactions")
    parser.add_argument("--output", type=Path, default=DEST)
    args = parser.parse_args()
    result = generate(args.output)
    print(f"Wrote {len(result):,} synthetic source rows to {args.output}")
