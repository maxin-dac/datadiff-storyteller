from __future__ import annotations

from typing import Any, Optional

import numpy as np
import pandas as pd


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (np.floating, float)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, (np.integer, int)):
        return float(value)
    try:
        result = float(value)
        if np.isnan(result):
            return None
        return result
    except Exception:
        return None


def _maybe_numeric(series: pd.Series) -> tuple[pd.Series, bool]:
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(float), True

    converted = pd.to_numeric(series, errors="coerce")
    non_null_original = series.notna().sum()

    if non_null_original == 0:
        return converted, False

    convertible_ratio = converted.notna().sum() / non_null_original

    if convertible_ratio >= 0.80:
        return converted, True

    return series, False


def _numeric_stats(series: pd.Series) -> dict:
    clean = series.dropna().astype(float)

    if clean.empty:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "q05": None,
            "q25": None,
            "q50": None,
            "q75": None,
            "q95": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
            "outlier_rate": 0.0,
        }

    q = clean.quantile([0.05, 0.25, 0.50, 0.75, 0.95]).to_dict()

    q05 = _safe_float(q.get(0.05))
    q25 = _safe_float(q.get(0.25))
    q50 = _safe_float(q.get(0.50))
    q75 = _safe_float(q.get(0.75))
    q95 = _safe_float(q.get(0.95))

    iqr = None
    lower_bound = None
    upper_bound = None
    outlier_count = 0
    outlier_rate = 0.0

    if q25 is not None and q75 is not None:
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outlier_mask = (clean < lower_bound) | (clean > upper_bound)
        outlier_count = int(outlier_mask.sum())
        outlier_rate = float(outlier_count / len(clean)) if len(clean) else 0.0

    return {
        "count": int(len(clean)),
        "min": _safe_float(clean.min()),
        "max": _safe_float(clean.max()),
        "mean": _safe_float(clean.mean()),
        "std": _safe_float(clean.std()),
        "q05": q05,
        "q25": q25,
        "q50": q50,
        "q75": q75,
        "q95": q95,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": outlier_count,
        "outlier_rate": outlier_rate,
    }


def _categorical_stats(series: pd.Series, top_n: int = 20) -> dict:
    clean = series.dropna().astype(str)

    if clean.empty:
        return {
            "count": 0,
            "unique_count": 0,
            "top_values": [],
            "category_shares": {},
            "dominant_share": 0.0,
        }

    value_counts = clean.value_counts()
    total = len(clean)

    top_values = value_counts.head(top_n).index.tolist()
    category_shares = {
        str(value): float(count / total)
        for value, count in value_counts.head(top_n).items()
    }

    dominant_share = float(value_counts.iloc[0] / total) if not value_counts.empty else 0.0

    return {
        "count": int(total),
        "unique_count": int(clean.nunique()),
        "top_values": top_values,
        "category_shares": category_shares,
        "dominant_share": dominant_share,
    }


def _temporal_stats(series: pd.Series) -> dict:
    clean = pd.to_datetime(series, errors="coerce").dropna()

    if clean.empty:
        return {
            "count": 0,
            "min": None,
            "max": None,
        }

    return {
        "count": int(len(clean)),
        "min": clean.min().isoformat(),
        "max": clean.max().isoformat(),
    }


def _detect_key_candidates(columns: list[str]) -> list[str]:
    candidates = []

    for column in columns:
        lowered = str(column).strip().lower()

        if lowered in {"id", "uuid", "guid", "pk"}:
            candidates.append(column)
        elif lowered.endswith("_id"):
            candidates.append(column)
        elif lowered.startswith("id_"):
            candidates.append(column)

    return candidates


def profile_dataframe(df: pd.DataFrame, top_categories: int = 20) -> dict:
    rows = int(len(df))

    column_profiles: dict[str, dict] = {}

    for column in df.columns:
        series = df[column]
        dtype = str(series.dtype)

        null_count = int(series.isna().sum())
        null_rate = float(null_count / rows) if rows else 0.0
        unique_count = int(series.nunique(dropna=True))

        profile: dict[str, Any] = {
            "dtype": dtype,
            "null_count": null_count,
            "null_rate": null_rate,
            "unique_count": unique_count,
        }

        numeric_series, is_numeric = _maybe_numeric(series)

        if is_numeric:
            profile["numeric"] = _numeric_stats(numeric_series)
        elif pd.api.types.is_datetime64_any_dtype(series):
            profile["temporal"] = _temporal_stats(series)
        else:
            profile["categorical"] = _categorical_stats(series, top_n=top_categories)

        column_profiles[str(column)] = profile

    row_duplicate_count = int(df.duplicated().sum())
    row_duplicate_rate = float(row_duplicate_count / rows) if rows else 0.0

    key_candidates = _detect_key_candidates(list(df.columns))
    key_duplicates: dict[str, dict] = {}

    for key in key_candidates:
        if key not in df.columns:
            continue

        series = df[key].dropna()
        duplicate_rows = int(series.duplicated().sum())
        duplicate_keys = int(series[series.duplicated(keep=False)].nunique())

        key_duplicates[key] = {
            "unique_count": int(series.nunique()),
            "duplicate_rows": duplicate_rows,
            "duplicate_keys": duplicate_keys,
            "duplicate_rate": float(duplicate_rows / len(series)) if len(series) else 0.0,
        }

    return {
        "rows": rows,
        "columns": [str(c) for c in df.columns],
        "column_profiles": column_profiles,
        "row_duplicate_count": row_duplicate_count,
        "row_duplicate_rate": row_duplicate_rate,
        "key_duplicates": key_duplicates,
    }