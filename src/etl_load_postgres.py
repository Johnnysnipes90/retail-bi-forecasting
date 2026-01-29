# src/etl_load_postgres.py
from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from validation import validate_no_nulls, validate_ranges, validate_required_columns

# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------
# Constants
# -----------------------------
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


# -----------------------------
# Helpers
# -----------------------------
def project_root() -> Path:
    """Return the project root directory (one level above /src)."""
    return Path(__file__).resolve().parent.parent


def load_project_env() -> None:
    """
    Load .env from project root explicitly.
    This avoids issues where load_dotenv() fails depending on the working directory.
    """
    env_path = project_root() / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f".env not found at: {env_path}")
    load_dotenv(dotenv_path=env_path)


def resolve_csv_path() -> Path:
    """
    Resolve RAW_CSV_PATH robustly:
    - If RAW_CSV_PATH is absolute -> use it
    - If RAW_CSV_PATH is relative -> treat it as relative to project root
    - If not set -> default to <root>/data/raw/superstore_sales_clean.csv
    """
    base_dir = project_root()
    default_path = base_dir / "data" / "raw" / "superstore_sales_clean.csv"

    raw_path = os.getenv("RAW_CSV_PATH")
    if not raw_path:
        return default_path

    p = Path(raw_path)

    # If an absolute path is provided, use it as-is
    if p.is_absolute():
        return p

    # Otherwise resolve relative paths against project root
    return (base_dir / p).resolve()


# -----------------------------
# Database engine
# -----------------------------
def get_engine():
    """
    Build and return a SQLAlchemy engine for PostgreSQL using env vars.
    """
    host = os.getenv("PG_HOST", "127.0.0.1")
    port = os.getenv("PG_PORT", "5432")
    db = os.getenv("PG_DB", "retail_bi")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD")
    schema = os.getenv("PG_SCHEMA", "public")

    if not password:
        raise ValueError(
            "PG_PASSWORD is missing. Ensure your .env contains PG_PASSWORD."
        )

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, connect_args={"options": f"-csearch_path={schema}"})


def preflight_db(engine) -> None:
    """
    Quick connectivity check with an actionable error message.
    Keeps failures obvious and easy to debug in real environments.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
    except Exception as e:
        raise RuntimeError(
            "PostgreSQL connection failed. Ensure:\n"
            "1) PostgreSQL is running\n"
            "2) Database exists (e.g., CREATE DATABASE retail_bi;)\n"
            "3) Credentials in .env are correct\n"
            "4) Host/port are correct (PG_HOST / PG_PORT)\n"
        ) from e


# -----------------------------
# Extract
# -----------------------------
def extract(csv_path: Path) -> pd.DataFrame:
    """
    Read raw CSV and validate that required columns exist.
    """
    logger.info("Reading CSV from %s", csv_path)

    if not csv_path.exists():
        expected = project_root() / "data" / "raw" / "superstore_sales_clean.csv"
        raise FileNotFoundError(
            f"CSV not found: {csv_path}\n"
            f"Expected at: {expected}\n"
            f"Tip: In .env, set RAW_CSV_PATH=data/raw/superstore_sales_clean.csv (relative to project root)."
        )

    df = pd.read_csv(csv_path)
    validate_required_columns(df, REQUIRED_COLUMNS)
    return df


# -----------------------------
# Transform
# -----------------------------
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw data into BI-ready shape:
    - Parse dates
    - Cast numeric types
    - Create derived feature(s)
    - Apply BI-safe validations
    """
    logger.info("Transforming data (dates, types, features, validation)")

    # Parse dates (fail fast)
    df["order_date"] = pd.to_datetime(
        df["order_date"], format="mixed", dayfirst=True, errors="raise"
    )
    df["ship_date"] = pd.to_datetime(
        df["ship_date"], format="mixed", dayfirst=True, errors="raise"
    )

    # Cast numeric types
    df["year"] = df["year"].astype(int)
    df["quantity"] = df["quantity"].astype(int)

    # Feature engineering
    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days

    # BI-safe validations (critical columns must be present and non-null)
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
            "shipping_days",
        ],
    )
    validate_ranges(df)

    # Standardize numeric precision (helps consistent reporting & BI formatting)
    df["sales"] = df["sales"].round(2)
    df["discount"] = df["discount"].round(2)
    df["shipping_cost"] = df["shipping_cost"].round(2)
    df["profit"] = df["profit"].round(3)

    return df


# -----------------------------
# Load
# -----------------------------
def load(engine, df: pd.DataFrame) -> None:
    """
    Load pattern:
    1) TRUNCATE staging table
    2) Bulk insert into staging via pandas.to_sql
    3) TRUNCATE production table
    4) INSERT into production with proper casting + derived shipping_days
    """
    logger.info("Loading %d rows into PostgreSQL staging table", len(df))

    df_stage = df.copy()

    # Convert dates to strings for staging (staging table stores dates as TEXT)
    df_stage["order_date"] = df_stage["order_date"].dt.strftime("%Y-%m-%d")
    df_stage["ship_date"] = df_stage["ship_date"].dt.strftime("%Y-%m-%d")

    # Clear staging table (idempotent reruns)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE public.stg_retail_sales;"))

    # Load into staging (drop derived column; production computes it in SQL)
    df_stage.drop(columns=["shipping_days"], errors="ignore").to_sql(
        name="stg_retail_sales",
        con=engine,
        schema="public",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    logger.info("Promoting data from staging to production table")

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


# -----------------------------
# Main entrypoint
# -----------------------------
def main():
    # 1) Load environment from project root
    load_project_env()

    # 2) Resolve CSV path robustly
    csv_path = resolve_csv_path()
    logger.info("Resolved CSV path: %s", csv_path)

    # 3) Connect to DB (preflight check)
    engine = get_engine()
    preflight_db(engine)

    # 4) ETL pipeline
    df = extract(csv_path)
    df = transform(df)
    load(engine, df)


if __name__ == "__main__":
    main()
