from __future__ import annotations

import csv
from io import BytesIO
from pathlib import Path
from typing import Any, Union

import pandas as pd

DEFAULT_ENCODINGS = ("utf-8", "utf-8-sig", "latin1", "cp1252")


def _get_raw_bytes_and_name(source: Union[str, Path, Any]) -> tuple[bytes, str]:
    if hasattr(source, "getvalue"):
        raw_bytes = source.getvalue()
        name = getattr(source, "name", "uploaded_file.csv")
    else:
        path = Path(source)
        raw_bytes = path.read_bytes()
        name = path.name

    return raw_bytes, Path(name).name


def _candidate_seps(sample: str, sep: str) -> list[Any]:
    if sep != "auto":
        return [sep]

    detected = None

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        detected = dialect.delimiter
    except csv.Error:
        detected = None

    candidates: list[Any] = []

    for candidate in [detected, None, ",", ";", "\t", "|"]:
        if candidate not in candidates:
            candidates.append(candidate)

    return candidates


def load_csv(
    source: Union[str, Path, Any],
    max_rows: int = 200_000,
    sep: str = "auto",
    encoding: str = "auto",
) -> tuple[pd.DataFrame, dict]:
    """
    Load a CSV file from a local path, a file-like object, or a Streamlit UploadedFile.

    This loader is intentionally tolerant:
    - tries multiple encodings when encoding="auto";
    - tries multiple separators when sep="auto";
    - keeps the best parsing result based on column count.
    """
    raw_bytes, name = _get_raw_bytes_and_name(source)

    encodings = [encoding] if encoding != "auto" else list(DEFAULT_ENCODINGS)

    best_df: pd.DataFrame | None = None
    best_columns = -1
    last_error: Exception | None = None

    for enc in encodings:
        try:
            sample = raw_bytes[:200_000].decode(enc, errors="ignore")
        except Exception as exc:
            last_error = exc
            continue

        seps = _candidate_seps(sample, sep)

        for current_sep in seps:
            buffer = BytesIO(raw_bytes)

            kwargs: dict[str, Any] = {
                "nrows": int(max_rows),
                "low_memory": False,
                "encoding": enc,
            }

            if current_sep is not None:
                kwargs["sep"] = current_sep

            try:
                df = pd.read_csv(buffer, **kwargs)
            except Exception as exc:
                last_error = exc
                continue

            if df.empty:
                continue

            if len(df.columns) > best_columns:
                best_columns = len(df.columns)
                best_df = df

            if len(df.columns) > 1:
                break

        if best_df is not None and best_columns > 1:
            break

    if best_df is None:
        message = "Impossible de lire le fichier CSV."

        if last_error is not None:
            message = f"{message} Derniere erreur rencontree : {last_error}"

        raise ValueError(message)

    meta = {
        "name": name,
        "rows": int(len(best_df)),
        "columns": int(len(best_df.columns)),
        "column_names": [str(column) for column in best_df.columns],
        "memory_usage_mb": round(
            float(best_df.memory_usage(deep=True).sum() / 1024 / 1024),
            2,
        ),
    }

    return best_df, meta
