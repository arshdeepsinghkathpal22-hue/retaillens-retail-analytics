"""Evidence-driven Markdown summaries and minimal reproducible charts."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def create_reports(out_root: Path, fact: pd.DataFrame, rejected: pd.DataFrame,
                   profile: dict, cleaning: dict, validity: dict, frames: dict,
                   cohort_through: str, demo: bool) -> None:
    report_dir = out_root / "reports"
    chart_dir = report_dir / "figures"
    chart_dir.mkdir(parents=True, exist_ok=True)
    label = "SYNTHETIC TEST FIXTURE — NOT BUSINESS EVIDENCE" if demo else "USER-SUPPLIED TRANSACTION DATA"
    rules = "\n".join(f"| {r['reason']} | {r['excluded']:,} |" for r in cleaning["rules"])
    (report_dir / "data_quality_report.md").write_text(f"""# Data quality report

**Source status:** {label}

| Check | Count |
|---|---:|
| Raw rows | {len(fact) + len(rejected):,} |
| Accepted rows | {len(fact):,} |
| Rejected rows | {len(rejected):,} |
| Exact duplicate-looking source rows retained | {cleaning['duplicate_rows_flagged_not_removed']:,} |
| Returns missing cancellation marker | {cleaning['returns_without_credit_prefix']:,} |
| Missing customer IDs in source | {profile['missing'].get('CustomerID',0):,} |
| High-quantity IQR flags (not deleted) | {profile['suspected_high_quantity_outliers']:,} |
| High-price IQR flags (not deleted) | {profile['suspected_high_unit_price_outliers']:,} |

## Rejection reasons

| Rule | Excluded rows |
|---|---:|
{rules}

## Warehouse quality gate

{validity['checks']}

Source invoice numbers repeat naturally across invoice lines. They are not duplicate business keys by themselves. Duplicate-looking complete lines are retained because the source provides no line identifier. Inspect `rejected_records.csv` before revising any rule. Revenue includes priced returns; zero-price and malformed records are excluded from priced-sales metrics.
""", encoding="utf-8")

    if fact.empty:
        return
    gross = fact.gross_sales.sum()
    ret = fact.return_amount.sum()
    net = fact.net_sales.sum()
    orders = fact.loc[fact.event_type == "sale", "invoice_no"].nunique()
    buyers = fact.loc[fact.event_type == "sale", "customer_id"].nunique()
    active = fact.loc[fact.event_type == "sale"].groupby("customer_id").invoice_no.nunique()
    repeat_rate = (active.ge(2).sum() / len(active) * 100) if len(active) else 0
    rfm = frames["customer_rfm"]
    cohort = frames["cohort_retention"]
    country = fact.groupby("country").net_sales.sum().sort_values(ascending=False)
    segments = rfm.segment.value_counts() if not rfm.empty else pd.Series(dtype=int)
    monthly = fact.groupby("month_key", as_index=False).net_sales.sum()
    first_month, last_month = monthly.month_key.iloc[0], monthly.month_key.iloc[-1]
    max_month = monthly.loc[monthly.net_sales.idxmax(), "month_key"]
    cohort1 = cohort.loc[cohort.months_since_acquisition == 1] if not cohort.empty else cohort
    if len(cohort1):
        weighted_retention = 100 * cohort1.active_customers.sum() / cohort1.cohort_size.sum()
        retention_text = f"Month-1 cohort retention (weighted across observable cohorts): **{weighted_retention:.2f}%**."
    else:
        retention_text = "Month-1 retention cannot be computed from enough fully observed cohort months."
    top_country = f"{country.index[0]} (£{country.iloc[0]:,.2f})" if len(country) else "Unavailable"
    segment_text = f"{segments.index[0]} ({segments.iloc[0]:,} identified buyers)" if len(segments) else "Unavailable"

    demo_note = ("**SYNTHETIC TEST FIXTURE — DEMONSTRATION ONLY.** All numbers on this page come from a deliberately small synthetic test fixture. "
                 "They must not be copied into a portfolio as empirical findings.\n\n") if demo else (
                 "**Data provenance note:** Results are computed from the locally supplied input file; inspect its origin and license before publicly treating it as the canonical UCI release.\n\n")
    text = f"""# Business insights and next actions

{demo_note}## Executive summary

| Metric | Observed value |
|---|---:|
| Gross merchandise line sales proxy | £{gross:,.2f} |
| Credit/return line amount | £{ret:,.2f} |
| Net line sales proxy | £{net:,.2f} |
| Unique sale invoices | {orders:,} |
| Identified purchasing customers | {buyers:,} |
| Gross average sale invoice value | £{gross / orders if orders else 0:,.2f} |
| Repeat-customer rate among identified buyers | {repeat_rate:.2f}% |

**Interpretation:** These are transaction-line totals, not tax-adjusted accounting revenue. Refunds may be unmatched to the original sale. No cost-of-goods or marketing data is supplied.

## Revenue trend

Invoices dated **{first_month} through {last_month}** were loaded. The month with the highest computed net line sales is **{max_month}**; check its completeness before comparing it with other months. The source's final observed month is conservatively treated as incomplete for cohort calculations.

## Customer retention

{retention_text} Only named customers and valid positive sale invoices count as purchases. Cohorts through **{cohort_through}** are used; later months are censored, not recorded as zeros.

## Segmentation

The largest observed RFM segment is **{segment_text}**. RFM is a rule-based ordering at snapshot date **{cleaning['reference_date']}**, not a predictive churn probability.

## Geography

The leading country by net line sales is **{top_country}**. Geography is inferred from invoice customer country; it is not a shipping-address field. Products have no supplied category hierarchy.

## Decisions to test, not promises

1. **Retention:** Review the At Risk and Hibernating segments for a carefully designed, permission-based re-engagement experiment. Measure incremental repeat-purchase rate against a control group.
2. **Returns:** Examine product and country return-to-gross ratios and inspect whether credit lines match known errors or fulfillment issues. Measure return ratio over the next comparable period.
3. **Concentration:** Review largest customers/products and diversify exposure only after assessing seasonality and contract characteristics.

No expected revenue uplift is asserted. These are hypotheses to investigate, not measured causal effects.

## Limitations

- No reliable cost, gross margin, marketing spend, acquisition source, shipment value, product category or discount fields.
- Anonymous transactions are included in sales but excluded from customer KPIs.
- The dataset's final calendar month may be partial and must not be treated as a full-month retention denominator.
- Invoice credits are not linked to original invoices; net sales are a transparent proxy.
- This is historical observational data, not an experiment and not current business performance.
- Cancellations are estimated from source convention; inspect edge cases.

Supporting tables: `data/outputs/02_revenue_analysis.csv`, `04_customer_segmentation.csv`, `05_cohort_retention.csv`, `08_executive_summary.csv`, and `10_returns_and_geography.csv`.
"""
    (report_dir / "business_insights.md").write_text(text, encoding="utf-8")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(monthly["month_key"], monthly["net_sales"], marker="o")
    ax.set_title("Monthly net line sales (GBP)" + (" — SYNTHETIC FIXTURE" if demo else ""))
    ax.set_ylabel("GBP")
    ax.set_xlabel("Invoice month")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(chart_dir / "monthly_net_sales.png", dpi=145)
    plt.close(fig)
    if not segments.empty:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        segments.plot.bar(ax=ax)
        ax.set_title("RFM segment customer count" + (" — SYNTHETIC FIXTURE" if demo else ""))
        ax.set_ylabel("Customers")
        ax.set_xlabel("Heuristic segment")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(chart_dir / "rfm_segments.png", dpi=145)
        plt.close(fig)
