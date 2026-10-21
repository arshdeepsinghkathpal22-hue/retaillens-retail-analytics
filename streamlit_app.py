"""RetailLens: an interactive read-only view over the existing analytics pipeline.

Run from this repository: python -m streamlit run streamlit_app.py
No online account, API key or database server is needed for the bundled demo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_metrics import (
    summary_metrics, monthly_sales, product_sales, country_sales,
    period_buyers_with_segments, cohort_grid,
)

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "demo_run"
REAL = ROOT
SEA = "#38d9bb"
SKY = "#60a5fa"
CORAL = "#fb7185"
GOLD = "#fbbf24"
INK = "#eef3ff"
GRID = "rgba(148,163,184,0.14)"

st.set_page_config(
    page_title="RetailLens | Revenue & Retention",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .stApp { background: #0c1424; color: #edf2fc; }
  [data-testid="stSidebar"] { background: #101d30; border-right: 1px solid #293852; }
  [data-testid="stHeader"] { background: transparent; }
  h1, h2, h3 { letter-spacing: -.025em; }
  [data-testid="stMetric"] { background: #15243a; padding: 17px 19px; border-radius: 15px;
    border: 1px solid #2b3a51; }
  [data-testid="stMetricLabel"] { color: #a2b3ce; }
  [data-testid="stMetricValue"] { color: #f1f6ff; }
  .eyebrow { color: #47dec5; text-transform: uppercase; letter-spacing: .15em;
    font-size: .73rem; font-weight: 700; margin-bottom: 7px; }
  .subhead { color: #9fb0c9; font-size: 1rem; margin: -6px 0 20px; }
  .focus-card { background: #15243a; border: 1px solid #2b3a51; border-radius: 15px;
    padding: 18px; margin: 8px 0; }
  .focus-card b { color: #eff7ff; }
  .focus-card p { color: #b8c8db; margin: 7px 0 0; }
  .tag { display:inline-block; padding: 5px 10px; border-radius: 999px;
    background:#24374b; color: #81e6d9; font-size: .76rem; margin-bottom:9px; }
  div[data-testid="stDataFrame"] { border: 1px solid #2b3a51; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


def page_title(kicker: str, title: str, description: str) -> None:
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="subhead">{description}</div>', unsafe_allow_html=True)


def plot_style(fig: go.Figure, height: int = 345) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", height=height, margin=dict(t=22, b=24, l=8, r=16),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="Arial"), legend=dict(orientation="h", y=1.11, x=0),
        hovermode="closest",
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, title=None)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, title=None)
    return fig


def money(amount: float) -> str:
    amount = float(amount)
    if abs(amount) >= 1_000_000:
        return f"£{amount / 1_000_000:,.2f}m"
    if abs(amount) >= 10_000:
        return f"£{amount / 1_000:,.1f}k"
    return f"£{amount:,.2f}"


def download_csv(label: str, frame: pd.DataFrame, name: str) -> None:
    st.download_button(
        label=label, data=frame.to_csv(index=False).encode("utf-8"),
        file_name=name, mime="text/csv", key=f"csv_{name}",
    )


@st.cache_data(show_spinner="Reading analytics tables...", max_entries=3)
def load_data(folder: str, signature: tuple[int, ...]) -> dict:
    """Cache read-only source tables; file modification times invalidate the cache."""
    _ = signature
    base = Path(folder)
    processed = base / "data/processed"
    fact = pd.read_csv(processed / "fact_sales.csv", dtype={
        "invoice_no": "string", "product_id": "string", "customer_id": "string",
        "month_key": "string", "date_key": "string",
    })
    product = pd.read_csv(processed / "dim_product.csv", dtype={"product_id": "string"})
    geography = pd.read_csv(processed / "dim_geography.csv")
    rfm = pd.read_csv(processed / "customer_rfm.csv", dtype={"customer_id": "string"})
    cohorts = pd.read_csv(processed / "cohort_retention.csv")
    rejected = pd.read_csv(processed / "rejected_records.csv")
    logs = {}
    for name in ["data_quality", "source_profile", "sql_execution_log", "metric_reconciliation", "cleaning_decisions"]:
        path = base / "data/outputs" / (name + ".json")
        logs[name] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return dict(fact=fact, products=product, geography=geography,
                rfm=rfm, cohorts=cohorts, rejected=rejected, logs=logs)


def overview() -> None:
    page_title("01 / Revenue intelligence", "Executive overview",
               "A consistent view of revenue, transaction volume and where sales originate.")
    metrics = summary_metrics(FILTERED)
    c1, c2, c3 = st.columns(3)
    c1.metric("Net line sales", money(metrics["net"]))
    c2.metric("Gross line sales", money(metrics["gross"]))
    c3.metric("Credits / returns", money(metrics["returns"]))
    c4, c5, c6 = st.columns(3)
    c4.metric("Purchase invoices", f"{metrics['orders']:,}")
    c5.metric("Known buyers", f"{metrics['buyers']:,}")
    c6.metric("Gross average order value", money(metrics["aov"]))

    st.markdown("### Revenue movement")
    trend = monthly_sales(FILTERED, SELECTED_MONTHS)
    left, right = st.columns([1.7, 1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend.month_key, y=trend.net, mode="lines+markers",
                                 name="Net sales", line=dict(color=SEA, width=3)))
        fig.add_trace(go.Scatter(x=trend.month_key, y=trend.gross, mode="lines+markers",
                                 name="Gross sales", line=dict(color=SKY, width=2, dash="dot")))
        fig.update_yaxes(tickprefix="£")
        st.plotly_chart(plot_style(fig), use_container_width=True)
    with right:
        st.markdown("#### Revenue bridge")
        bridge = go.Figure(go.Waterfall(
            x=["Gross sales", "Returns", "Net sales"],
            y=[metrics["gross"], -metrics["returns"], metrics["net"]],
            measure=["absolute", "relative", "total"],
            increasing=dict(marker=dict(color=SKY)),
            decreasing=dict(marker=dict(color=CORAL)),
            totals=dict(marker=dict(color=SEA)),
            connector=dict(line=dict(color="#52647f")),
        ))
        bridge.update_yaxes(tickprefix="£")
        st.plotly_chart(plot_style(bridge), use_container_width=True)

    a, b = st.columns([1, 1])
    countries = country_sales(FILTERED, DATA["geography"])
    with a:
        st.markdown("### Sales by country")
        if countries.empty:
            st.info("No country transactions in this selection.")
        else:
            fig = px.bar(countries.head(10).sort_values("net"), x="net", y="country",
                         orientation="h", color_discrete_sequence=[SKY], labels={"net": "GBP", "country": ""})
            fig.update_xaxes(tickprefix="£")
            st.plotly_chart(plot_style(fig, 345), use_container_width=True)
    with b:
        st.markdown("### Top contributing products")
        prod = product_sales(FILTERED, DATA["products"])
        if prod.empty:
            st.info("No products in this selection.")
        else:
            fig = px.bar(prod.head(10).sort_values("net"), x="net", y="product_description",
                         orientation="h", color_discrete_sequence=[SEA], labels={"net": "GBP", "product_description": ""})
            fig.update_yaxes(automargin=True)
            fig.update_xaxes(tickprefix="£")
            st.plotly_chart(plot_style(fig, 345), use_container_width=True)
    st.caption("Gross and net sales are transaction-line metrics, not accounting profit. Distinct invoices count only positive purchases.")
    download_csv("Download monthly summary", trend, "monthly_summary.csv")


def products() -> None:
    page_title("02 / Revenue drivers", "Products & markets",
               "Compare best sellers, return exposure and revenue concentration without assuming product costs.")
    prod = product_sales(FILTERED, DATA["products"])
    geo = country_sales(FILTERED, DATA["geography"])
    if prod.empty:
        st.info("No product results for the current filters.")
        return
    first = prod.iloc[0]
    total_net = prod.net.sum()
    x, y, z = st.columns(3)
    x.metric("Products in selection", f"{len(prod):,}")
    y.metric("Units sold", f"{int(prod.units.sum()):,}")
    z.metric("Top product share", f"{100 * first.net / total_net:.1f}%" if total_net > 0 else "N/A")

    st.markdown("### Product performance")
    limit = st.slider("Products to compare", 5, 30, 10, step=5)
    subset = prod.head(limit).sort_values("net")
    chart = px.bar(subset, x="net", y="product_description", orientation="h",
                   color="net", color_continuous_scale=[[0, "#1d4b68"], [1, SEA]],
                   custom_data=["product_id", "units"],
                   labels={"net": "Net GBP", "product_description": ""})
    chart.update_traces(hovertemplate="%{y}<br>Net: £%{x:,.2f}<br>Item: %{customdata[0]}<br>Units: %{customdata[1]}<extra></extra>")
    chart.update_layout(coloraxis_showscale=False)
    chart.update_xaxes(tickprefix="£")
    st.plotly_chart(plot_style(chart, max(330, min(720, 75 + len(subset)*28))), use_container_width=True)

    l, r = st.columns(2)
    with l:
        st.markdown("### Gross vs credits by product")
        returns = prod[prod.returns.gt(0)].nlargest(12, "returns").copy()
        if returns.empty:
            st.info("No recorded returns in this selection.")
        else:
            stacked = go.Figure()
            for key, label, color in [("gross", "Gross", SKY), ("returns", "Credits", CORAL)]:
                stacked.add_bar(y=returns.product_description, x=returns[key], orientation="h",
                                name=label, marker_color=color)
            stacked.update_layout(barmode="group")
            stacked.update_xaxes(tickprefix="£")
            st.plotly_chart(plot_style(stacked), use_container_width=True)
    with r:
        st.markdown("### Market comparison")
        if not geo.empty:
            fig = px.bar(geo.head(12), x="country", y="net", color_discrete_sequence=[GOLD])
            fig.update_yaxes(tickprefix="£")
            st.plotly_chart(plot_style(fig), use_container_width=True)

    st.markdown("### Product-level detail")
    view = prod.rename(columns={"product_description": "Product", "gross": "Gross GBP",
                                "returns": "Credits GBP", "net": "Net GBP", "units": "Units"})
    st.dataframe(view, use_container_width=True, hide_index=True, height=280)
    download_csv("Download product analysis", prod, "product_analysis.csv")
    st.caption("The source dataset has no product categories, costs or margins. Negative net product totals are shown, not silently discarded.")


def customers() -> None:
    page_title("03 / Customer intelligence", "Customer retention & RFM",
               "Explore repeat purchase behavior, lifecycle segments and historical acquisition cohorts.")
    metrics = summary_metrics(FILTERED)
    buyers = period_buyers_with_segments(FILTERED, DATA["rfm"])
    a, b, c = st.columns(3)
    a.metric("Known buyers in selection", f"{metrics['buyers']:,}")
    b.metric("Repeat buyers in selection", f"{metrics['repeat_buyers']:,}")
    c.metric("Repeat-buyer rate", f"{metrics['repeat_rate']:.1f}%")
    st.caption("The repeat-buyer denominator is identified customers who purchased within the selected dates and countries; two or more distinct invoices count as repeat buyers.")

    left, right = st.columns(2)
    with left:
        st.markdown("### Snapshot RFM segments of selected buyers")
        by_segment = buyers.segment.fillna("Unclassified").value_counts().reset_index()
        by_segment.columns = ["segment", "customers"]
        if by_segment.empty:
            st.info("No identified purchasers in the current filter selection.")
        else:
            fig = px.bar(by_segment, x="customers", y="segment", orientation="h",
                         color="segment", color_discrete_sequence=[SEA, SKY, GOLD, CORAL, "#a78bfa", "#8b9bb0"])
            fig.update_layout(showlegend=False)
            st.plotly_chart(plot_style(fig), use_container_width=True)
    with right:
        st.markdown("### Orders per identified buyer")
        if buyers.empty:
            st.info("No identified purchasers in the current filter selection.")
        else:
            distribution = buyers.orders_in_selection.value_counts().sort_index().rename_axis("orders").reset_index(name="customers")
            fig = px.bar(distribution, x="orders", y="customers", color_discrete_sequence=[SKY])
            fig.update_xaxes(dtick=1)
            st.plotly_chart(plot_style(fig), use_container_width=True)

    st.markdown("### Monthly cohort retention · complete calendar months")
    st.info("Cohorts are precomputed across the entire chosen dataset and **do not change** with month or country filters. The final potentially partial month is excluded; blank cells mean the cohort had no observed window.")
    grid = cohort_grid(DATA["cohorts"])
    if grid.empty:
        st.warning("Insufficient complete-month data to display cohort retention.")
    else:
        if grid.shape[0] > 18:
            st.caption(f"Showing the latest 18 of {grid.shape[0]} acquisition cohorts for readability.")
            grid = grid.tail(18)
        fig = go.Figure(go.Heatmap(
            z=grid.to_numpy(dtype=float), x=[f"M+{n}" for n in grid.columns],
            y=grid.index.tolist(), zmin=0, zmax=100,
            colorscale=[[0, "#1c344f"], [0.5, "#177c82"], [1, "#35dfba"]],
            colorbar=dict(title="% retained", ticksuffix="%"),
            hovertemplate="Acquired %{y}<br>Age %{x}<br>Retention %{z:.1f}%<extra></extra>",
        ))
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(plot_style(fig, min(680, max(270, 70 + 25 * len(grid)))), use_container_width=True)
    st.caption("Cohort size is based on each customer's first valid purchase, and an active member must have a valid purchase in a complete calendar month. RFM segments are descriptive heuristics, not churn predictions.")
    left, right = st.columns(2)
    with left:
        download_csv("Download selected buyers", buyers, "buyer_segments.csv")
    with right:
        download_csv("Download historical cohorts", DATA["cohorts"], "cohort_retention.csv")


def recommendations() -> None:
    page_title("04 / Decision support", "Recommendations & risks",
               "Signals from observed transactions, with questions to test before taking action.")
    k = summary_metrics(FILTERED)
    prod = product_sales(FILTERED, DATA["products"])
    highest = prod.head(1)
    top_label = str(highest.product_description.iloc[0]) if not highest.empty else "N/A"
    top_share = 100 * highest.net.iloc[0] / k["net"] if not highest.empty and k["net"] > 0 else 0.0
    top_3_share = 100 * prod.head(3).net.sum() / k["net"] if k["net"] > 0 else 0.0
    a, b, c, d = st.columns(4)
    a.metric("Credit / gross", f"{k['return_rate']:.1f}%")
    b.metric("Largest product's net share", f"{top_share:.1f}%" if k["net"] > 0 else "N/A")
    c.metric("Top 3 products' net share", f"{top_3_share:.1f}%" if k["net"] > 0 else "N/A")
    d.metric("Anonymous gross sales share", f"{k['unidentified_gross_rate']:.1f}%")

    st.markdown("### Suggested investigations")
    ideas = [
        ("Monitor returns", f"Recorded credits are {money(k['returns'])} against {money(k['gross'])} gross sales ({k['return_rate']:.1f}%).",
         "Break returns down by product and country, check data quality, and verify whether any apparent pattern persists in complete periods.",
         "Credit / gross ratio by product, month and market."),
        ("Review product concentration", f"The highest net contributor is {top_label} ({top_share:.1f}% of current net sales where positive).",
         "Test whether reliance on a few products presents an operational risk; compare seasonality and repeat sales before changing inventory.",
         "Top-1 and top-3 net sales share over time."),
        ("Investigate customer retention", f"{k['repeat_buyers']:,} of {k['buyers']:,} identified buyers made at least two purchase invoices in the selected slice.",
         "Compare historical complete-month cohorts and evaluate any retention intervention using a controlled experiment.",
         "Repeat-buyer rate and full-month cohort retention."),
        ("Improve buyer attribution", f"Anonymous purchase lines represent {k['unidentified_gross_rate']:.1f}% of gross sales in this slice.",
         "Check why customer IDs are missing before drawing conclusions about buyer-level performance.",
         "Share of gross sale value from lines missing customer IDs."),
    ]
    for idx, (title, evidence, action, monitoring) in enumerate(ideas, 1):
        with st.container(border=True):
            st.markdown(f"**{idx:02d} · {title}**")
            st.write(evidence)
            st.caption(f"Investigate: {action}  |  Track: {monitoring}")
    st.warning("These are descriptive decision prompts, not proof of cause, validated churn predictions or claims of guaranteed revenue growth.")

    st.markdown("### Action tracker · exportable starting point")
    actions = pd.DataFrame([{"Theme": title, "Observed signal": evidence, "Suggested follow-up": action,
                             "Measure to monitor": monitoring} for title, evidence, action, monitoring in ideas])
    st.dataframe(actions, use_container_width=True, hide_index=True)
    download_csv("Download investigation ideas", actions, "business_investigations.csv")


def quality() -> None:
    page_title("05 / Audit and provenance", "Data quality & SQL checks",
               "See which records were retained, what was rejected and which checks actually ran.")
    logs = DATA["logs"]
    qa = logs.get("data_quality", {})
    run = logs.get("sql_execution_log", {})
    a, b, c, d = st.columns(4)
    a.metric("Source rows", f"{int(qa.get('original_rows', 0)):,}")
    b.metric("Accepted", f"{int(qa.get('accepted_rows', 0)):,}")
    c.metric("Rejected", f"{int(qa.get('rejected_rows', 0)):,}")
    passed_sql = sum(isinstance(v, dict) and v.get("status") == "passed" for v in run.values())
    sql_total = sum(isinstance(v, dict) and "status" in v for v in run.values())
    d.metric("SQL query files passed", f"{passed_sql}/{sql_total}")

    if qa.get("passed") is True:
        st.success("Warehouse pre-load data-quality validation passed for this prepared dataset.")
    elif qa:
        st.error("Warehouse data-quality validation reported failures. Inspect the details before using these figures.")
    else:
        st.warning("No validation log found for this data source.")

    left, right = st.columns(2)
    with left:
        st.markdown("### Rejected-record reasons")
        rejected = DATA["rejected"]
        if rejected.empty or "rejection_reason" not in rejected:
            st.info("No rejected records or rejection reasons are available.")
        else:
            reasons = rejected.rejection_reason.value_counts().rename_axis("reason").reset_index(name="records")
            fig = px.bar(reasons, x="records", y="reason", orientation="h", color_discrete_sequence=[CORAL])
            st.plotly_chart(plot_style(fig), use_container_width=True)
    with right:
        st.markdown("### Programmatic validations")
        checks = logs.get("metric_reconciliation", {})
        st.markdown("**Pre-load checks**")
        values = qa.get("checks", {})
        if values:
            st.dataframe(pd.DataFrame([{"check": k, "passed": str(v)} for k, v in values.items()]),
                         use_container_width=True, hide_index=True, height=210)
        else:
            st.info("No pre-load check details were stored.")
        with st.expander("Python and SQL reconciliation results", expanded=False):
            st.json(checks)

    st.markdown("### Executed SQL query log")
    sql_list = pd.DataFrame([{
        "query": k, "status": v.get("status", "unknown"), "result rows": v.get("rows", "—"),
    } for k, v in run.items() if isinstance(v, dict) and "status" in v])
    if not sql_list.empty:
        st.dataframe(sql_list, use_container_width=True, hide_index=True)
    else:
        st.info("No SQL query log available.")

    with st.expander("Source profile and cleaning policy"):
        st.json(logs.get("source_profile", {}))
        st.json(logs.get("cleaning_decisions", {}))
    st.markdown("### Inspect the transaction lines")
    st.dataframe(FILTERED.head(500), use_container_width=True, hide_index=True, height=270)
    st.caption("The table shows at most 500 currently selected lines. All rejected-record auditing comes from the full prepared source, not the sidebar filter selection.")
    if not DATA["rejected"].empty:
        download_csv("Download rejected records", DATA["rejected"], "rejected_records.csv")




def sql_explorer() -> None:
    page_title("06 / Reproducible analytics", "SQL explorer",
               "Browse the SQL that was executed and its saved results, not hardcoded sample tables.")
    st.info("These SQL results are from the full prepared source, so they do not respond to the country/month sidebar filters. The query text is shared by demo and real-data runs.")
    sql_files = sorted((ROOT / "sql").glob("[0-9][0-9]_*.sql"))
    if not sql_files:
        st.warning("No executable SQL files were found in the repository.")
        return
    selected = st.selectbox("Analytical query", [p.name for p in sql_files])
    query_path = ROOT / "sql" / selected
    result_path = folder / "data/outputs" / (query_path.stem + ".csv")
    audit = DATA["logs"].get("sql_execution_log", {}).get(selected, {})
    c1, c2, c3 = st.columns(3)
    c1.metric("Execution status", audit.get("status", "Not run"))
    c2.metric("Result rows", int(audit.get("rows", 0)))
    c3.metric("Result columns", len(audit.get("columns", [])))
    if result_path.exists():
        frame = pd.read_csv(result_path)
        st.markdown("### Saved query result")
        st.dataframe(frame, use_container_width=True, hide_index=True, height=390)
        download_csv("Download query result", frame, query_path.stem + ".csv")
    else:
        st.warning("The query output is missing. Run the Python pipeline before inspecting it.")
    with st.expander("View the executed SQL", expanded=True):
        st.code(query_path.read_text(encoding="utf-8"), language="sql")
    st.caption("All query CSVs and their execution log were produced by scripts/run_sql_checks.py. This interface is read-only.")


def methodology() -> None:
    page_title("07 / Project walkthrough", "Methods & project evidence",
               "Understand the business definitions, analytical design and remaining scope.")
    st.markdown("### End-to-end pipeline")
    stages = ["Original source or SYNTHETIC fixture", "Schema validation and profiling",
              "Accept / reject lines with reasons", "Star-model dimensions and facts",
              "SQLite warehouse + 10 executed queries", "Python vs SQL metric reconciliation",
              "Customer and cohort analysis", "Interactive dashboard / Power BI handoff"]
    for n, stage in enumerate(stages, 1):
        st.markdown(f"**{n:02d}.** {stage}")
    m1, m2, m3 = st.columns(3)
    m1.metric("SQL reconciliations", sum(bool(v) for v in DATA["logs"].get("metric_reconciliation", {}).values()))
    m2.metric("SQL analysis files", len(list((ROOT / "sql").glob("[0-9][0-9]_*.sql"))))
    m3.metric("Fact rows loaded", f"{len(DATA['fact']):,}")
    st.markdown("### KPI definitions")
    definitions = pd.DataFrame([
        ("Gross line sales", "Sum of positive purchase line amounts"),
        ("Credits / returns", "Absolute value of negative-quantity credit lines"),
        ("Net line sales", "Gross sales minus credits, before unknown taxes/shipping"),
        ("Sale invoices", "Distinct positive-purchase invoice identifiers"),
        ("Known customers", "Distinct identified buyers with valid positive sales"),
        ("Repeat-buyer rate", "Identified buyers with 2+ distinct sale invoices / known buyers"),
        ("Cohort retention", "Customers purchasing in full calendar month / acquisition cohort size"),
        ("RFM", "Heuristic recency/frequency/monetary ranking at last invoice + 1 day"),
    ], columns=["Measure", "Interpretation"])
    st.dataframe(definitions, hide_index=True, use_container_width=True)
    st.markdown("### Methodology and source limitations")
    options = [("Methodology", ROOT / "reports/methodology.md"),
               ("Limitations", ROOT / "reports/limitations.md"),
               ("Power BI build guide", ROOT / "powerbi/README.md"),
               ("How to reproduce", ROOT / "STREAMLIT_DEMO.md")]
    for title, path in options:
        with st.expander(title):
            st.markdown(path.read_text(encoding="utf-8"))
    st.warning("Demo metrics are synthetic. The full original UCI dataset and a validated Power BI Desktop .pbix are not included. This app is an analytical demo, not a deployed production service.")


# Source + global page state: all seven views use the same filtered fact rows.
st.sidebar.markdown("## RETAIL<span style='color:#38d9bb'>LENS</span>", unsafe_allow_html=True)
st.sidebar.caption("Revenue • customers • decision intelligence")
st.sidebar.divider()
options = {"Synthetic demo (included)": DEMO}
if (REAL / "data/processed/fact_sales.csv").exists():
    options["Real dataset (local pipeline output)"] = REAL
source_name = st.sidebar.radio("Data source", list(options), index=0)
folder = options[source_name]
required = ["fact_sales.csv", "dim_product.csv", "dim_geography.csv", "customer_rfm.csv", "cohort_retention.csv", "rejected_records.csv"]
paths = [folder / "data/processed" / fname for fname in required]
missing = [p.name for p in paths if not p.exists()]
if missing:
    st.error(f"Missing pipeline outputs: {', '.join(missing)}")
    st.code("python scripts/run_pipeline.py --demo", language="bash")
    st.stop()

try:
    signature = tuple(int(p.stat().st_mtime_ns) for p in paths)
    DATA = load_data(str(folder), signature)
except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
    st.error(f"Cannot load prepared data: {exc}")
    st.stop()

FACT = DATA["fact"]
FACT = FACT.merge(DATA["geography"][['geography_id', 'country']],
                  on="geography_id", how="left", validate="many_to_one")
all_months = sorted(FACT.month_key.dropna().unique().tolist())
all_countries = sorted(FACT.country.dropna().unique().tolist())

st.sidebar.markdown("### Global filters")
SELECTED_MONTHS = st.sidebar.multiselect("Transaction months", all_months, default=all_months)
SELECTED_COUNTRIES = st.sidebar.multiselect("Countries", all_countries, default=all_countries)
FILTERED = FACT.loc[FACT.month_key.isin(SELECTED_MONTHS) & FACT.country.isin(SELECTED_COUNTRIES)].copy()
st.sidebar.caption(f"{len(FILTERED):,} transaction lines in current selection")
st.sidebar.divider()
if source_name.startswith("Synthetic"):
    st.sidebar.warning("SYNTHETIC DEMO · not real business results")
else:
    st.sidebar.info("Processed dataset · verify source attribution")
st.sidebar.caption("No live business API. No account needed. Figures are computed from your existing CSV outputs.")

navigation = st.navigation([
    st.Page(overview, title="Executive overview", icon="📊", default=True),
    st.Page(products, title="Products & markets", icon="🛍️"),
    st.Page(customers, title="Customer retention", icon="👥"),
    st.Page(recommendations, title="Recommendations", icon="🎯"),
    st.Page(quality, title="Data quality & SQL", icon="🔍"),
    st.Page(sql_explorer, title="SQL explorer", icon="🗄️"),
    st.Page(methodology, title="Methods & evidence", icon="🧭"),
])

if source_name.startswith("Synthetic"):
    st.markdown('<span class="tag">● DEMO MODE · SYNTHETIC TRANSACTIONS</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="tag">● LOCAL PROCESSED DATA</span>', unsafe_allow_html=True)
navigation.run()
st.markdown("---")
st.caption("RetailLens | Historical descriptive analysis · © project showcase. Credit amounts reduce net sales. No fabricated profitability or causal claims.")
