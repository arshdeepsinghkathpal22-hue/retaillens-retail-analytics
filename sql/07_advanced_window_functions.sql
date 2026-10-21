-- Shows LAG, LEAD, running totals, rolling mean, and product ranking by month.
WITH monthly_product AS (
    SELECT month_key, product_id, ROUND(SUM(net_sales),2) AS net_sales_gbp
    FROM fact_sales GROUP BY month_key, product_id
), windowed AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY month_key ORDER BY net_sales_gbp DESC, product_id) AS row_number,
           RANK() OVER (PARTITION BY month_key ORDER BY net_sales_gbp DESC) AS sales_rank,
           LAG(net_sales_gbp) OVER (PARTITION BY product_id ORDER BY month_key) AS preceding_active_month_sales,
           LEAD(net_sales_gbp) OVER (PARTITION BY product_id ORDER BY month_key) AS following_active_month_sales,
           ROUND(SUM(net_sales_gbp) OVER (PARTITION BY product_id ORDER BY month_key ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),2) AS running_product_sales,
           ROUND(AVG(net_sales_gbp) OVER (PARTITION BY product_id ORDER BY month_key ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS three_active_month_avg
    FROM monthly_product
)
SELECT * FROM windowed ORDER BY month_key, row_number;
