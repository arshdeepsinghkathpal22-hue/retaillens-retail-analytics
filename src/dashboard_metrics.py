"""Small, reusable metrics behind the Streamlit views.

All order and buyer denominators use positive purchase invoices. A return is a
separate transaction event; it reduces net sales but does not create a sale.
"""

import pandas as pd


def summary_metrics(fact: pd.DataFrame) -> dict[str, float | int]:
    """Summarize whatever filtered slice is currently visible in the dashboard."""
    sales = fact.loc[fact["event_type"] == "sale"]
    buyers = sales.loc[sales["customer_id"].notna()]
    orders = int(sales["invoice_no"].nunique())
    distinct_buyers = int(buyers["customer_id"].nunique())
    buyer_orders = buyers.groupby("customer_id")["invoice_no"].nunique()
    repeat_buyers = int((buyer_orders >= 2).sum())
    gross = float(fact["gross_sales"].sum())
    credits = float(fact["return_amount"].sum())
    net = float(fact["net_sales"].sum())
    unidentified_gross = float(sales.loc[sales["customer_id"].isna(), "gross_sales"].sum())
    return {
        "gross": gross,
        "returns": credits,
        "net": net,
        "orders": orders,
        "buyers": distinct_buyers,
        "aov": gross / orders if orders else 0.0,
        "units_sold": int(fact["units_sold"].sum()),
        "repeat_buyers": repeat_buyers,
        "repeat_rate": (100 * repeat_buyers / distinct_buyers) if distinct_buyers else 0.0,
        "return_rate": (100 * credits / gross) if gross > 0 else 0.0,
        "unidentified_gross": unidentified_gross,
        "unidentified_gross_rate": (100 * unidentified_gross / gross) if gross > 0 else 0.0,
    }


def monthly_sales(fact: pd.DataFrame, selected_months: list[str] | None = None) -> pd.DataFrame:
    """Return monthly gross/credit/net totals; optionally show zero-activity months."""
    grouped = fact.groupby("month_key", as_index=False, sort=True).agg(
        gross=("gross_sales", "sum"), returns=("return_amount", "sum"), net=("net_sales", "sum"),
    )
    if selected_months is not None:
        grouped = pd.DataFrame({"month_key": pd.Series(sorted(set(selected_months)), dtype="string")}).merge(
            grouped, on="month_key", how="left"
        )
        grouped[["gross", "returns", "net"]] = grouped[["gross", "returns", "net"]].fillna(0)
    return grouped


def product_sales(fact: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Group lines first, then join product names once (do not multiply revenue)."""
    grouped = fact.groupby("product_id", as_index=False).agg(
        gross=("gross_sales", "sum"),
        returns=("return_amount", "sum"),
        net=("net_sales", "sum"),
        units=("units_sold", "sum"),
    )
    return (grouped.merge(products[["product_id", "product_description"]], on="product_id", how="left", validate="one_to_one")
            .sort_values(["net", "product_id"], ascending=[False, True]))


def country_sales(fact: pd.DataFrame, geography: pd.DataFrame) -> pd.DataFrame:
    grouped = fact.groupby("geography_id", as_index=False).agg(
        gross=("gross_sales", "sum"),
        returns=("return_amount", "sum"),
        net=("net_sales", "sum"),
    )
    sales = (fact.loc[fact["event_type"].eq("sale")]
             .groupby("geography_id")["invoice_no"].nunique().rename("orders"))
    grouped = grouped.join(sales, on="geography_id")
    grouped["orders"] = grouped["orders"].fillna(0).astype(int)
    return (grouped.merge(geography, on="geography_id", how="left", validate="one_to_one")
            .sort_values("net", ascending=False))


def period_buyers_with_segments(fact: pd.DataFrame, rfm: pd.DataFrame) -> pd.DataFrame:
    """RFM labels are *historical full-source snapshots*, not recomputed per filter."""
    sale_lines = fact.loc[(fact["event_type"] == "sale") & fact["customer_id"].notna()]
    if sale_lines.empty:
        return pd.DataFrame(columns=["customer_id", "orders_in_selection", "segment"])
    orders = sale_lines.groupby("customer_id", as_index=False)["invoice_no"].nunique()
    orders = orders.rename(columns={"invoice_no": "orders_in_selection"})
    return orders.merge(rfm[["customer_id", "segment"]], on="customer_id", how="left", validate="one_to_one")


def cohort_grid(cohorts: pd.DataFrame) -> pd.DataFrame:
    if cohorts.empty:
        return pd.DataFrame()
    return cohorts.pivot(index="cohort_month", columns="months_since_acquisition", values="retention_percent").sort_index()
