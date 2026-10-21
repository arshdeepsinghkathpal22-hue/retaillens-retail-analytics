-- Acquisition is first valid purchase. Last observed month is excluded as incomplete.
WITH first_purchase AS (
    SELECT customer_id, MIN(month_index) AS cohort_index
    FROM fact_sales WHERE event_type = 'sale' AND customer_id IS NOT NULL
    GROUP BY customer_id
), eligible AS (
    SELECT f.customer_id, f.month_index
    FROM fact_sales f CROSS JOIN run_metadata meta
    WHERE f.event_type = 'sale' AND f.customer_id IS NOT NULL
      AND f.month_index <= meta.last_complete_month_index
    GROUP BY f.customer_id, f.month_index
), cohorts AS (
    SELECT p.cohort_index, COUNT(*) AS cohort_size
    FROM first_purchase p CROSS JOIN run_metadata meta
    WHERE p.cohort_index <= meta.last_complete_month_index
    GROUP BY p.cohort_index
), observed AS (
    SELECT fp.cohort_index, e.month_index,
           COUNT(DISTINCT e.customer_id) AS active_customers
    FROM eligible e JOIN first_purchase fp ON e.customer_id = fp.customer_id
    GROUP BY fp.cohort_index, e.month_index
)
SELECT months.month_key AS observed_month,
       acquired.month_key AS cohort_month,
       months.month_index - c.cohort_index AS months_since_acquisition,
       COALESCE(o.active_customers,0) AS active_customers,
       c.cohort_size,
       ROUND(100.0 * COALESCE(o.active_customers,0) / c.cohort_size,2) AS retention_percent
FROM cohorts c
JOIN dim_month acquired ON acquired.month_index = c.cohort_index
JOIN dim_month months ON months.month_index >= c.cohort_index
CROSS JOIN run_metadata meta
LEFT JOIN observed o ON o.cohort_index = c.cohort_index AND o.month_index = months.month_index
WHERE months.month_index <= meta.last_complete_month_index
ORDER BY c.cohort_index, months.month_index;
