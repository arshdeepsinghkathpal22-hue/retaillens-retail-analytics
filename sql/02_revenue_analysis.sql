-- Monthly net sales includes returns; orders and active customers require actual sales.
WITH monthly AS (
    SELECT d.month_key,
           ROUND(COALESCE(SUM(f.gross_sales), 0), 2) AS gross_sales_gbp,
           ROUND(COALESCE(SUM(f.return_amount), 0), 2) AS returns_gbp,
           ROUND(COALESCE(SUM(f.net_sales), 0), 2) AS net_sales_gbp,
           COUNT(DISTINCT CASE WHEN f.event_type = 'sale' THEN f.invoice_no END) AS orders,
           COUNT(DISTINCT CASE WHEN f.event_type = 'sale' THEN f.customer_id END) AS active_known_customers
    FROM dim_month d LEFT JOIN fact_sales f ON d.month_index = f.month_index
    GROUP BY d.month_key
), lagged AS (
    SELECT *, LAG(net_sales_gbp) OVER (ORDER BY month_key) AS prior_month_sales
    FROM monthly
)
SELECT month_key, gross_sales_gbp, returns_gbp, net_sales_gbp, orders,
       active_known_customers,
       ROUND(CASE WHEN orders > 0 THEN gross_sales_gbp * 1.0 / orders END, 2) AS gross_aov_gbp,
       ROUND(CASE WHEN prior_month_sales <> 0
             THEN 100.0 * (net_sales_gbp - prior_month_sales) / ABS(prior_month_sales) END, 2) AS mom_net_change_pct
FROM lagged ORDER BY month_key;
