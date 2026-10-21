from pathlib import Path
import pytest
from src.config import ROOT
from src.data_loader import load_transactions
from src.data_cleaning import clean_transactions


@pytest.fixture
def raw_fixture():
    return load_transactions(ROOT / "data/samples/synthetic_retail_fixture.csv")


@pytest.fixture
def fixture_cleaned(raw_fixture):
    return clean_transactions(raw_fixture)
