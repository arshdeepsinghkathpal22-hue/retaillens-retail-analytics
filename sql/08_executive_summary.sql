-- One row for reconciliation: invoice count is not the number of invoice lines.
SELECT ROUND(COALESCE(SUM(net_sales),0),2) AS net_sales_gbp,
       ROUND(COALESCE(SUM(gross_sales),0),2) AS gross_sales_gbp,
       ROUND(COALESCE(SUM(return_amount),0),2) AS returns_gbp,
       COUNT(DISTINCT CASE WHEN event_type = 'sale' THEN invoice_no END) AS orders,
       COUNT(DISTINCT CASE WHEN event_type = 'sale' THEN customer_id END) AS known_buying_customers,
       SUM(units_sold) AS units_sold,
       SUM(units_returned) AS units_returned,
       ROUND(COALESCE(SUM(gross_sales),0) * 1.0 / NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'sale' THEN invoice_no END),0),2) AS gross_aov_gbp
FROM fact_sales;
