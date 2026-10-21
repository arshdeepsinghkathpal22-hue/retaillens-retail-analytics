# Data analytics project: interview prep

## 90-second walkthrough

**Business problem.** Retail invoice lines do not automatically translate to reliable KPIs. Orders, returns and customers need consistent definitions before a dashboard is useful.

**Source.** UCI Online Retail (Chen, 2015), 2010–2011, in GBP. The original file was not obtainable during the initial build, so only synthetic demo outcomes are currently verified. The real dataset must be run locally before presenting empirical findings.

**Pipeline.** I load raw Excel/CSV without changing the source, profile source quality, reject malformed/non-commercial lines with an audit trail and separate positive sales from negative returns. I keep anonymous purchases for revenue but not customer retention.

**SQL and modeling.** One fact row per accepted invoice line, dimensions for date, product, customer and country. I independently calculate monthly net sales, window trends, customer RFM, cohort retention, returns and concentration with 10 SQL query files.

**Power BI.** The import plan uses single-direction star joins, a proper date table, DAX KPI measures and fixed-snapshot cohort/RFM tables. The desktop dashboard is not yet implemented.

**Strongest demonstrated result.** In the **synthetic** demo, all 10 SQLite query files executed, and Python versus SQL metric checks passed. This is an engineering validation, not a UCI business insight.

**Limits.** No costs/profit, product categories, matched refund links, acquired-channel data, causal attribution or real-time churn predictions. Last observed cohort month is excluded as partial.

**Next step.** Run official UCI workbook, validate accounting conventions and real findings, implement Power BI report, then evaluate recommendations with controlled experiments.

## 35 technical interview questions and answers

### Python, pandas and data quality

1. **Why use source row numbers?** An invoice has multiple lines; source row numbers provide an auditable within-file line reference, not a permanent globally unique transaction key.
2. **Why not drop identical records?** Identical looking items may be legitimate; the dataset lacks stable line IDs. I flag lookalikes and preserve them until business rules support deduplication.
3. **How do you parse date fields?** `pd.to_datetime(..., errors='coerce', format='mixed')`, then reject failed parses explicitly.
4. **Why use nullable customer IDs?** Invented identities distort distinct buyer, cohort and RFM denominators; unknowns remain part of sales totals only.
5. **How are cancellations identified?** Source convention says `C` prefix; I also capture negative quantities and flag cases where the two signals disagree.
6. **How do you ensure repeatability?** Deterministic transforms, immutable source, fixed RFM snapshot date, canonical output paths and identical results on a second run.
7. **How do you reject invalid records?** Every rejection has one explicit priority-ordered reason in `rejected_records.csv` and summary counts in JSON.
8. **What is idempotence here?** Re-running the pipeline with the same source replaces derived tables and produces the same metrics without duplicate append records.
9. **Why use vectorized pandas?** Validation, flags and revenue columns process many rows without Python loops. Only tiny grouped RFM classification uses a row-wise rule function.
10. **What if a file is empty?** The cleaning layer returns empty shaped outputs; the full analytics pipeline exits with a clear error before claiming useful measures.

### SQL

11. **What is the fact table grain?** One priced, accepted invoice line, uniquely keyed by source row within a source file.
12. **Why a star schema?** Dimensions make slicing easy and avoid repeating descriptive attributes inside every BI calculation.
13. **How do you count orders?** `COUNT(DISTINCT CASE WHEN event_type='sale' THEN invoice_no END)` rather than counting lines.
14. **What is a CTE?** A named query block that organizes calculations into readable, testable steps without persisting an intermediate table.
15. **What is a window function?** An analytic function like `LAG` or `RANK` that evaluates within a partition while preserving individual result rows.
16. **RANK versus DENSE_RANK?** Both share ranks on ties, but `RANK` leaves gaps after ties and `DENSE_RANK` does not.
17. **When is LAG useful?** It retrieves a prior monthly metric for period-on-period comparisons without self-joining a summary to itself.
18. **What is the difference between ROW_NUMBER and COUNT DISTINCT?** The first numbers result rows; the second counts distinct keys in an aggregation.
19. **How is return value represented?** Return amounts are positive in a return column and negative in net sales, so gross and credits reconcile.
20. **Why NULLIF in percentages?** Denominators of zero return NULL rather than cause divide-by-zero or imply a made-up valid rate.
21. **How do cohort SQL queries avoid false zeros?** The query materializes only months up to the last completed observation month; within that window, left joins fill truly observed zeros.
22. **How is first purchase established?** Minimum month index across valid positive sales with known customer IDs; credit-only activity cannot create a cohort.
23. **How do you score RFM ties?** `PERCENT_RANK` uses equal ranks for ties; multiply the rank percentile by four and invert to derive tiers 5→1.
24. **Why inspect query plans?** For large fact tables, indexes on date, customer, SKU and geography can avoid unnecessary scans, but plans should be measured before tuning.
25. **Is this executed in PostgreSQL?** No. SQL is designed to be portable, but automated runs execute against SQLite. A PostgreSQL DDL is provided for later validation.

### Power BI, DAX and modeling

26. **What is a DAX measure?** An expression evaluated in report filter context; a calculated column is materialized per row at refresh time.
27. **What is row context vs filter context?** Row context selects a current row during iteration; filter context constrains which rows a measure aggregates. `CALCULATE` can modify filter context.
28. **Why use a date dimension?** A continuous unique Date column enables reliable time intelligence and clear date slicers.
29. **How do you avoid circular filters?** Use one-direction dimension-to-fact relationships, and keep snapshot RFM/cohort tables detached rather than bidirectional many-to-many joins.
30. **What is TREATAS used for here?** It applies selected RFM customer IDs to DimCustomer for net-sales measures without making a physically ambiguous relationship.
31. **Why might a cohort heatmap ignore the date slicer?** Cohorts are precomputed for a fixed historical window; filtering FactSales afterward cannot correctly recompute acquisition populations.
32. **How do you validate a measure?** Compare the same period and filters against an independently executed SQL value; verify date types, relationship direction and blank IDs.

### Business reasoning

33. **Is a large revenue figure a large profit figure?** No; without reliable cost data profit or margin cannot be calculated.
34. **Does an At Risk segment predict churn?** No. It is a heuristic based on historic recency/frequency/monetary values, not a calibrated probability or causal diagnosis.
35. **What is your top business recommendation?** Start with a hypothesis and success metric, such as a consent-based control-group retention test; do not claim uplift until a valid experiment supports it.

## Two practical follow-up checks

- **Credit scenario:** Choose one C-prefixed transaction, verify it adds positive `return_amount` and negative `net_sales`, but does not add to valid sale-invoice count.
- **Cohort scenario:** Manually list a known customer's qualifying purchases and verify their first purchase month, month indices and eligible periods against SQL 05 and Python cohort output.

## Honest portfolio wording

You can say: *I implemented and tested an auditable retail analytics pipeline and wrote the Power BI handoff files.* Do not say: *I built and deployed a Power BI dashboard, analyzed the full canonical source, or increased retailer revenue* until those actions are actually complete and verified.
