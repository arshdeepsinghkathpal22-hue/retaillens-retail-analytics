# Data handling

**Source:** UCI Online Retail, 2010-12-01 to 2011-12-09, 541,909 rows and 8 original columns, UK-based gift retailer. URL: https://archive.ics.uci.edu/dataset/352/online+retail (CC BY 4.0).

- `raw/`: immutable original workbook `Online Retail.xlsx` (not included in repo or downloadable project bundle). Download with `python scripts/download_data.py` or download from UCI manually. `source_manifest.json` records download timestamp, file name, source URL and SHA-256 when the script succeeds.
- `samples/synthetic_retail_fixture.csv`: **synthetic**, small test case including credits, missing IDs, duplicates, invalid prices and dates. Safe to commit, never real evidence.
- `samples/synthetic_showcase.csv`: **synthetic** 7,725-row reproducible showcase across 21 months, generated using `python scripts/generate_showcase_data.py`; safe to commit, not real findings.
- `processed/`: generated fact and dimension CSVs, rejected-records CSV and SQLite warehouse after **real** pipeline execution. Gitignored.
- `outputs/`: generated SQL query tables, profile, cleaning audit, quality gate and reconciliation. Gitignored.
- `../demo_run/`: deliberately segregated synthetic outputs, included to let reviewers see an actual successful run without claiming UCI outcomes.

## Raw columns

`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.

## Download fallback

If UCI blocks automatic download, save `Online Retail.xlsx` from the official dataset page into `data/raw/`. The pipeline accepts `.xlsx` and schema-equivalent `.csv`. It never overwrites the original. The source contains no profit, cost, marketing spend, discount, customer acquisition cost or reliable product category attributes.

## Checksums

Every pipeline run writes the input file's SHA-256 to `data/outputs/run_log.json` or `demo_run/data/outputs/run_log.json`. This proves file identity between runs, not that an arbitrary user-supplied file matches UCI's canonical original.
