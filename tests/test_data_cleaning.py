import pandas as pd
from src.data_cleaning import clean_transactions


def test_every_row_is_retained_or_rejected(raw_fixture, fixture_cleaned):
    fact, rejects, _ = fixture_cleaned
    assert len(raw_fixture) == len(fact) + len(rejects) == 27
    assert len(fact) == 20
    assert len(rejects) == 7


def test_rejections_are_explicit(fixture_cleaned):
    _, rejects, decisions = fixture_cleaned
    assert set(rejects.rejection_reason) == {
        "missing_invoice", "missing_stock_code", "invalid_invoice_date",
        "zero_quantity", "invalid_price", "zero_price_noncommercial",
        "credit_with_positive_quantity",
    }
    assert sum(rule["excluded"] for rule in decisions["rules"]) == 7


def test_returns_are_not_dropped(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    credits = fact[fact.event_type == "return"]
    assert len(credits) == 3
    assert credits.return_amount.sum() == 23.5
    assert credits.gross_sales.sum() == 0
    assert credits.net_sales.sum() == -23.5


def test_negative_quantity_without_c_marker_is_flagged(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    bad_marker = fact[fact.unmarked_return == 1]
    assert len(bad_marker) == 1
    assert bad_marker.iloc[0].invoice_no == "10012"
    assert bad_marker.iloc[0].event_type == "return"


def test_anonymous_rows_are_kept_without_fake_ids(fixture_cleaned):
    fact, _, _ = fixture_cleaned
    assert fact.customer_id.isna().sum() == 2
    assert (fact.loc[fact.customer_id.isna(), "gross_sales"] > 0).all()


def test_identical_lines_preserved_and_flagged(fixture_cleaned):
    fact, _, decisions = fixture_cleaned
    assert decisions["duplicate_rows_flagged_not_removed"] == 1
    assert len(fact[fact.invoice_no == "10015"]) == 2
    assert fact.line_id.is_unique


def test_cleaning_does_not_mutate_source(raw_fixture):
    before = raw_fixture.copy(deep=True)
    clean_transactions(raw_fixture)
    pd.testing.assert_frame_equal(raw_fixture, before)


def test_empty_table_has_safe_empty_result(raw_fixture):
    fact, rejects, _ = clean_transactions(raw_fixture.iloc[0:0])
    assert fact.empty and rejects.empty


def test_non_integer_quantities_rejected(raw_fixture):
    row = raw_fixture.iloc[[0]].copy()
    row["Quantity"] = row["Quantity"].astype("float64")
    row.loc[:, "Quantity"] = 1.5
    _, rejects, _ = clean_transactions(row)
    assert rejects.iloc[0].rejection_reason == "invalid_quantity"


def test_product_description_missing_does_not_imply_invalid_revenue(raw_fixture):
    one = raw_fixture.iloc[[0]].copy()
    one.loc[:, "Description"] = None
    fact, rejects, _ = clean_transactions(one)
    assert len(fact) == 1 and len(rejects) == 0
    assert pd.isna(fact.iloc[0].product_description)
