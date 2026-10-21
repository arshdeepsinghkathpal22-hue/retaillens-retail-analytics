from pathlib import Path
import pytest
from src.data_loader import load_transactions
from src.data_validation import profile_source, check_cleaned


def test_csv_reads_preserving_identifiers(raw_fixture):
    assert str(raw_fixture.iloc[0].InvoiceNo) == "10001"
    assert "source_row" in raw_fixture
    assert raw_fixture.iloc[0].source_row == 2


def test_profile_reports_duplicates_and_malformed_date(raw_fixture):
    info = profile_source(raw_fixture)
    assert info["row_count"] == 27
    assert info["exact_duplicate_rows"] == 1
    assert info["missing"]["CustomerID"] == 2
    assert info["zero_quantity_rows"] == 1


def test_independent_quality_gate(raw_fixture, fixture_cleaned):
    fact, rejected, _ = fixture_cleaned
    report = check_cleaned(raw_fixture, fact, rejected)
    assert report["passed"]
    assert all(report["checks"].values())


def test_bad_column_fails_fast(tmp_path, raw_fixture):
    broken = tmp_path / "broken.csv"
    raw_fixture.drop(columns="Quantity").to_csv(broken, index=False)
    with pytest.raises(ValueError, match="Quantity"):
        load_transactions(broken)


def test_missing_dataset_has_explicit_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_transactions(tmp_path / "missing.xlsx")


def test_excel_ingestion_roundtrip(tmp_path, raw_fixture):
    output = tmp_path / "small.xlsx"
    raw_fixture.iloc[:3].drop(columns="source_row").to_excel(output, index=False)
    imported = load_transactions(output)
    assert len(imported) == 3
    assert imported.iloc[0].InvoiceNo == 10001  # Excel stores numeric-like invoice IDs as numbers.
