# RetailLens — Interactive Streamlit demo

The project includes a **seven-view Streamlit application** over the already-generated Python/SQL analytical tables. It runs in your browser on your own laptop without a Power BI installation, API key, database server or internet connection (after dependencies are installed).

## Quick start on Windows (PowerShell + VS Code)

Open the extracted `customer-revenue-retention-analytics` directory in VS Code, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the **Local URL** printed by Streamlit in Chrome/Edge, normally `http://localhost:8501`.

Use **Ctrl+C** in the terminal to stop the local server.

### First, check that the Python/SQL demo works (optional)

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_pipeline.py --demo
```

Running the pipeline again refreshes `demo_run/`, including the metrics the app reads.

## What is included?

| View | Interactive components |
|---|---|
| Executive overview | Net/gross sales, credits, order count, buyer count, average order value, monthly sales trend, revenue bridge, geography and product charts |
| Products & markets | Ranked products, returns per product, country comparison, searchable results and CSV download |
| Customer retention | Repeat buyer rate, frequency distribution, precomputed RFM segments, retention cohort heatmap and CSV downloads |
| Recommendations | Data-grounded diagnostic signals, follow-up suggestions and downloadable action ideas |
| Data quality & SQL | Source/rejection counts, rejected reasons, data validation checks, executed SQL checks, profiling details and sample transaction lines |
| SQL Explorer | Real executed SQL source beside result tables, downloads and query logs |
| Methods & evidence | KPI definitions, project stages, documentation, limitations and Power BI build guide |

The sidebar lets you filter **transaction months** and **countries**. Those filters affect transactions and the transaction-derived KPIs, product data, period buyers and recommendations. The historical cohort heatmap intentionally remains a *full-data* view. RFM labels are historical snapshot classifications, not recomputed with filters; the segment chart displays only selected buyers.

All demo figures are explicitly labeled **synthetic**, not presented as real sales results. Profit, category sales, advertising ROI and predictions are not shown because those fields/models are absent.

## Use real UCI data instead of the synthetic demo

When ready, obtain the original UCI Online Retail workbook following the main README, then run:

```powershell
.\.venv\Scripts\python.exe scripts/download_data.py
.\.venv\Scripts\python.exe scripts/run_pipeline.py --input "data/raw/Online Retail.xlsx"
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

If downloading fails, get `Online Retail.xlsx` from https://archive.ics.uci.edu/dataset/352/online+retail and save it under `data/raw/` yourself. After the real-data pipeline creates `data/processed/fact_sales.csv`, the sidebar automatically offers **Real dataset (local pipeline output)**. The bundled demo remains available independently.

## Troubleshooting

- **`No module named streamlit`**: install the requirements using the *same* interpreter you use for `-m streamlit`.
- **`No module named plotly`**: likewise rerun dependency installation; Plotly is an app dependency.
- **`python is not recognized`**: install Python 3.11+ and restart your terminal, or use the Windows `py` launcher in place of `python` for virtual environment creation.
- **`Missing pipeline outputs`**: run `python scripts/run_pipeline.py --demo` from the project folder.
- **The browser page doesn't load**: keep the terminal open and use the Local URL printed there; the default is `http://localhost:8501` unless another port is chosen.
- **PowerShell blocks activation**: no activation is required; run the `.\.venv\Scripts\python.exe` commands above.
- **Charts not changing with filters**: cohorts intentionally remain a full-dataset snapshot; transaction charts do update. The filters are not filters for the underlying QA audit.

## Validation status

Dashboard-specific metrics have automated tests, including reconciliation of demo KPIs with executed SQL. The Streamlit UI could not be launched in the original build environment because Streamlit was not installed and external package downloads were blocked. A syntax check and the complete pytest suite were executed; the first browser launch must be checked on a machine where Streamlit can be installed. This repository includes no hosted public demo or claimed browser screenshot.

## Host publicly from GitHub

After validating locally, use [`DEPLOY_STREAMLIT_CLOUD.md`](DEPLOY_STREAMLIT_CLOUD.md) for the repository-upload and Streamlit Community Cloud steps. The demo ships with 7,725 **synthetic** source rows (7,716 accepted), 21 monthly periods, saved SQL results and auditable record exclusions. The tiny 27-row fixture is reserved for unit tests.
