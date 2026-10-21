# Final validation and project handoff

## Completed by automated demo run

- [x] Genuine source metadata/licensing checked on UCI official page
- [x] Raw/processed/test data paths separated, no overwrite of original source
- [x] Reader supports .xlsx and .csv; synthetic fixture labelled
- [x] Cleaning audit, rejection reasons and profile exported
- [x] Historical sale/return metrics, RFM, cohorts calculated
- [x] Star-schema-style warehouse and 10 SQL queries implemented and executed in SQLite
- [x] SQL/Python revenue, order, RFM and cohort results cross-checked in the demo
- [x] Matplotlib demo plots with visible synthetic labels
- [x] Streamlit seven-view source with query explorer; every view and Plotly serialization smoke-tested with stubbed UI
- [x] Deterministic 7,725-row synthetic showcase and checked-in query/CSV outputs
- [x] Power BI data files, design, relationship documentation and DAX measures prepared

## Must still be done locally before claiming final portfolio deployment

- [ ] Download and verify original UCI Online Retail workbook (download currently blocked here)
- [ ] Run entire pipeline using actual UCI data; inspect every failure and complete-cohort boundary
- [ ] Check data-quality and SQL results for unexpected outliers/invoices
- [ ] Read generated **real-data** `reports/business_insights.md`, fact-check findings and form recommendations
- [ ] Import Power BI tables; create and validate DAX measures; save real `.pbix`
- [ ] Export genuine Power BI screenshots; show all four finished dashboard pages
- [ ] Optionally load PostgreSQL schema/imports and run SQL queries against PostgreSQL (SQLite executed)
- [ ] Run CI in GitHub after push; capture actual passing status
- [ ] Actually open Streamlit in a browser and verify mobile/desktop navigation, then deploy on Streamlit Community Cloud

**Commands:** `python -m pytest -q`; `python scripts/run_pipeline.py --demo`; `python scripts/download_data.py`; `python scripts/run_pipeline.py --input "data/raw/Online Retail.xlsx"`; `python scripts/run_sql_checks.py`.

**Source page:** https://archive.ics.uci.edu/dataset/352/online+retail. **Dataset attribution:** Chen, D. (2015), UCI, DOI 10.24432/C5BW33, CC BY 4.0.
