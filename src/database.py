"""Small SQLite warehouse for portable local query execution."""
from pathlib import Path
import sqlite3
import pandas as pd


def create_database(path: str | Path, frames: dict[str, pd.DataFrame], metadata: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()  # The warehouse is an output, not an append-only source.
    with sqlite3.connect(path) as db:
        for name, frame in frames.items():
            frame.to_sql(name, db, index=False, if_exists="replace", chunksize=25000)
        pd.DataFrame([metadata]).to_sql("run_metadata", db, index=False, if_exists="replace")
        for sql in [
            "CREATE UNIQUE INDEX ix_fact_line ON fact_sales (line_id)",
            "CREATE INDEX ix_fact_customer ON fact_sales (customer_id)",
            "CREATE INDEX ix_fact_date ON fact_sales (date_key)",
            "CREATE INDEX ix_fact_product ON fact_sales (product_id)",
            "CREATE INDEX ix_fact_geography ON fact_sales (geography_id)",
            "CREATE INDEX ix_fact_month ON fact_sales (month_index)",
            "CREATE UNIQUE INDEX ix_customer_id ON dim_customer (customer_id)",
            "CREATE UNIQUE INDEX ix_product_id ON dim_product (product_id)",
            "CREATE UNIQUE INDEX ix_geography_id ON dim_geography (geography_id)",
        ]:
            db.execute(sql)
