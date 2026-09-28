from __future__ import annotations

import difflib
from collections import defaultdict
from typing import Optional

import pandas as pd

from models.schemas import ColumnMapping


def normalize_column_name(name: str) -> str:
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
    )


def name_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_column_name(a), normalize_column_name(b)).ratio()


def content_similarity(
    left: pd.Series,
    right: pd.Series,
    sample_size: int = 5_000,
    random_state: int = 42,
) -> float:
    left_clean = left.dropna()
    right_clean = right.dropna()

    if left_clean.empty and right_clean.empty:
        return 1.0

    if left_clean.empty or right_clean.empty:
        return 0.0

    if len(left_clean) > sample_size:
        left_clean = left_clean.sample(sample_size, random_state=random_state)

    if len(right_clean) > sample_size:
        right_clean = right_clean.sample(sample_size, random_state=random_state)

    left_clean = left_clean.astype(str)
    right_clean = right_clean.astype(str)

    left_set = set(left_clean.tolist())
    right_set = set(right_clean.tolist())

    intersection = len(left_set & right_set)
    union = len(left_set | right_set)

    if union == 0:
        return 0.0

    return float(intersection / union)


def build_column_mappings(
    baseline_df: pd.DataFrame,
    compare_df: pd.DataFrame,
    name_threshold: float = 0.62,
    combined_threshold: float = 0.74,
) -> list[ColumnMapping]:
    baseline_columns = list(baseline_df.columns)
    compare_columns = list(compare_df.columns)

    mappings: list[ColumnMapping] = []

    used_baseline: set[str] = set()
    used_compare: set[str] = set()

    for baseline_col in baseline_columns:
        if baseline_col not in compare_columns or baseline_col in used_baseline:
            continue
        mappings.append(
            ColumnMapping(
                baseline_column=baseline_col,
                compare_column=baseline_col,
                mapping_type="same",
                confidence=1.0,
            )
        )

        used_baseline.add(baseline_col)
        used_compare.add(baseline_col)

    baseline_by_norm: dict[str, list[str]] = defaultdict(list)
    compare_by_norm: dict[str, list[str]] = defaultdict(list)
    for column in baseline_columns:
        if column not in used_baseline:
            baseline_by_norm[normalize_column_name(column)].append(column)
    for column in compare_columns:
        if column not in used_compare:
            compare_by_norm[normalize_column_name(column)].append(column)

    for norm_name, baseline_matches in baseline_by_norm.items():
        compare_matches = compare_by_norm.get(norm_name, [])
        if len(baseline_matches) != 1 or len(compare_matches) != 1:
            continue

        baseline_col = baseline_matches[0]
        compare_col = compare_matches[0]
        mappings.append(
            ColumnMapping(
                baseline_column=baseline_col,
                compare_column=compare_col,
                mapping_type="same",
                confidence=1.0,
            )
        )
        used_baseline.add(baseline_col)
        used_compare.add(compare_col)

    remaining_baseline = [c for c in baseline_columns if c not in used_baseline]
    remaining_compare = [c for c in compare_columns if c not in used_compare]

    # Fuzzy rename detection.
    for baseline_col in remaining_baseline:
        best_match: Optional[str] = None
        best_score = 0.0

        for compare_col in remaining_compare:
            if compare_col in used_compare:
                continue

            n_sim = name_similarity(baseline_col, compare_col)

            if n_sim < name_threshold:
                continue

            c_sim = content_similarity(
                baseline_df[baseline_col],
                compare_df[compare_col],
            )

            score = 0.65 * n_sim + 0.35 * c_sim

            if score > best_score:
                best_score = score
                best_match = compare_col

        if best_match is not None and best_score >= combined_threshold:
            mappings.append(
                ColumnMapping(
                    baseline_column=baseline_col,
                    compare_column=best_match,
                    mapping_type="renamed",
                    confidence=round(float(best_score), 4),
                )
            )
            used_baseline.add(baseline_col)
            used_compare.add(best_match)

    # Removed columns.
    for baseline_col in baseline_columns:
        if baseline_col not in used_baseline:
            mappings.append(
                ColumnMapping(
                    baseline_column=baseline_col,
                    compare_column=None,
                    mapping_type="removed",
                    confidence=1.0,
                )
            )

    # Added columns.
    for compare_col in compare_columns:
        if compare_col not in used_compare:
            mappings.append(
                ColumnMapping(
                    baseline_column=None,
                    compare_column=compare_col,
                    mapping_type="added",
                    confidence=1.0,
                )
            )

    return mappings