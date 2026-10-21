-- Product contribution: negative returns offset sales, not profit.
WITH totals AS (
    SELECT product_id,
           ROUND(SUM(gross_sales),2) AS gross_sales_gbp,
           ROUND(SUM(return_amount),2) AS returned_gbp,
           ROUND(SUM(net_sales),2) AS net_sales_gbp,
           SUM(units_sold) AS units_sold
    FROM fact_sales GROUP BY product_id
)
SELECT t.product_id, p.product_description, t.gross_sales_gbp, t.returned_gbp,
       t.net_sales_gbp, t.units_sold,
       RANK() OVER (ORDER BY t.net_sales_gbp DESC) AS revenue_rank,
       DENSE_RANK() OVER (ORDER BY t.units_sold DESC) AS unit_rank,
       ROUND(100.0 * t.net_sales_gbp / NULLIF(SUM(t.net_sales_gbp) OVER (),0),2) AS contribution_pct
FROM totals t JOIN dim_product p ON p.product_id = t.product_id
ORDER BY revenue_rank, t.product_id;
