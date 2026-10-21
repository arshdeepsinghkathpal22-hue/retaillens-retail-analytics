# Publish RetailLens on GitHub and Streamlit Community Cloud

The bundled dashboard is a **publicly displayable synthetic showcase**, not a claimed analysis of the original UCI dataset. The code, demo CSVs, query results, and audit JSON files are included so Streamlit Community Cloud can load the demo without a database, secrets, or downloading an external workbook.

## 1. Test on your Windows laptop

Open the project folder in VS Code or PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_pipeline.py --demo
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the **Local URL** displayed in the terminal, normally `http://localhost:8501`. Check every one of the seven pages, change country/month filters, browse the SQL Explorer, and verify that the synthetic-data warning is clearly visible. Streamlit installation/browser launch was not possible in the original offline packaging environment, so this is a necessary final manual browser check.

## 2. Create a GitHub repository

1. Create a new repository on GitHub, such as `retail-revenue-retention-analytics`.
2. Extract the supplied ZIP first. **Do not upload the ZIP as a single file**: upload its *contents* (the README, `streamlit_app.py`, `src/`, `demo_run/`, `tests/`, `.streamlit/`, etc.).
3. Keep `.gitignore`, `.streamlit/config.toml`, and `.github/workflows/tests.yml` in the repository. If uploading through GitHub's web UI, the usual Git CLI is easier to preserve hidden directories.
4. Do **not** commit `data/raw/Online Retail.xlsx`, `data/processed/`, `data/outputs/`, `.venv/`, API credentials, or large private datasets.
5. Wait for **Actions → Python tests** to finish green on both Python versions before promoting the repository as verified on GitHub.

Git CLI alternative, run from the extracted folder (replace `<YOUR-REPO-URL>`):

```bash
git init
# Only if your default branch isn't main:
git branch -M main
git add .
git status
# Verify no private file was staged.
git commit -m "feat: reproducible retail analytics and Streamlit showcase"
git remote add origin <YOUR-REPO-URL>
git push -u origin main
```

## 3. Deploy on Streamlit Community Cloud

1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app / New app** and select your repository and the `main` branch.
3. Set the main file path to **`streamlit_app.py`**.
4. Choose Deploy. Dependencies are installed from `requirements.txt` automatically.
5. When the app becomes available, check all seven pages and both filter states.

The public app loads the checked-in **synthetic demo** by default. The **Real dataset** radio option only appears when *you have run the original UCI file locally* to create `data/processed/` outputs. Those generated real-data artifacts are intentionally excluded from GitHub. Do not claim the public deployment runs real UCI data until you have intentionally published an appropriately licensed, verified dataset and reviewed its privacy/provenance.

## 4. What the public visitor can inspect

- Executive metrics, gross/net/return waterfall, monthly trends, top products, markets
- Product rankings, revenue concentration, per-product credits, detailed CSV downloads
- Repeat buyers, RFM snapshot and complete-month cohort-retention heatmap
- Evidence-backed investigations and exportable decision prompts
- Source profiling, rejected records, data quality audit and executed SQL statuses
- **SQL Explorer** showing actual SQL files beside their precomputed result tables
- Data-flow walkthrough, method choices, Power BI design guide and limitations

All tabular charts read `demo_run/data/processed/` and `demo_run/data/outputs/`, which are bundled with this repository. The app is read-only. It does not run the ETL on every visitor page load.

## 5. Troubleshooting

- **Deployment says `No module named streamlit/plotly`:** verify root `requirements.txt` is committed.
- **`Missing pipeline outputs`:** confirm you committed `demo_run/data/processed/*.csv` and `demo_run/data/outputs/*.json` / `*.csv`. The `.sqlite` file is optional for the dashboard and is ignored by Git.
- **Blank SQL Explorer:** ensure `sql/*.sql` and `demo_run/data/outputs/*.csv` exist in your repository.
- **Filters return empty output:** clear and reselect countries/months; charts are designed to handle an empty selection without crashing.
- **On Windows PowerShell, scripts won't activate:** use the explicit `.venv\Scripts\python.exe` commands; activation is not required.
- **GitHub ZIP upload shows only one file:** extract and push the project tree instead; Streamlit Cloud needs to find `streamlit_app.py` at the repository root.

## 6. Honest verification boundary

Offline validation covers the synthetic ETL, ten executed SQLite SQL analyses, Python/SQL reconciliation, regression/unit tests, and programmatic construction of all dashboard pages/Plotly figures. It does **not** include an actual Streamlit browser session, GitHub Actions run, Streamlit Community Cloud deployment, original-UCI full-data execution, PostgreSQL deployment, or Power BI Desktop `.pbix` validation. Those require the target online/desktop environments.
