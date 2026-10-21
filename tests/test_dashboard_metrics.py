"""Tests against the generated showcase output, with SQL as a second oracle."""
from pathlib import Path
import pandas as pd
from src.dashboard_metrics import (
    summary_metrics, monthly_sales, product_sales, country_sales,
    period_buyers_with_segments, cohort_grid,
)

DEMO = Path(__file__).resolve().parents[1] / "demo_run/data/processed"


def demo_data():
    fact = pd.read_csv(DEMO / "fact_sales.csv", dtype={"customer_id": "string"})
    geo = pd.read_csv(DEMO / "dim_geography.csv")
    products = pd.read_csv(DEMO / "dim_product.csv")
    rfm = pd.read_csv(DEMO / "customer_rfm.csv", dtype={"customer_id": "string"})
    cohort = pd.read_csv(DEMO / "cohort_retention.csv")
    return fact, geo, products, rfm, cohort


def test_summary_matches_executed_sql():
    fact, *_ = demo_data()
    report = pd.read_csv(DEMO.parent / "outputs/08_executive_summary.csv").iloc[0]
    kpis = summary_metrics(fact)
    assert round(kpis["net"], 2) == report.net_sales_gbp
    assert round(kpis["gross"], 2) == report.gross_sales_gbp
    assert round(kpis["returns"], 2) == report.returns_gbp
    assert kpis["orders"] == report.orders
    assert kpis["buyers"] == report.known_buying_customers
    assert round(kpis["aov"], 2) == report.gross_aov_gbp
    buyers = fact[(fact.event_type == "sale") & fact.customer_id.notna()]
    assert kpis["repeat_buyers"] == int((buyers.groupby("customer_id").invoice_no.nunique() >= 2).sum())


def test_filtered_metrics_exclude_returns_from_orders():
    fact, *_ = demo_data()
    feb = fact[fact.month_key == "2025-02"]
    m = summary_metrics(feb)
    assert m["orders"] == feb.loc[feb.event_type.eq("sale"), "invoice_no"].nunique()
    assert round(m["gross"] - m["returns"], 2) == round(m["net"], 2)
    assert m["returns"] > 0


def test_monthly_and_zero_activity_month():
    fact, *_ = demo_data()
    bymonth = monthly_sales(fact, ["2025-01", "2025-02", "2026-05"])
    assert round(bymonth.loc[bymonth.month_key.eq("2025-02"), "net"].iloc[0], 2) == round(
        fact.loc[fact.month_key.eq("2025-02"), "net_sales"].sum(), 2
    )
    assert bymonth.loc[bymonth.month_key.eq("2026-05"), "net"].iloc[0] == 0


def test_product_and_country_reconcile():
    fact, geo, products, *_ = demo_data()
    assert round(product_sales(fact, products).net.sum(), 2) == round(fact.net_sales.sum(), 2)
    assert round(country_sales(fact, geo).net.sum(), 2) == round(fact.net_sales.sum(), 2)
    assert len(product_sales(fact, products)) == products.product_id.nunique()


def test_segments_are_snapshot_labels():
    fact, _, _, rfm, _ = demo_data()
    selected = period_buyers_with_segments(fact[fact.month_key == "2025-01"], rfm)
    assert not selected.empty
    assert selected.segment.notna().all()
    assert selected.customer_id.is_unique


def test_cohort_grid_keeps_unobserved_blanks():
    _, _, _, _, cohort = demo_data()
    grid = cohort_grid(cohort)
    assert not grid.empty
    assert (grid.iloc[:, 0] == 100).all()
    assert grid.isna().any().any()  # Future windows are omitted, not false 0%s.
    assert (grid.stack() >= 0).all() and (grid.stack() <= 100).all()


def test_empty_slice_does_not_divide_by_zero():
    fact, *_ = demo_data()
    empty = fact.iloc[:0]
    kpis = summary_metrics(empty)
    assert kpis["aov"] == kpis["return_rate"] == kpis["repeat_rate"] == 0
    assert monthly_sales(empty, ["2025-01"]).iloc[0].net == 0
