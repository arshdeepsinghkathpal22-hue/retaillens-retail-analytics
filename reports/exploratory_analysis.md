# Exploratory analysis plan and reproducible outputs

This project treats exploratory checks as an auditable operation rather than an unexplained notebook.

1. `data/outputs/source_profile.json`: row counts, column types, missing ratios, duplicate-lookalike counts, invoice/date coverage, zero/negative prices and quantities, unique invoices/products/countries/customers.
2. `data/outputs/cleaning_decisions.json` + `data/processed/rejected_records.csv`: rejected rows and reasons, accepted source line audit flags, and cancellation convention.
3. `data/outputs/02_revenue_analysis.csv`: monthly orders, active customers, gross and net line sales, credited amounts, monthly changes.
4. `data/outputs/03_product_analysis.csv`, `10_returns_and_geography.csv`: product and country concentration and returns.
5. `data/outputs/05_cohort_retention.csv`, `06_rfm_analysis.csv`: validated historical customer behavior snapshots.
6. `reports/figures/monthly_net_sales.png`, `rfm_segments.png`: simple Matplotlib plots generated from loaded rows (demo chart titles contain **SYNTHETIC FIXTURE**).

For any unusual outlier, return ratio, missing customer pattern, customer concentration or negative net customer, inspect the underlying invoices **before** asserting a business cause.

There are no recorded UCI numerical findings in this repository before running the original dataset. Avoid publishing fixture charts as empirical outcomes.
