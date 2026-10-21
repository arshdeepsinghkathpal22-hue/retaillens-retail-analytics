"""Star dimensions, customer snapshot and fully observed monthly cohorts."""
import calendar
import math
import numpy as np
import pandas as pd


def build_dimensions(fact: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if fact.empty:
        raise ValueError("Cannot model an empty accepted transaction table")
    products = fact[["product_id", "product_description"]].dropna(subset=["product_description"])
    # Prefer the most frequently observed label if a product's name varies.
    counts = products.groupby(["product_id", "product_description"]).size().rename("n").reset_index()
    counts = counts.sort_values(["product_id", "n", "product_description"], ascending=[True, False, True])
    descriptions = counts.drop_duplicates("product_id")[ ["product_id", "product_description"] ]
    dim_product = fact[["product_id"]].drop_duplicates().merge(descriptions, how="left", on="product_id")
    dim_product["product_description"] = dim_product["product_description"].fillna("Description missing in source")
    dim_product = dim_product.sort_values("product_id").reset_index(drop=True)

    dim_geography = pd.DataFrame({"country": sorted(fact["country"].dropna().unique())})
    dim_geography.insert(0, "geography_id", np.arange(1, len(dim_geography) + 1))
    fact = fact.merge(dim_geography, on="country", how="left", validate="many_to_one")

    customers = fact.loc[fact["customer_id"].notna(), ["customer_id"]].drop_duplicates()
    first_buy = (fact.loc[(fact.event_type == "sale") & fact.customer_id.notna()]
                 .groupby("customer_id", as_index=False)["date_key"].min()
                 .rename(columns={"date_key": "first_purchase_date"}))
    dim_customer = customers.merge(first_buy, on="customer_id", how="left").sort_values("customer_id")
    dim_customer = dim_customer.reset_index(drop=True)

    day_range = pd.date_range(fact["date_key"].min(), fact["date_key"].max(), freq="D")
    dim_date = pd.DataFrame({
        "date_key": day_range.strftime("%Y-%m-%d"),
        "year": day_range.year,
        "month": day_range.month,
        "year_month": day_range.strftime("%Y-%m"),
        "month_index": day_range.year * 12 + day_range.month,
        "quarter": day_range.quarter,
        "day_of_week": day_range.day_name(),
        "is_weekend": (day_range.dayofweek >= 5).astype(int),
    })
    month_range = pd.period_range(fact["month_key"].min(), fact["month_key"].max(), freq="M")
    dim_month = pd.DataFrame({"month_key": month_range.astype(str), "month_index": month_range.year * 12 + month_range.month})
    return {"fact_sales": fact.drop(columns=["country", "product_description"]),
            "dim_product": dim_product, "dim_customer": dim_customer,
            "dim_date": dim_date, "dim_geography": dim_geography, "dim_month": dim_month}


def _score(series: pd.Series, high_is_good: bool) -> pd.Series:
    # rank(method='min') gives the same tier to tied observations.
    n = len(series)
    if n == 1:
        return pd.Series([3], index=series.index, dtype="int64")
    positions = series.rank(method="min", ascending=not high_is_good)
    return (5 - np.floor(4 * (positions - 1) / (n - 1))).astype("int64")


def calculate_rfm(fact: pd.DataFrame) -> pd.DataFrame:
    sales = fact[(fact["event_type"] == "sale") & fact["customer_id"].notna()]
    cols = ["customer_id", "recency_days", "frequency_orders", "monetary_net_gbp",
            "r_score", "f_score", "m_score", "segment"]
    if sales.empty:
        return pd.DataFrame(columns=cols)
    buy = sales.groupby("customer_id").agg(
        recency_days=("days_from_reference", "min"),
        frequency_orders=("invoice_no", "nunique"),
    )
    total_net = fact[fact["customer_id"].notna()].groupby("customer_id")["net_sales"].sum().round(2)
    rfm = buy.join(total_net.rename("monetary_net_gbp")).reset_index()
    rfm["r_score"] = _score(rfm["recency_days"], False)
    rfm["f_score"] = _score(rfm["frequency_orders"], True)
    rfm["m_score"] = _score(rfm["monetary_net_gbp"], True)

    def classify(row: pd.Series) -> str:
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if f >= 4 and m >= 3:
            return "Loyal Customers"
        if r >= 4 and row["frequency_orders"] == 1:
            return "New Customers"
        if r <= 2 and f >= 3:
            return "At Risk"
        if r <= 2:
            return "Hibernating"
        return "Potential Loyalists"

    rfm["segment"] = rfm.apply(classify, axis=1)
    return rfm.sort_values("customer_id").reset_index(drop=True)[cols]


def calculate_cohorts(fact: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    fields = ["cohort_month", "months_since_acquisition", "active_customers", "cohort_size", "retention_percent"]
    if fact.empty:
        return pd.DataFrame(columns=fields), ""
    # Exclude the last calendar month: the source stops partway through it.
    final_observed = pd.Period(fact["month_key"].max(), freq="M")
    last_complete = final_observed - 1
    sales = fact[(fact.event_type == "sale") & fact.customer_id.notna()].copy()
    sales = sales[sales["month_index"] <= last_complete.year * 12 + last_complete.month]
    if sales.empty:
        return pd.DataFrame(columns=fields), str(last_complete)
    visits = sales[["customer_id", "month_index"]].drop_duplicates()
    acquisitions = visits.groupby("customer_id", as_index=False)["month_index"].min().rename(columns={"month_index": "cohort_index"})
    visits = visits.merge(acquisitions, on="customer_id", validate="many_to_one")
    visits["months_since_acquisition"] = visits["month_index"] - visits["cohort_index"]
    active = (visits.groupby(["cohort_index", "months_since_acquisition"])["customer_id"]
              .nunique().to_dict())
    cohort_sizes = acquisitions.groupby("cohort_index")["customer_id"].nunique()
    end_index = last_complete.year * 12 + last_complete.month
    rows = []
    for idx, size in cohort_sizes.items():
        year, month = divmod(int(idx) - 1, 12)
        for offset in range(end_index - int(idx) + 1):
            users = int(active.get((idx, offset), 0))
            rows.append((f"{year:04d}-{month+1:02d}", offset, users, int(size), round(100 * users / size, 2)))
    return pd.DataFrame(rows, columns=fields), str(last_complete)
