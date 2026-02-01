"""
SARIMA Forecasting Module (Monthly Revenue)

- Pulls monthly revenue from Postgres (vw_monthly_sales)
- Runs leakage-free backtest (last N months)
- Benchmarks against seasonal naive baseline
- Fits final model and forecasts next N months with CI
- Exports CSV artifacts and (optionally) writes results to Postgres for Power BI

Designed for portfolio-grade "production" structure.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import Engine, create_engine
from statsmodels.tsa.statespace.sarimax import SARIMAX


# -----------------------------
# Config
# -----------------------------
@dataclass(frozen=True)
class ForecastConfig:
    schema: str = "public"
    source_view: str = "vw_monthly_sales"
    target_table: str = "monthly_sales_forecast"

    date_col: str = "month"
    value_col: str = "monthly_sales"

    freq: str = "MS"  # month start
    seasonal_period: int = 12

    # SARIMA(1,1,1)(0,1,1,12) default
    order: Tuple[int, int, int] = (1, 1, 1)
    seasonal_order: Tuple[int, int, int, int] = (0, 1, 1, 12)

    backtest_horizon: int = 6
    forecast_horizon: int = 6

    output_dir: str = "data/processed"
    write_to_postgres: bool = True


# -----------------------------
# Helpers / Metrics
# -----------------------------
def smape(y_true, y_pred) -> float:
    """Symmetric MAPE (%), robust to scale."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    denom = np.abs(y_true) + np.abs(y_pred)
    denom = np.where(denom == 0, 1, denom)
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom) * 100)


def get_engine_from_env() -> Engine:
    """
    Creates a SQLAlchemy engine from env vars:
    PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
    """
    # ✅ Load .env automatically when running scripts
    load_dotenv()

    missing = [
        k
        for k in ["PG_HOST", "PG_PORT", "PG_DB", "PG_USER", "PG_PASSWORD"]
        if not os.getenv(k)
    ]
    if missing:
        raise EnvironmentError(
            f"Missing env vars: {missing}. Ensure .env is loaded into your environment."
        )

    return create_engine(
        f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
        f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
    )


# -----------------------------
# Data I/O
# -----------------------------
def load_monthly_series(engine: Engine, cfg: ForecastConfig) -> pd.Series:
    """Load monthly sales from Postgres view and return a monthly-indexed Series."""
    q = f"""
    SELECT {cfg.date_col} AS month, {cfg.value_col} AS value
    FROM {cfg.schema}.{cfg.source_view}
    ORDER BY {cfg.date_col};
    """
    df = pd.read_sql(q, engine)
    df["month"] = pd.to_datetime(df["month"])
    df = df.set_index("month").sort_index()

    # Enforce monthly frequency
    df = df.asfreq(cfg.freq)

    if df["value"].isna().any():
        raise ValueError(
            "Monthly series contains NaNs after enforcing frequency. Check missing months in SQL view."
        )

    return df["value"]


# -----------------------------
# Modeling
# -----------------------------
def seasonal_naive_baseline(
    train: pd.Series, test_index: pd.DatetimeIndex, seasonal_period: int
) -> pd.Series:
    """
    Seasonal naive baseline: forecast equals last year's same month.
    """
    baseline = train.shift(seasonal_period).reindex(test_index)
    if baseline.isna().any():
        # If not enough history, fallback to last observed value
        baseline = baseline.fillna(train.iloc[-1])
    return baseline


def fit_sarima(train: pd.Series, cfg: ForecastConfig):
    """Fit SARIMA model and return fitted results."""
    model = SARIMAX(
        train,
        order=cfg.order,
        seasonal_order=cfg.seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def backtest_sarima(ts: pd.Series, cfg: ForecastConfig) -> dict:
    """
    Backtest using last cfg.backtest_horizon months.
    Returns metrics + predictions + confidence intervals.
    """
    if len(ts) <= (cfg.backtest_horizon + cfg.seasonal_period + 1):
        raise ValueError(
            "Not enough history for seasonal backtest. Need more observations."
        )

    train = ts.iloc[: -cfg.backtest_horizon]
    test = ts.iloc[-cfg.backtest_horizon :]

    # Baseline
    baseline_pred = seasonal_naive_baseline(train, test.index, cfg.seasonal_period)

    baseline_mae = mean_absolute_error(test, baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(test, baseline_pred))
    baseline_smape = smape(test, baseline_pred)

    # SARIMA
    res = fit_sarima(train, cfg)
    fc = res.get_forecast(steps=len(test))

    sarima_mean = fc.predicted_mean
    sarima_ci = fc.conf_int()

    # Align indices
    sarima_mean.index = test.index
    sarima_ci.index = test.index

    sarima_mae = mean_absolute_error(test, sarima_mean)
    sarima_rmse = np.sqrt(mean_squared_error(test, sarima_mean))
    sarima_smape = smape(test, sarima_mean)

    return {
        "train": train,
        "test": test,
        "baseline_pred": baseline_pred,
        "sarima_pred": sarima_mean,
        "sarima_ci": sarima_ci,
        "metrics": {
            "baseline": {
                "mae": baseline_mae,
                "rmse": baseline_rmse,
                "smape": baseline_smape,
            },
            "sarima": {"mae": sarima_mae, "rmse": sarima_rmse, "smape": sarima_smape},
        },
    }


def fit_and_forecast(ts: pd.Series, cfg: ForecastConfig) -> pd.DataFrame:
    """Fit SARIMA on full series and return future forecast dataframe with mean + CI."""
    res = fit_sarima(ts, cfg)
    future = res.get_forecast(steps=cfg.forecast_horizon)
    future_df = future.summary_frame()  # mean, mean_ci_lower, mean_ci_upper, mean_se
    return future_df


# -----------------------------
# Outputs (CSV + Postgres)
# -----------------------------
def build_output_tables(
    backtest: dict,
    future_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      backtest_out: month, actual_sales, forecast_sales, ci_lower, ci_upper, run_type=backtest
      future_out:   month, actual_sales(NaN), forecast_sales, ci_lower, ci_upper, run_type=future
      combined:     concatenation for BI
    """
    test = backtest["test"]
    pred = backtest["sarima_pred"]
    ci = backtest["sarima_ci"]

    backtest_out = pd.DataFrame(
        {
            "month": test.index,
            "actual_sales": test.values,
            "forecast_sales": pred.values,
            "ci_lower": ci.iloc[:, 0].values,
            "ci_upper": ci.iloc[:, 1].values,
            "run_type": "backtest",
        }
    )

    future_out = pd.DataFrame(
        {
            "month": future_df.index,
            "actual_sales": np.nan,
            "forecast_sales": future_df["mean"].values,
            "ci_lower": future_df["mean_ci_lower"].values,
            "ci_upper": future_df["mean_ci_upper"].values,
            "run_type": "future",
        }
    )

    combined = pd.concat([backtest_out, future_out], ignore_index=True)
    return backtest_out, future_out, combined


def save_csv_artifacts(
    backtest_out: pd.DataFrame, future_out: pd.DataFrame, cfg: ForecastConfig
) -> None:
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    backtest_path = out_dir / "backtest_forecast.csv"
    future_path = out_dir / "monthly_forecast.csv"

    backtest_out.to_csv(backtest_path, index=False)
    future_out.to_csv(future_path, index=False)

    print("Saved CSV artifacts:")
    print(f" - {backtest_path}")
    print(f" - {future_path}")


def write_forecast_table_to_postgres(
    engine: Engine, combined: pd.DataFrame, cfg: ForecastConfig
) -> None:
    combined.to_sql(
        cfg.target_table,
        engine,
        schema=cfg.schema,
        if_exists="replace",  # portfolio-friendly; in production you'd use append + versioning
        index=False,
    )
    print(f"Wrote table: {cfg.schema}.{cfg.target_table}")


# -----------------------------
# Orchestrator
# -----------------------------
def run_pipeline(
    engine: Optional[Engine] = None, cfg: Optional[ForecastConfig] = None
) -> dict:
    """
    End-to-end forecasting run:
    - load series
    - backtest
    - fit full + forecast
    - build outputs
    - save artifacts
    - (optional) write to postgres

    Returns a dict with metrics and outputs.
    """
    cfg = cfg or ForecastConfig()
    engine = engine or get_engine_from_env()

    ts = load_monthly_series(engine, cfg)

    backtest = backtest_sarima(ts, cfg)
    future_df = fit_and_forecast(ts, cfg)

    backtest_out, future_out, combined = build_output_tables(backtest, future_df)

    save_csv_artifacts(backtest_out, future_out, cfg)

    if cfg.write_to_postgres:
        write_forecast_table_to_postgres(engine, combined, cfg)

    return {
        "metrics": backtest["metrics"],
        "backtest_out": backtest_out,
        "future_out": future_out,
        "combined": combined,
    }
