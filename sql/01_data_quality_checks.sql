-- Audit the *accepted* warehouse. Rejected-row counts are in data_quality.json.
SELECT 'duplicate_line_ids' AS check_name, COUNT(*) AS issue_count
FROM (SELECT line_id FROM fact_sales GROUP BY line_id HAVING COUNT(*) > 1)
UNION ALL
SELECT 'missing_invoice', COUNT(*) FROM fact_sales WHERE invoice_no IS NULL OR invoice_no = ''
UNION ALL
SELECT 'missing_date', COUNT(*) FROM fact_sales WHERE date_key IS NULL
UNION ALL
SELECT 'missing_product', COUNT(*) FROM fact_sales WHERE product_id IS NULL
UNION ALL
SELECT 'nonpositive_price', COUNT(*) FROM fact_sales WHERE unit_price <= 0
UNION ALL
SELECT 'orphan_products', COUNT(*) FROM fact_sales f LEFT JOIN dim_product p ON f.product_id = p.product_id WHERE p.product_id IS NULL
UNION ALL
SELECT 'orphan_geographies', COUNT(*) FROM fact_sales f LEFT JOIN dim_geography g ON f.geography_id = g.geography_id WHERE g.geography_id IS NULL
UNION ALL
SELECT 'orphan_named_customers', COUNT(*) FROM fact_sales f LEFT JOIN dim_customer c ON f.customer_id = c.customer_id WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL
UNION ALL
SELECT 'source_lookalikes_retained', COALESCE(SUM(duplicate_source_values),0) FROM fact_sales
UNION ALL
SELECT 'negative_quantities_with_no_C', COALESCE(SUM(unmarked_return),0) FROM fact_sales;
