# Star schema and join directions

`FactSales` grain: **one accepted source Excel invoice line** (not invoice header).
`DimDate` grain: one calendar day, `DimProduct`: one stock code, `DimCustomer`: one known customer, `DimGeography`: one country.

All relationships use **single-direction** filtering from the dimension to `FactSales`:

| From: one side | To: many side | Status |
|---|---|---|
| DimDate[date_key] | FactSales[date_key] | Active, date-type join |
| DimCustomer[customer_id] | FactSales[customer_id] | Active; fact may be blank |
| DimProduct[product_id] | FactSales[product_id] | Active |
| DimGeography[geography_id] | FactSales[geography_id] | Active |

`CustomerRFM` and `CohortRetention` are **snapshot/aggregate tables**. Do not connect them directly to fact with a bidirectional many-to-many link. Use `TREATAS` (in the supplied segment revenue measure) to apply customer snapshot selections to `DimCustomer`. `CohortRetention` is intentionally detached; its matrix reflects the fixed full historical observation window, not an arbitrary FactSales date slicer. RFM scores are also static to the source's max date + 1 day.

`DimMonth` is for SQL; it need not be imported into Power BI. The `run_metadata` table records the snapshot and last fully observed cohort month.

## Text architecture

UCI raw workbook → Python cleaning/audit → accepted line fact + rejected lines → dimension tables → SQLite SQL warehouse → output CSVs → Power BI Desktop model and four report pages.

For time intelligence: cast `DimDate[date_key]` and `FactSales[date_key]` to **Date** in Power Query. Mark `DimDate` as the date table and select `DimDate[date_key]`. Cast `DimCustomer[first_purchase_date]` to Date as well.
