import pandas as pd
from src.feature_engineering import build_dimensions, calculate_rfm, calculate_cohorts, _score


def test_returns_net_gross_reconcile(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    assert abs(fact.gross_sales.sum() - fact.return_amount.sum() - fact.net_sales.sum()) < 0.001


def test_orders_count_distinct_invoice_not_lines(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    sales = fact[fact.event_type == "sale"]
    assert len(sales) > sales.invoice_no.nunique()
    assert sales[sales.invoice_no == "10015"].shape[0] == 2


def test_rfm_purchase_frequency_deduplicates_invoice(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    rfm = calculate_rfm(fact).set_index("customer_id")
    assert int(rfm.loc["107", "frequency_orders"]) == 2
    assert int(rfm.loc["101", "frequency_orders"]) == 3
    assert "New Customers" in set(rfm.segment)


def test_rfm_excludes_anonymous_and_return_only(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    out = calculate_rfm(fact)
    assert out.customer_id.notna().all()
    assert out.customer_id.nunique() == 7


def test_rfm_reference_date_anchored_to_observation(fixture_cleaned):
    fact, _, decisions = fixture_cleaned
    assert decisions["reference_date"] == "2025-04-11"
    assert fact.loc[fact.date_key == "2025-04-10", "days_from_reference"].iloc[0] == 1


def test_rank_ties_keep_same_score():
    values = pd.Series([5, 5, 1, 0])
    ranked = _score(values, high_is_good=True)
    assert ranked.iloc[0] == ranked.iloc[1]
    assert ranked.iloc[0] > ranked.iloc[-1]


def test_single_customer_rfm_does_not_crash(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    one = fact[fact.customer_id == "101"]
    rfm = calculate_rfm(one)
    assert len(rfm) == 1
    assert rfm.loc[0, "r_score"] == 3


def test_cohort_denominator_and_month_1(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    cohorts, last = calculate_cohorts(fact)
    assert last == "2025-03"
    jan = cohorts[cohorts.cohort_month == "2025-01"].set_index("months_since_acquisition")
    assert int(jan.loc[0, "cohort_size"]) == 3
    assert int(jan.loc[0, "active_customers"]) == 3
    assert int(jan.loc[1, "active_customers"]) == 2
    assert int(jan.loc[2, "active_customers"]) == 1
    assert float(jan.loc[1, "retention_percent"]) == 66.67


def test_cohort_excludes_incomplete_month(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    cohorts, _ = calculate_cohorts(fact)
    assert cohorts.cohort_month.max() <= "2025-03"
    assert (cohorts.months_since_acquisition <= 2).all()


def test_geography_dimension_links_to_fact(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    tables = build_dimensions(fact)
    assert tables["fact_sales"].geography_id.notna().all()
    assert tables["dim_geography"].geography_id.is_unique
    assert tables["dim_product"].product_id.is_unique
    assert "category" not in tables["dim_product"].columns
