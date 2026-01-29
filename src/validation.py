# src/validation.py
from __future__ import annotations

import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_cols: list[str]) -> None:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_no_nulls(df: pd.DataFrame, cols: list[str]) -> None:
    null_counts = df[cols].isnull().sum()
    bad = null_counts[null_counts > 0]
    if not bad.empty:
        raise ValueError(f"Nulls found in critical columns:\n{bad}")


def validate_ranges(df: pd.DataFrame) -> None:
    # Sales, quantity, shipping cost should be non-negative
    if (df["sales"] < 0).any():
        raise ValueError("Invalid: negative sales found.")
    if (df["quantity"] <= 0).any():
        raise ValueError("Invalid: non-positive quantity found.")
    if (df["shipping_cost"] < 0).any():
        raise ValueError("Invalid: negative shipping_cost found.")

    # Discount should be between 0 and 1
    if ((df["discount"] < 0) | (df["discount"] > 1)).any():
        raise ValueError("Invalid: discount outside [0,1] detected.")

    # Shipping days should not be negative
    if (df["shipping_days"] < 0).any():
        raise ValueError("Invalid: negative shipping_days found.")


def validate_duplicates(df: pd.DataFrame, subset: list[str]) -> None:
    dup_count = df.duplicated(subset=subset).sum()
    # Duplicates can exist if multiple line items share the same order_id,
    # so use a safe subset key for line items when available.
    if dup_count > 0:
        raise ValueError(
            f"Duplicate records detected for key subset {subset}: {dup_count}"
        )
