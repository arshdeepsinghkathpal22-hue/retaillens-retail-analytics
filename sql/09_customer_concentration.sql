-- Revenue share is within identified customers only, not all company revenue.
WITH c AS (
    SELECT customer_id, ROUND(SUM(net_sales),2) AS net_spend_gbp
    FROM fact_sales WHERE customer_id IS NOT NULL
    GROUP BY customer_id
), totals AS (
    SELECT *, SUM(net_spend_gbp) OVER () AS known_net_sales
    FROM c
)
SELECT customer_id, net_spend_gbp,
       ROW_NUMBER() OVER (ORDER BY net_spend_gbp DESC, customer_id) AS customer_rank,
       ROUND(100.0 * net_spend_gbp / NULLIF(known_net_sales, 0),2) AS known_revenue_share_pct
FROM totals ORDER BY customer_rank;
