-- Recency is measured from max(source invoice date) + 1 day, not today's date.
-- PERCENT_RANK + RANK tie semantics keep equally-valued customers in one tier.
WITH customers AS (
    SELECT customer_id,
           MIN(CASE WHEN event_type = 'sale' THEN days_from_reference END) AS recency_days,
           COUNT(DISTINCT CASE WHEN event_type = 'sale' THEN invoice_no END) AS frequency_orders,
           ROUND(SUM(net_sales),2) AS monetary_net_gbp
    FROM fact_sales WHERE customer_id IS NOT NULL
    GROUP BY customer_id
    HAVING COUNT(DISTINCT CASE WHEN event_type = 'sale' THEN invoice_no END) >= 1
), scored AS (
    SELECT *,
           5 - CAST(4 * PERCENT_RANK() OVER (ORDER BY recency_days ASC) AS INTEGER) AS r_score,
           5 - CAST(4 * PERCENT_RANK() OVER (ORDER BY frequency_orders DESC) AS INTEGER) AS f_score,
           5 - CAST(4 * PERCENT_RANK() OVER (ORDER BY monetary_net_gbp DESC) AS INTEGER) AS m_score
    FROM customers
)
SELECT customer_id, recency_days, frequency_orders, monetary_net_gbp,
       r_score, f_score, m_score,
       CASE
         WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
         WHEN f_score >= 4 AND m_score >= 3 THEN 'Loyal Customers'
         WHEN r_score >= 4 AND frequency_orders = 1 THEN 'New Customers'
         WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
         WHEN r_score <= 2 THEN 'Hibernating'
         ELSE 'Potential Loyalists'
       END AS segment
FROM scored ORDER BY customer_id;
