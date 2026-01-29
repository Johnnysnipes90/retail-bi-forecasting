# src/etl_load_postgres.py
from __future__ import annotations

import logging
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from validation import validate_no_nulls, validate_ranges, validate_required_columns

# -----------------------------
# Logging (professional standard)
# -----------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_name",
    "segment",
    "state",
    "country",
    "market",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit",
    "shipping_cost",
    "order_priority",
    "year",
]


def get_engine() -> "Engine":
    load_dotenv()

    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    db = os.getenv("PG_DB", "retail_bi")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "")
    schema = os.getenv("PG_SCHEMA", "public")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    return engine


def extract(csv_path: str) -> pd.DataFrame:
    logger.info("Reading CSV from %s", csv_path)
    df = pd.read_csv(csv_path)
    validate_required_columns(df, REQUIRED_COLUMNS)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Transforming data: parsing dates, casting types, creating features")

    # Parse dates (fail fast if parsing fails)
    df["order_date"] = pd.to_datetime(
        df["order_date"], format="mixed", dayfirst=True, errors="raise"
    )
    df["ship_date"] = pd.to_datetime(
        df["ship_date"], format="mixed", dayfirst=True, errors="raise"
    )

    # Cast types
    df["year"] = df["year"].astype(int)
    df["quantity"] = df["quantity"].astype(int)

    # Feature engineering for ops KPI
    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days

    # Basic validation (BI-safe)
    validate_no_nulls(
        df,
        [
            "order_id",
            "order_date",
            "ship_date",
            "sales",
            "quantity",
            "discount",
            "profit",
            "shipping_cost",
            "year",
        ],
    )
    validate_ranges(df)

    # Conform decimals (optional but helps consistency)
    df["sales"] = df["sales"].round(2)
    df["discount"] = df["discount"].round(2)
    df["shipping_cost"] = df["shipping_cost"].round(2)
    df["profit"] = df["profit"].round(3)

    return df


def load(engine, df: pd.DataFrame) -> None:
    logger.info("Loading %d rows into PostgreSQL staging table", len(df))

    # Load into staging (replace to keep runs idempotent)
    df_to_stage = df.copy()

    # For staging table we store dates as strings to avoid mismatch issues
    df_to_stage["order_date"] = df_to_stage["order_date"].dt.strftime("%Y-%m-%d")
    df_to_stage["ship_date"] = df_to_stage["ship_date"].dt.strftime("%Y-%m-%d")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE public.stg_retail_sales;"))

    df_to_stage.drop(columns=["shipping_days"], errors="ignore").to_sql(
        "stg_retail_sales",
        engine,
        schema="public",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    logger.info("Promoting staging data into production table")

    promote_sql = """
    TRUNCATE TABLE public.retail_sales;

    INSERT INTO public.retail_sales (
      order_id, order_date, ship_date, ship_mode, customer_name,
      segment, state, country, market, region,
      product_id, category, sub_category, product_name,
      sales, quantity, discount, profit, shipping_cost,
      order_priority, year, shipping_days
    )
    SELECT
      order_id,
      order_date::date,
      ship_date::date,
      ship_mode,
      customer_name,
      segment,
      state,
      country,
      market,
      region,
      product_id,
      category,
      sub_category,
      product_name,
      sales::numeric,
      quantity::int,
      discount::numeric,
      profit::numeric,
      shipping_cost::numeric,
      order_priority,
      year::int,
      (ship_date::date - order_date::date) AS shipping_days
    FROM public.stg_retail_sales;
    """

    with engine.begin() as conn:
        conn.execute(text(promote_sql))

    logger.info("Load complete: production table refreshed")


def main():
    load_dotenv()
    csv_path = os.getenv("RAW_CSV_PATH", "../data/raw/superstore_sales_clean.csv")

    engine = get_engine()

    df = extract(csv_path)
    df = transform(df)
    load(engine, df)


if __name__ == "__main__":
    main()
