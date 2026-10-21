# Warehouse data dictionary

| Table | Columns | Definition |
|---|---|---|
| FactSales | line_id, source_row | Distinct Excel row number used as a stable within-file line key (not global business ID) |
| FactSales | invoice_no, invoice_date | Source invoice; one invoice can have multiple lines |
| FactSales | date_key, month_key, month_index | ISO date and year-month, with `year * 12 + month` for month spacing |
| FactSales | customer_id | Nullable source customer ID; missing values remain absent |
| FactSales | product_id, geography_id | Foreign keys into reference dimensions |
| FactSales | quantity, unit_price | Signed units and per-unit price in GBP |
| FactSales | event_type | `sale` for positive regular invoice, `return` for negative units or C-prefixed credit |
| FactSales | gross_sales, return_amount, net_sales | Positive sale amount, positive credited amount, and signed difference (GBP) |
| FactSales | units_sold, units_returned | Non-negative counts, separated by event type |
| FactSales | duplicate_source_values | 1 if an identical raw record preceded it; still retained |
| FactSales | unmarked_return | Negative quantity without cancellation marker |
| FactSales | days_from_reference | Day difference from next date after final observed invoice date; used for RFM |
| DimCustomer | customer_id, first_purchase_date | Identified customer and first valid positive sale date; returns-only customers have no acquisition date |
| DimProduct | product_id, product_description | Source SKU and most frequent nonblank text label; no category field |
| DimDate | date_key, year, month, year_month, month_index, quarter, day_of_week, is_weekend | Continuous calendar |
| DimGeography | geography_id, country | Distinct source country string; unknowns are labeled Unknown |
| CustomerRFM | customer_id, recency_days, frequency_orders, monetary_net_gbp, r_score, f_score, m_score, segment | Snapshot segments; not predictive |
| CohortRetention | cohort_month, months_since_acquisition, active_customers, cohort_size, retention_percent | Full-month historical customer acquisition cohorts |
| DimMonth | month_key, month_index | Continuous observed months for SQL reporting |
| run_metadata | last_complete_month, snapshot_date, is_synthetic_fixture | Reporting boundaries and provenance flag |
| RejectedRecords | source fields, rejection_reason | Auditable raw excluded rows |

**Currency:** Prices are identified by UCI as pound sterling. No currency conversion is applied. All amounts are observational sales proxies, not legally reconciled accounting revenue or cash payments.
