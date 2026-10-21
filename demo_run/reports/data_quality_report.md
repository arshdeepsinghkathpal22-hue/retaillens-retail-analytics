# Data quality report

**Source status:** SYNTHETIC TEST FIXTURE — NOT BUSINESS EVIDENCE

| Check | Count |
|---|---:|
| Raw rows | 7,725 |
| Accepted rows | 7,716 |
| Rejected rows | 9 |
| Exact duplicate-looking source rows retained | 1 |
| Returns missing cancellation marker | 0 |
| Missing customer IDs in source | 262 |
| High-quantity IQR flags (not deleted) | 0 |
| High-price IQR flags (not deleted) | 157 |

## Rejection reasons

| Rule | Excluded rows |
|---|---:|
| missing_invoice | 1 |
| missing_stock_code | 1 |
| invalid_invoice_date | 1 |
| invalid_quantity | 1 |
| zero_quantity | 1 |
| invalid_price | 2 |
| zero_price_noncommercial | 1 |
| credit_with_positive_quantity | 1 |

## Warehouse quality gate

{'all_rows_accounted_for': True, 'line_ids_unique': True, 'no_nonpositive_prices': True, 'no_zero_quantities': True, 'no_missing_invoices': True, 'no_missing_products': True, 'no_missing_dates': True, 'net_sales_reconcile': True}

Source invoice numbers repeat naturally across invoice lines. They are not duplicate business keys by themselves. Duplicate-looking complete lines are retained because the source provides no line identifier. Inspect `rejected_records.csv` before revising any rule. Revenue includes priced returns; zero-price and malformed records are excluded from priced-sales metrics.
