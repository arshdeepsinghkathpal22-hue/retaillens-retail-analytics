# Power BI Desktop implementation guide

**Status:** Import-ready data, four DAX measure files, model plan, and detailed design are included. **No `.pbix` file or genuine Power BI screenshot was built/tested here**, because Power BI Desktop cannot run in this environment.

## Import checklist

1. Run the real dataset locally using `python scripts/run_pipeline.py --input "data/raw/Online Retail.xlsx"`.
2. Open Power BI Desktop → **Get data → Text/CSV**. Import from `data/processed/`:
   - `fact_sales.csv` → **FactSales**
   - `dim_customer.csv` → **DimCustomer**
   - `dim_product.csv` → **DimProduct**
   - `dim_geography.csv` → **DimGeography**
   - `dim_date.csv` → **DimDate**
   - `customer_rfm.csv` → **CustomerRFM**
   - `cohort_retention.csv` → **CohortRetention**
3. In Power Query, set IDs (`invoice_no`, `product_id`, `customer_id`) as **Text**, geography IDs and scores as **Whole number**; sales amounts as **Decimal number** or **Fixed decimal** for relevant measures; `DimDate[date_key]`, `FactSales[date_key]`, `DimCustomer[first_purchase_date]` as **Date**. Leave `FactSales[invoice_date]` as Date/Time. Preserve invoice identifiers as text even if entirely numeric.
4. Create the **four** active relationships from `model/relationships.md`. Use **single** filter direction and one-to-many cardinality. Avoid connecting `CustomerRFM` or `CohortRetention` as a second filter path to facts.
5. Mark DimDate as the date table. Verify there is exactly one row per `DimDate[date_key]` with no gaps.
6. Create a measure group (or place measures on FactSales). Copy each named expression from `dax/*.dax` **one measure at a time**. These files are a source library, not a directly executable Power BI deployment script.
7. Set amount measures to currency **GBP (£)**, percentage measures to Percentage (1–2 decimals). In DAX measures percentage values are **ratios** and need percentage formatting, unlike SQL outputs which are multiplied by 100.
8. For cohort heatmap, use `CohortRetention[cohort_month]` rows, `months_since_acquisition` columns, and `[Cohort Retention %]` values. Disable the top-level Date slicer influencing this matrix (it is a fixed cohort snapshot).
9. Verify four drill tests: invoice count versus line count; anonymous sales retained; a credit lowers net sales; date slicer affects FactSales KPI cards but does not rewrite historical RFM snapshot scores.
10. Save the Power BI report as `powerbi/customer_revenue_retention.pbix` **locally**, then add genuine screenshots in `powerbi/screenshots/` before claiming the dashboard has been implemented.

## Page specifications

### Page 1 — Executive Overview

**Top row:** `Net Line Sales GBP`, `Gross Line Sales GBP`, `Sale Invoices`, `Known Purchasing Customers`, `Gross Average Order Value GBP`. Subtitle: *net is a transaction-line proxy; includes credited lines*. **Charts:** monthly line from DimDate[year_month] → `[Net Line Sales GBP]`; top countries bar from DimGeography[country]; KPI comparison card `[MoM Net Sales Change %]`.

**Slicers:** DimDate year/month/date, country, optional product. Exclude the incomplete final month for fair monthly comparison; net sales can still be viewed with it if clearly labelled.

### Page 2 — Product and Revenue

**Charts:** top 10 products by `[Net Line Sales GBP]` with product description + SKU, top revenue contribution with `[Product Share of Selected Net Sales %]`, gross vs returns by month, country-level `Return to Gross Sales %`, product drill-through table including units and return amounts.

**Caveat:** UCI provides no categories, profit, or costs. Do not add fictional categories, margins, or discount visualizations.

### Page 3 — Customer Retention & RFM

**Cards:** `[Known Purchasing Customers]`, `[Period Repeat Buyers]`, `[Period Repeat Buyer Rate %]`, `[Returning Buyers]`, `[New Buyers]`. **Charts:** segment customer counts from `CustomerRFM`, a `CohortRetention` heatmap, identified-customer concentration table, sales by RFM segment via `[Snapshot Segment Net Sales GBP]`.

**Tooltip:** *RFM segment labels are based on the final historical observation date and do not rescore when users move the date slicer.* **Cohort tooltip:** *month 0 = acquisition, percentages computed on distinct known customers who purchased in that month; final partial month excluded*.

### Page 4 — Recommendations & Risks

**Cards:** return-to-gross share; identified-customer sales concentration; segment shares. **Narrative:** largest product/customer concentration, customer-at-risk slice, credit and return hypotheses. Link to `reports/business_insights.md`; measure control-group repeat purchase and future return ratio instead of promising an uplift. Add a *Limitations* text panel.

## Interactions and accessibility

- Use a consistent 16:9 canvas, plain white or neutral background, high-contrast text, one restrained accent color and consistent GBP/percentage formatting.
- Add concise alt text. Do not use color alone for negative sales; label values and direction explicitly.
- Keep slicers in a predictable header position. For cohort/RFM fixed snapshots, use visible badges or explanatory subtitles **inside Power BI** to avoid interpreting them as dynamic date-filter outputs.
- Use tooltip pages to explain denominator and cancellation treatment. Test each slicer on totals and on one known invoice.

## Visual validation record (to complete in Desktop)

- [ ] Import all seven CSV files
- [ ] Set data types / mark date table
- [ ] Verify dimension cardinality and active filter directions
- [ ] Enter and format DAX measures
- [ ] Validate gross / return / net numbers against SQL summary
- [ ] Test period repeat buyers and first-purchase new buyers
- [ ] Verify cohort month 0 is 100% in the matrix
- [ ] Validate RFM segment totals against `04_customer_segmentation.csv`
- [ ] Build and review all four pages
- [ ] Save an actual `.pbix` and export genuine screenshots
- [ ] Record Desktop version and test results
