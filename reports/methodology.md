# Methodology, metrics, and decisions

## Business questions

How do net line sales change by month and product? Which countries and identifiable customers account for sales? How much do credit lines offset gross sales? Who repeats purchases? What do acquisition cohorts and recency-frequency-monetary segments show?

## Scope and inputs

- UCI Online Retail (CC BY 4.0), source documentation linked in `data/README.md`.
- Original data has invoice **lines**, not a guaranteed immutable line item ID, product category, company cost, discounts, shipping or acquisition channel.
- The sales analysis covers accepted priced transaction lines; customer analysis covers known customer identifiers with at least one valid positive sale.
- Each output records the input SHA-256, as-of reference date, and last complete cohort calendar month.

## Cleaning decision log

1. Keep the raw source in `data/raw/` unchanged. Add `source_row` as an audit key. Exact duplicate-looking rows are **flagged but retained**: two visually identical items within one invoice cannot safely be distinguished from accidental duplication without a source line key.
2. Reject blank invoice or stock code, unparseable date, missing or fractional quantity, zero quantity, negative/blank price, and zero-price noncommercial lines. Rejected source rows remain available with a reason.
3. Use `InvoiceNo` starting with C or negative quantity to identify credited lines. A C-prefixed invoice with positive quantity is rejected as a contradiction; negative-quantity lines without C are retained as returns but flagged. Do **not** silently drop returns.
4. No currency conversions are assumed; unit prices are in sterling (source metadata). `Quantity × UnitPrice` is rounded to two decimals *per line*. Sources do not report tax, fulfillment or original-refund matching; treat numbers as transparent revenue proxies.
5. Missing `CustomerID` remains null. Anonymous sales count in revenue but do **not** count toward identified-customer retention, repeat rate or RFM.
6. Product labels may vary. Retain the most frequent available description for each product ID, with deterministic alphabetic tie breaking. Country null/blank is reported as **Unknown**, not a real location.
7. RFM snapshot date is max observed invoice date + one day, **not** the current date. Scoring uses equal-value ties: best values score 5, worst 1, using rank position divided by n-1; single-customer cases score 3.
8. Cohorts are first observed *valid positive purchases*. Month 0 is acquisition. A buyer is active in a month only if at least one qualifying sale invoice exists. The final observed calendar month is always excluded (conservative partial-month censoring); omitted future months are not zeros. All earlier calendar months in a cohort lifespan are filled with observed values or observed zero.

## Metric dictionary

| Metric | Operational formula | Return handling | Missing customer IDs | Implementation |
|---|---|---|---|---|
| Gross line sales (GBP) | Σ positive-priced sale-line quantity × unit price | Credits not in gross | Included | `gross_sales` in cleaning; SQL 08; DAX base |
| Return line amount (GBP) | Σ absolute credited quantity × unit price | Positive amount | Included | `return_amount`; SQL 08; DAX base |
| Net line sales (GBP) | Gross line sales − return line amount | Credits subtracted, original sale may be outside window | Included | `net_sales`; SQL 08; DAX base |
| Valid sale orders | Count distinct `invoice_no` from valid **sale** lines | Credit-only invoices excluded | Included | SQL 08; DAX `Sale Invoices` |
| Identified buyers | Distinct non-null customers with ≥1 valid sale | Returns-only buyers excluded | Excluded | SQL 08; DAX `Known Purchasing Customers` |
| Units sold / returned | Sums separately from sale vs return lines | Separate columns | Included | SQL 08; DAX base |
| Gross AOV | Gross line sales / valid sale invoices | Credits not removed; net-per-sale-invoice is separate | Included | SQL 08; DAX base |
| Average net per identified buyer | Net sales associated with known IDs / distinct sale buyers | Credits netted, potentially including historical differences | Excluded | DAX base |
| Repeat buyer rate | Buyers with ≥2 distinct qualifying sale invoices / identified buyers | Returns do not add purchases | Excluded | pandas reporting; DAX customer (period-scoped) |
| MoM net change | (current month net − prior net)/abs(prior net) | Net includes credits | Included | SQL 02; DAX time intelligence |
| YoY net change | (period net − comparable prior-year net)/abs(prior net) | Net includes credits | Included | DAX; interpretation limited by short dataset |
| RFM recency | Reference date minus last valid sale date, in days | Returns do not shift last purchase | Excluded | Python RFM; SQL 06 |
| RFM frequency | Distinct qualifying sale invoices per customer | Credits do not add purchases | Excluded | Python RFM; SQL 06 |
| RFM monetary | Sum all valid signed line sales for buyer | Credits reduce monetary value | Excluded | Python RFM; SQL 06 |
| Monthly cohort retention | Known acquired customers buying in cohort age n / cohort size | Credits alone do not make active | Excluded | Python cohorts; SQL 05; DAX customer |
| Country net sales | Sum net line sales grouped by source country | Credits netted | Included | SQL 10; FactSales + DimGeography |
| Product contribution | Product net sales / total net sales in scope | Credits netted; shares can be negative | Included | SQL 03; DAX ranking |

**Revenue ≠ profit; invoice lines ≠ distinct orders.** If a metric's denominator is zero, return a missing value rather than an invented zero percentage. No unobserved profit, category, tax or discount measure is created.

## Technical boundaries

- Python owns row-level cleaning and physical export; SQL owns independent business aggregations and verifies RFM/cohorts; DAX governs interactive filter context in Power BI (desktop work remains manual).
- Portable SQL stores calendar keys as ISO text and integer month indexes. PostgreSQL DDL is provided in `sql/schema/` but has **not** been deployed in this environment. The root 10 query files ran against SQLite.
- Power BI RFM/cohort tables are **fixed snapshots**; FactSales date slicers do not recompute cohorts or tiers.
- Only Python and SQLite queries are automatically tested; DAX is supplied for manual Power BI verification.
