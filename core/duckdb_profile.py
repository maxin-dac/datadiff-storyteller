from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

NUMERIC_TYPE_TOKENS = ("INT", "DOUBLE", "FLOAT", "DECIMAL")
TEMPORAL_TYPE_TOKENS = ("DATE", "TIMESTAMP")


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _is_numeric_dtype(dtype: str) -> bool:
    upper = dtype.upper()
    return any(token in upper for token in NUMERIC_TYPE_TOKENS)


def _is_temporal_dtype(dtype: str) -> bool:
    upper = dtype.upper()
    return any(token in upper for token in TEMPORAL_TYPE_TOKENS)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def duckdb_profile(csv_path: str | Path, top_categories: int = 20) -> dict:
    """
    Build a profile dictionary compatible with core.profile.profile_dataframe,
    using DuckDB SQL aggregation instead of loading the full file into Pandas.
    """
    path = str(Path(csv_path).resolve())

    con = duckdb.connect()

    con.execute(
        """
        CREATE OR REPLACE TABLE dataset AS
        SELECT * FROM read_csv_auto(?, header=true, sample_size=100000)
        """,
        [path],
    )

    rows = int(con.execute("SELECT count(*) FROM dataset").fetchone()[0])

    described = con.execute("DESCRIBE dataset").fetchall()

    column_profiles: dict[str, dict] = {}

    for item in described:
        column = str(item[0])
        dtype = str(item[1])

        quoted = _quote_identifier(column)

        null_count = int(
            con.execute(
                f"""
                SELECT count(*) FILTER (WHERE {quoted} IS NULL)
                FROM dataset
                """
            ).fetchone()[0]
        )

        unique_count = int(
            con.execute(
                f"""
                SELECT count(DISTINCT {quoted})
                FROM dataset
                """
            ).fetchone()[0]
        )

        profile: dict[str, Any] = {
            "dtype": dtype,
            "null_count": null_count,
            "null_rate": float(null_count / rows) if rows else 0.0,
            "unique_count": unique_count,
        }

        if _is_numeric_dtype(dtype):
            stats = con.execute(
                f"""
                SELECT
                    min({quoted}) AS min_value,
                    max({quoted}) AS max_value,
                    avg({quoted}) AS avg_value,
                    stddev({quoted}) AS std_value,
                    quantile_cont({quoted}, 0.05) AS q05,
                    quantile_cont({quoted}, 0.25) AS q25,
                    quantile_cont({quoted}, 0.50) AS q50,
                    quantile_cont({quoted}, 0.75) AS q75,
                    quantile_cont({quoted}, 0.95) AS q95,
                    count({quoted}) AS non_null_count
                FROM dataset
                WHERE {quoted} IS NOT NULL
                """
            ).fetchone()

            min_value = _safe_float(stats[0])
            max_value = _safe_float(stats[1])
            mean_value = _safe_float(stats[2])
            std_value = _safe_float(stats[3])
            q05 = _safe_float(stats[4])
            q25 = _safe_float(stats[5])
            q50 = _safe_float(stats[6])
            q75 = _safe_float(stats[7])
            q95 = _safe_float(stats[8])
            non_null_count = int(stats[9] or 0)

            iqr = None
            lower_bound = None
            upper_bound = None
            outlier_count = 0
            outlier_rate = 0.0

            if q25 is not None and q75 is not None:
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr

                outlier_count = int(
                    con.execute(
                        f"""
                        SELECT count(*)
                        FROM dataset
                        WHERE {quoted} IS NOT NULL
                          AND ({quoted} < {lower_bound} OR {quoted} > {upper_bound})
                        """
                    ).fetchone()[0]
                )

                outlier_rate = float(outlier_count / non_null_count) if non_null_count else 0.0

            profile["numeric"] = {
                "count": non_null_count,
                "min": min_value,
                "max": max_value,
                "mean": mean_value,
                "std": std_value,
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

        elif _is_temporal_dtype(dtype):
            temporal = con.execute(
                f"""
                SELECT
                    min({quoted}) AS min_value,
                    max({quoted}) AS max_value,
                    count({quoted}) AS non_null_count
                FROM dataset
                WHERE {quoted} IS NOT NULL
                """
            ).fetchone()

            profile["temporal"] = {
                "count": int(temporal[2] or 0),
                "min": str(temporal[0]) if temporal[0] is not None else None,
                "max": str(temporal[1]) if temporal[1] is not None else None,
            }

        else:
            value_counts = con.execute(
                f"""
                SELECT
                    CAST({quoted} AS VARCHAR) AS value,
                    count(*) AS cnt
                FROM dataset
                WHERE {quoted} IS NOT NULL
                GROUP BY 1
                ORDER BY cnt DESC
                LIMIT {int(top_categories)}
                """
            ).fetchall()

            non_null_count = rows - null_count

            category_shares = {
                str(value): float(count / non_null_count)
                for value, count in value_counts
                if non_null_count
            }

            top_values = [str(value) for value, _ in value_counts]

            profile["categorical"] = {
                "count": non_null_count,
                "unique_count": unique_count,
                "top_values": top_values,
                "category_shares": category_shares,
                "dominant_share": float(value_counts[0][1] / non_null_count) if value_counts and non_null_count else 0.0,
            }

        column_profiles[column] = profile

    row_duplicate_count = int(
        con.execute(
            """
            SELECT COALESCE(SUM(c - 1), 0)
            FROM (
                SELECT count(*) AS c
                FROM dataset
                GROUP BY ALL
                HAVING count(*) > 1
            )
            """
        ).fetchone()[0]
    )

    key_candidates = [
        column
        for column in column_profiles
        if column.lower() in {"id", "uuid", "guid", "pk"}
        or column.lower().endswith("_id")
        or column.lower().startswith("id_")
    ]

    key_duplicates: dict[str, dict] = {}

    for column in key_candidates:
        quoted = _quote_identifier(column)

        result = con.execute(
            f"""
            SELECT
                count(*) AS duplicate_keys,
                COALESCE(SUM(c - 1), 0) AS duplicate_rows
            FROM (
                SELECT {quoted}, count(*) AS c
                FROM dataset
                WHERE {quoted} IS NOT NULL
                GROUP BY {quoted}
                HAVING count(*) > 1
            )
            """
        ).fetchone()

        duplicate_keys = int(result[0] or 0)
        duplicate_rows = int(result[1] or 0)
        unique_count = int(column_profiles[column].get("unique_count", 0))

        key_duplicates[column] = {
            "unique_count": unique_count,
            "duplicate_keys": duplicate_keys,
            "duplicate_rows": duplicate_rows,
            "duplicate_rate": float(duplicate_rows / unique_count) if unique_count else 0.0,
        }

    con.close()

    return {
        "rows": rows,
        "columns": list(column_profiles.keys()),
        "column_profiles": column_profiles,
        "row_duplicate_count": row_duplicate_count,
        "row_duplicate_rate": float(row_duplicate_count / rows) if rows else 0.0,
        "key_duplicates": key_duplicates,
    }