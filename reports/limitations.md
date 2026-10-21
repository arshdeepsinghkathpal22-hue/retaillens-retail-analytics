# Limitations and integrity controls

The upstream UCI dataset is historical (December 2010–December 2011) and is not a live business feed. It has no reliable item costs, net profit, discounts, advertising spend, attribution, delivery cost, category hierarchy, customer contact permissions, or mapping between a credit note and its original sale. Therefore we **do not** infer margin, ROAS, discount elasticity, profit, causal drivers or churn probabilities.

- **Invoice-line ambiguity:** Distinct source lines can be identical in all available fields. We retain and flag duplicate-looking lines instead of silently removing possibly valid sales.
- **Credit convention:** Negative quantity or a C prefix signifies a return/credit in this model. Inconsistencies are logged. Financial settlement status is unknown.
- **Currency:** All figures are in GBP per UCI source description. VAT treatment is unknown.
- **Partial periods:** The final observed month is censored for cohort retention; user-facing dashboards should label/filter partial periods in monthly growth charts.
- **Customer gaps:** Customer analyses exclude null IDs, but sales KPIs include those transactions, so shares of identified buyers must not be portrayed as shares of all sales without adjustment.
- **RFM:** A heuristic historical segmentation snapshot, not a predicted event or real-time marketing audience. Avoid sending actual marketing communications without permissions.
- **Concentration:** High customer or product contribution need not indicate risk without seasonality, product lifecycle and industry context.
- **Environment:** SQLite query execution and Python testing were possible; PostgreSQL deployment and Power BI Desktop were not. DAX has not been loaded/validated in Desktop; no genuine PBIX or Power BI screenshots are included.
- **Source verification:** The UCI landing page and license were checked; download of its original workbook was blocked in the execution environment. Local real-data metrics are pending a run using the original file.
