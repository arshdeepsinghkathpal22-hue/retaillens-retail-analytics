# Actual build and validation record — 2026-10-21

## Environment and boundaries

- Environment: Python **3.13.5** with pandas **2.2.3**, Plotly **6.5.2**, SQLite and pytest.
- **Streamlit is NOT installed in the offline build container** (installation failed: no package index/network access). Thus there is **no verified live Streamlit browser screenshot or deployed public URL**.
- UCI source metadata was checked separately during the project design. The original 541,909-row workbook **could not be downloaded in this network-restricted container**. No verified UCI real-data results are bundled or claimed.
- A `.pbix` has not been built or run in Power BI Desktop. PostgreSQL has not been deployed. These are explicit outstanding tasks.

## Commands executed

```bash
python scripts/generate_showcase_data.py
python scripts/run_pipeline.py --demo
python -m pytest -q
python -m compileall -q src scripts tests streamlit_app.py
python -m pip install 'streamlit>=1.38,<2' --timeout 4 --retries 0 -q  # failed: offline index
```

The end-to-end `--demo` command executes all ten SQL query files, independently reconciles Python/SQL totals and RFM/cohort results, and regenerates the CSV, JSON, Markdown, images and SQLite warehouse. The additional 27-row fixture remains for small unit tests. Automated Streamlit stand-in tests execute *all seven page callbacks* and serialize the Plotly charts for non-empty/empty selections. This is **programmatic page-smoke coverage, not a browser run**.

## Verified results — clearly SYNTHETIC showcase, not UCI business evidence

| Gate | Verified outcome |
|---|---|
| Synthetic source lines | **7,725** |
| Accepted priced sale/credit lines | **7,716** |
| Rejected lines with recorded reasons | **9** |
| Preserved source-lookalikes | **1** flagged |
| Invoice-month range | **2024-01 through 2025-09** |
| Executed SQL files | **10 / 10 succeeded** |
| Blocking warehouse issues | **0** |
| Automated tests | **39 / 39 passed** |
| Streamlit view smoke runs | All **7** views, populated and empty filter selections |
| Python-vs-SQL reconciliation | All **8** recorded checks passed |
| Synthetic gross line sales | **£384,746.26** |
| Synthetic credits | **£5,619.36** |
| Synthetic net line sales | **£379,126.90** |
| Synthetic distinct purchase invoices | **3,055** |
| Synthetic identified purchasing customers | **320** |

**Never describe these figures as real UCI/business results.** Their role is to demonstrate reproducible mechanics and UI interactivity without relying on restricted source downloads.

## Evidence and reproducibility

- `demo_run/data/outputs/run_log.json`: source SHA-256, source type, counts, 8 reconciliation checks.
- `demo_run/data/outputs/sql_execution_log.json`: ten executed queries, result-row counts and no blocking issues.
- `demo_run/data/outputs/08_executive_summary.csv`: SQL reference figures.
- `demo_run/data/outputs/06_rfm_analysis.csv` and `05_cohort_retention.csv`: complete Python/SQL reconciled analysis output.
- `demo_run/data/processed/`: import-ready fact, dimensions, RFM, cohorts, rejected records, optional local SQLite warehouse.
- `demo_run/reports/`: generated, synthetic-labelled narrative and Matplotlib figures.
- `tests/test_streamlit_views.py`: seven-page and empty-filter chart smoke coverage. No live Streamlit process or browser was available.
- `tests/test_showcase_integrity.py`: deterministic fixture regeneration, bundle/output integrity and SHA-256 checks.

## Remaining before calling the whole portfolio deployed / real-data ready

1. Run `python -m pip install -r requirements.txt` in your local machine or Streamlit Community Cloud.
2. Locally run `python -m streamlit run streamlit_app.py` and visually review all seven pages. No claim of live UI testing here.
3. Upload project contents (not just its ZIP) to GitHub. Confirm GitHub Actions passes on Python 3.11 and 3.12. No CI run has been verified before upload.
4. Deploy `streamlit_app.py` from `main` to Streamlit Community Cloud and visually review navigation, filters, query detail and data labels.
5. Acquire/verify original UCI workbook and run `python scripts/run_pipeline.py --input "data/raw/Online Retail.xlsx"` before claiming real business insights.
6. In Windows Power BI Desktop, build/validate the .pbix dashboard and actual DAX evaluation; do not call the DAX text files a finished report.

See `DEPLOY_STREAMLIT_CLOUD.md` for concrete deployment steps. No fabricated results, tests, screenshots, live URL, source licensing, or success statuses are claimed.
