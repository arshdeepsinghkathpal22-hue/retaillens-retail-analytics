-- Reference PostgreSQL warehouse DDL. The automated demo creates SQLite tables
-- from CSVs instead; this file is not executed by the demo runner.
CREATE TABLE dim_product (
    product_id TEXT PRIMARY KEY,
    product_description TEXT NOT NULL
);
CREATE TABLE dim_customer (
    customer_id TEXT PRIMARY KEY,
    first_purchase_date DATE
);
CREATE TABLE dim_geography (
    geography_id INTEGER PRIMARY KEY,
    country TEXT NOT NULL
);
CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year_month CHAR(7) NOT NULL,
    month_index INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL
);
CREATE TABLE dim_month (
    month_key CHAR(7) PRIMARY KEY,
    month_index INTEGER NOT NULL UNIQUE
);
CREATE TABLE fact_sales (
    line_id BIGINT PRIMARY KEY,
    source_row BIGINT NOT NULL,
    invoice_no TEXT NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    date_key DATE NOT NULL REFERENCES dim_date(date_key),
    month_key CHAR(7) NOT NULL REFERENCES dim_month(month_key),
    month_index INTEGER NOT NULL,
    customer_id TEXT REFERENCES dim_customer(customer_id),
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(18,4) NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('sale','return')),
    gross_sales NUMERIC(18,2) NOT NULL,
    return_amount NUMERIC(18,2) NOT NULL,
    net_sales NUMERIC(18,2) NOT NULL,
    units_sold INTEGER NOT NULL,
    units_returned INTEGER NOT NULL,
    duplicate_source_values INTEGER NOT NULL,
    unmarked_return INTEGER NOT NULL,
    days_from_reference INTEGER NOT NULL,
    geography_id INTEGER REFERENCES dim_geography(geography_id)
);
CREATE TABLE run_metadata (
    last_complete_month_index INTEGER NOT NULL,
    last_complete_month CHAR(7) NOT NULL,
    snapshot_date DATE NOT NULL,
    is_synthetic_fixture INTEGER NOT NULL
);
CREATE TABLE customer_rfm (
    customer_id TEXT PRIMARY KEY REFERENCES dim_customer(customer_id),
    recency_days INTEGER NOT NULL,
    frequency_orders INTEGER NOT NULL,
    monetary_net_gbp NUMERIC(18,2) NOT NULL,
    r_score INTEGER NOT NULL,
    f_score INTEGER NOT NULL,
    m_score INTEGER NOT NULL,
    segment TEXT NOT NULL
);
CREATE TABLE cohort_retention (
    cohort_month CHAR(7) NOT NULL,
    months_since_acquisition INTEGER NOT NULL,
    active_customers INTEGER NOT NULL,
    cohort_size INTEGER NOT NULL,
    retention_percent NUMERIC(5,2) NOT NULL,
    PRIMARY KEY (cohort_month, months_since_acquisition)
);
-- For PostgreSQL, import the generated CSV files in dimension-first order;
-- check all generated types before enabling foreign keys.
