-- Segment labels are heuristic RFM groupings, not churn predictions.
SELECT segment, COUNT(*) AS customers,
       ROUND(SUM(monetary_net_gbp),2) AS known_customer_net_sales_gbp,
       ROUND(AVG(frequency_orders),2) AS mean_purchase_frequency,
       ROUND(AVG(recency_days),2) AS mean_recency_days
FROM customer_rfm GROUP BY segment ORDER BY customers DESC, segment;
