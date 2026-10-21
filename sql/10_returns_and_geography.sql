-- Returns by country are priced credits, NOT verified refund cashflows.
SELECT g.country, COUNT(DISTINCT CASE WHEN f.event_type = 'sale' THEN f.invoice_no END) AS sales_invoices,
       COUNT(DISTINCT CASE WHEN f.event_type = 'return' THEN f.invoice_no END) AS credit_invoices,
       ROUND(SUM(f.gross_sales),2) AS gross_sales_gbp,
       ROUND(SUM(f.return_amount),2) AS returns_gbp,
       ROUND(SUM(f.net_sales),2) AS net_sales_gbp,
       ROUND(100.0 * SUM(f.return_amount) / NULLIF(SUM(f.gross_sales),0),2) AS return_to_gross_pct
FROM fact_sales f JOIN dim_geography g ON f.geography_id = g.geography_id
GROUP BY g.country ORDER BY net_sales_gbp DESC;
