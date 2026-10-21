# Business insights and next actions

**SYNTHETIC TEST FIXTURE — DEMONSTRATION ONLY.** All numbers on this page come from a deliberately small synthetic test fixture. They must not be copied into a portfolio as empirical findings.

## Executive summary

| Metric | Observed value |
|---|---:|
| Gross merchandise line sales proxy | £384,746.26 |
| Credit/return line amount | £5,619.36 |
| Net line sales proxy | £379,126.90 |
| Unique sale invoices | 3,055 |
| Identified purchasing customers | 320 |
| Gross average sale invoice value | £125.94 |
| Repeat-customer rate among identified buyers | 92.19% |

**Interpretation:** These are transaction-line totals, not tax-adjusted accounting revenue. Refunds may be unmatched to the original sale. No cost-of-goods or marketing data is supplied.

## Revenue trend

Invoices dated **2024-01 through 2025-09** were loaded. The month with the highest computed net line sales is **2025-08**; check its completeness before comparing it with other months. The source's final observed month is conservatively treated as incomplete for cohort calculations.

## Customer retention

Month-1 cohort retention (weighted across observable cohorts): **49.69%**. Only named customers and valid positive sale invoices count as purchases. Cohorts through **2025-08** are used; later months are censored, not recorded as zeros.

## Segmentation

The largest observed RFM segment is **Loyal Customers (100 identified buyers)**. RFM is a rule-based ordering at snapshot date **2025-10-01**, not a predictive churn probability.

## Geography

The leading country by net line sales is **United Kingdom (£236,988.89)**. Geography is inferred from invoice customer country; it is not a shipping-address field. Products have no supplied category hierarchy.

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
