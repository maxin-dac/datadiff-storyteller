from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from core.findings import make_finding
from core.i18n import (
    nar_dist_categorical,
    nar_dist_numeric,
    nar_dup_key,
    nar_dup_rows,
    nar_nulls,
    nar_outliers,
    nar_quality_all_null,
    nar_quality_cardinality,
    nar_quality_constant,
    nar_rule_age,
    nar_rule_email,
    nar_rule_negative,
    nar_schema_added,
    nar_schema_no_common,
    nar_schema_removed,
    nar_schema_renamed,
    nar_schema_type,
    nar_volume,
)
from core.scoring import SEVERITY_RANK, sort_findings
from models.schemas import ColumnMapping, Finding


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    best: dict[str, Finding] = {}
    for finding in findings:
        current = best.get(finding.id)
        if current is None:
            best[finding.id] = finding
            continue
        if SEVERITY_RANK.get(finding.severity, 99) < SEVERITY_RANK.get(current.severity, 99):
            best[finding.id] = finding
    return sort_findings(list(best.values()))


def _is_numeric_profile(profile: dict) -> bool:
    return isinstance(profile.get("numeric"), dict)


def _is_categorical_profile(profile: dict) -> bool:
    return isinstance(profile.get("categorical"), dict)


def calculate_psi(baseline_values: pd.Series, compare_values: pd.Series, bins: int = 10) -> float:
    baseline = pd.to_numeric(baseline_values, errors="coerce").dropna().astype(float)
    compare = pd.to_numeric(compare_values, errors="coerce").dropna().astype(float)

    if baseline.empty or compare.empty:
        return 0.0

    quantiles = np.linspace(0, 1, bins + 1)
    breakpoints = np.unique(np.quantile(baseline, quantiles))

    if len(breakpoints) < 3:
        return 0.0

    breakpoints = breakpoints.astype(float)
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    baseline_counts, _ = np.histogram(baseline, bins=breakpoints)
    compare_counts, _ = np.histogram(compare, bins=breakpoints)

    baseline_pct = baseline_counts / len(baseline)
    compare_pct = compare_counts / len(compare)

    epsilon = 1e-4
    baseline_pct = np.where(baseline_pct == 0, epsilon, baseline_pct)
    compare_pct = np.where(compare_pct == 0, epsilon, compare_pct)

    psi = np.sum((compare_pct - baseline_pct) * np.log(compare_pct / baseline_pct))
    return float(psi)


def _volume_findings(pb, pc, mb, mc, lang):
    rows_b = int(pb.get("rows", 0))
    rows_c = int(pc.get("rows", 0))
    delta_rows = rows_c - rows_b
    delta_pct = (delta_rows / rows_b) if rows_b else None

    if rows_b == 0:
        severity = "info"
    else:
        abs_pct = abs(delta_pct)
        if abs_pct >= 0.50:
            severity = "high"
        elif abs_pct >= 0.20:
            severity = "medium"
        elif abs_pct >= 0.05:
            severity = "low"
        else:
            severity = "info"

    title, narrative, reco = nar_volume(lang, rows_b, rows_c, delta_rows, delta_pct)
    if severity == "info":
        reco = None

    return [
        make_finding(
            finding_id="volume_row_count_change",
            category="volume",
            severity=severity,
            title=title,
            narrative=narrative,
            columns=[],
            metrics={
                "baseline_rows": rows_b,
                "compare_rows": rows_c,
                "delta_rows": delta_rows,
                "delta_percent": delta_pct,
                "baseline_name": mb.get("name"),
                "compare_name": mc.get("name"),
            },
            recommendation=reco,
        )
    ]


def _schema_findings(mappings, pb, pc, lang):
    findings = []
    bp = pb.get("column_profiles", {})
    cp = pc.get("column_profiles", {})

    for mapping in mappings:
        if mapping.mapping_type == "added":
            column = mapping.compare_column
            title, narrative, reco = nar_schema_added(lang, column)
            findings.append(make_finding(
                finding_id=f"schema_added_{column}", category="schema", severity="low",
                title=title, narrative=narrative, columns=[column] if column else [],
                metrics={"mapping_type": "added"}, recommendation=reco,
            ))
        elif mapping.mapping_type == "removed":
            column = mapping.baseline_column
            title, narrative, reco = nar_schema_removed(lang, column)
            findings.append(make_finding(
                finding_id=f"schema_removed_{column}", category="schema", severity="medium",
                title=title, narrative=narrative, columns=[column] if column else [],
                metrics={"mapping_type": "removed"}, recommendation=reco,
            ))
        elif mapping.mapping_type == "renamed":
            b, c = mapping.baseline_column, mapping.compare_column
            severity = "info" if mapping.confidence >= 0.85 else "low"
            title, narrative, reco = nar_schema_renamed(lang, b, c, mapping.confidence)
            findings.append(make_finding(
                finding_id=f"schema_renamed_{b}_{c}", category="schema", severity=severity,
                title=title, narrative=narrative, columns=[b, c],
                metrics={"mapping_type": "renamed", "confidence": mapping.confidence}, recommendation=reco,
            ))

        if mapping.baseline_column and mapping.compare_column:
            bprof = bp.get(mapping.baseline_column, {})
            cprof = cp.get(mapping.compare_column, {})
            dtype_b = bprof.get("dtype")
            dtype_c = cprof.get("dtype")
            if dtype_b and dtype_c and dtype_b != dtype_c:
                bn = _is_numeric_profile(bprof)
                cn = _is_numeric_profile(cprof)
                if bn and cn:
                    severity, interpretation = "low", ("changement numérique probablement mineur" if lang == "fr" else "likely minor numeric change")
                elif bn and not cn:
                    severity, interpretation = "high", ("perte potentielle de typage numérique" if lang == "fr" else "potential loss of numeric typing")
                elif not bn and cn:
                    severity, interpretation = "medium", ("conversion vers un type numérique" if lang == "fr" else "conversion to a numeric type")
                else:
                    severity, interpretation = "medium", ("changement de type non numérique" if lang == "fr" else "non-numeric type change")
                title, narrative, reco = nar_schema_type(lang, mapping.baseline_column, mapping.compare_column, dtype_b, dtype_c, interpretation)
                findings.append(make_finding(
                    finding_id=f"schema_type_{mapping.baseline_column}_{mapping.compare_column}",
                    category="schema", severity=severity, title=title, narrative=narrative,
                    columns=[mapping.baseline_column, mapping.compare_column],
                    metrics={"baseline_dtype": dtype_b, "compare_dtype": dtype_c}, recommendation=reco,
                ))
    return findings


def _null_findings(mappings, pb, pc, lang):
    findings = []
    bp = pb.get("column_profiles", {})
    cp = pc.get("column_profiles", {})
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        rate_b = float(bp.get(mapping.baseline_column, {}).get("null_rate", 0.0))
        rate_c = float(cp.get(mapping.compare_column, {}).get("null_rate", 0.0))
        delta = rate_c - rate_b
        if abs(delta) < 0.02:
            continue
        if delta >= 0.30 or (rate_c >= 0.99 and rate_b < 0.99):
            severity = "critical"
        elif delta >= 0.15:
            severity = "high"
        elif delta >= 0.05:
            severity = "medium"
        elif delta > 0:
            severity = "low"
        elif delta <= -0.15:
            severity = "info"
        else:
            severity = "low"
        title, narrative, reco = nar_nulls(lang, mapping.compare_column, rate_b, rate_c, delta, delta > 0)
        findings.append(make_finding(
            finding_id=f"nulls_{mapping.compare_column}", category="nulls", severity=severity,
            title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
            metrics={"baseline_null_rate": rate_b, "compare_null_rate": rate_c, "absolute_delta": delta},
            recommendation=reco,
        ))
    return findings


def _distribution_findings(df_b, df_c, pb, pc, mappings, lang):
    findings = []
    bp = pb.get("column_profiles", {})
    cp = pc.get("column_profiles", {})
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        bprof = bp.get(mapping.baseline_column, {})
        cprof = cp.get(mapping.compare_column, {})

        if _is_numeric_profile(bprof) and _is_numeric_profile(cprof):
            bs = bprof["numeric"]
            cs = cprof["numeric"]
            if bs.get("count", 0) == 0 or cs.get("count", 0) == 0:
                continue
            psi = calculate_psi(df_b[mapping.baseline_column], df_c[mapping.compare_column])
            med_b, med_c = bs.get("q50"), cs.get("q50")
            mean_b, mean_c = bs.get("mean"), cs.get("mean")
            median_delta = (med_c - med_b) if (med_b is not None and med_c is not None) else None
            severity = "info"
            if psi >= 0.25:
                severity = "high"
            elif psi >= 0.10:
                severity = "medium"
            elif median_delta is not None and med_b not in (None, 0):
                if abs(median_delta / max(1e-9, abs(med_b))) >= 0.20:
                    severity = "low"
            if severity == "info":
                continue
            strength = ("fort" if psi >= 0.25 else "modéré") if lang == "fr" else ("strong" if psi >= 0.25 else "moderate")
            title, narrative, reco = nar_dist_numeric(lang, mapping.compare_column, psi, med_b, med_c, mean_b, mean_c, strength)
            findings.append(make_finding(
                finding_id=f"distribution_numeric_{mapping.compare_column}", category="distribution",
                severity=severity, title=title, narrative=narrative,
                columns=[mapping.baseline_column, mapping.compare_column],
                metrics={"psi": psi, "baseline_median": med_b, "compare_median": med_c,
                         "baseline_mean": mean_b, "compare_mean": mean_c},
                recommendation=reco,
            ))

        if _is_categorical_profile(bprof) and _is_categorical_profile(cprof):
            bc = bprof["categorical"]
            cc = cprof["categorical"]
            bshares = bc.get("category_shares", {})
            cshares = cc.get("category_shares", {})
            all_cats = set(bshares) | set(cshares)
            new_cats = sorted(set(cshares) - set(bshares))
            removed_cats = sorted(set(bshares) - set(cshares))
            max_shift, max_cat = 0.0, None
            for cat in all_cats:
                shift = abs(float(cshares.get(cat, 0.0)) - float(bshares.get(cat, 0.0)))
                if shift > max_shift:
                    max_shift, max_cat = shift, cat
            significant_new = [c for c in new_cats if float(cshares.get(c, 0.0)) >= 0.05]
            severity = "info"
            if significant_new or max_shift >= 0.15:
                severity = "high"
            elif new_cats or removed_cats or max_shift >= 0.08:
                severity = "medium"
            elif max_shift >= 0.03:
                severity = "low"
            if severity == "info":
                continue
            parts = []
            if significant_new:
                if lang == "fr":
                    parts.append("De nouvelles catégories significatives apparaissent : " + ", ".join(f"{c} ({float(cshares.get(c,0)):.1%})" for c in significant_new[:5]))
                else:
                    parts.append("New significant categories appear: " + ", ".join(f"{c} ({float(cshares.get(c,0)):.1%})" for c in significant_new[:5]))
            elif new_cats:
                parts.append(("De nouvelles catégories apparaissent : " if lang == "fr" else "New categories appear: ") + ", ".join(new_cats[:5]))
            if removed_cats:
                parts.append(("Des catégories disparaissent : " if lang == "fr" else "Categories disappear: ") + ", ".join(removed_cats[:5]))
            if max_cat is not None and max_shift >= 0.03:
                if lang == "fr":
                    parts.append(f"Le plus fort déplacement de fréquence concerne la catégorie {max_cat}, avec un écart de {max_shift:.1%}.")
                else:
                    parts.append(f"The largest frequency shift concerns category {max_cat}, with a gap of {max_shift:.1%}.")
            title, narrative, reco = nar_dist_categorical(lang, mapping.compare_column, parts)
            findings.append(make_finding(
                finding_id=f"distribution_categorical_{mapping.compare_column}", category="distribution",
                severity=severity, title=title, narrative=narrative,
                columns=[mapping.baseline_column, mapping.compare_column],
                metrics={"new_categories": new_cats, "removed_categories": removed_cats,
                         "max_frequency_shift": max_shift, "max_shift_category": max_cat},
                recommendation=reco,
            ))
    return findings


def _outlier_findings(df_b, df_c, pb, pc, mappings, lang):
    findings = []
    bp = pb.get("column_profiles", {})
    cp = pc.get("column_profiles", {})
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        bprof = bp.get(mapping.baseline_column, {})
        cprof = cp.get(mapping.compare_column, {})
        if not _is_numeric_profile(bprof) or not _is_numeric_profile(cprof):
            continue
        bs = bprof["numeric"]
        lower, upper = bs.get("lower_bound"), bs.get("upper_bound")
        if lower is None or upper is None:
            continue
        series = pd.to_numeric(df_c[mapping.compare_column], errors="coerce").dropna().astype(float)
        if series.empty:
            continue
        mask = (series < lower) | (series > upper)
        count = int(mask.sum())
        rate_c = float(count / len(series))
        rate_b = float(bs.get("outlier_rate", 0.0))
        if count == 0:
            continue
        if rate_c >= 0.05 or count >= 100:
            severity = "high"
        elif rate_c - rate_b >= 0.01 or count >= 20:
            severity = "medium"
        else:
            continue
        sample = series[mask].astype(str).head(10).tolist()
        title, narrative, reco = nar_outliers(lang, mapping.compare_column, count, lower, upper, rate_b, rate_c)
        findings.append(make_finding(
            finding_id=f"outliers_{mapping.compare_column}", category="outliers", severity=severity,
            title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
            metrics={"baseline_lower_bound": lower, "baseline_upper_bound": upper,
                     "compare_outlier_count": count, "compare_outlier_rate": rate_c, "baseline_outlier_rate": rate_b},
            evidence={"sample_values": sample}, recommendation=reco,
        ))
    return findings


def _business_rule_findings(df_b, df_c, mappings, lang):
    findings = []
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        column = mapping.compare_column
        lowered = column.lower()

        if "age" in lowered:
            bv = pd.to_numeric(df_b[mapping.baseline_column], errors="coerce")
            cv = pd.to_numeric(df_c[mapping.compare_column], errors="coerce")
            invalid_b = int(((bv < 0) | (bv > 120)).sum())
            mask = (cv < 0) | (cv > 120)
            invalid_c = int(mask.sum())
            new_invalid = invalid_c - invalid_b
            if new_invalid > 0:
                sample = cv[mask].astype(str).head(10).tolist()
                title, narrative, reco = nar_rule_age(lang, column, invalid_c, invalid_b, new_invalid)
                findings.append(make_finding(
                    finding_id=f"business_rule_age_{column}", category="business_rule",
                    severity="high" if new_invalid >= 50 else "medium", title=title, narrative=narrative,
                    columns=[mapping.baseline_column, mapping.compare_column],
                    metrics={"baseline_invalid_count": invalid_b, "compare_invalid_count": invalid_c, "new_invalid_count": new_invalid},
                    evidence={"sample_values": sample}, recommendation=reco,
                ))

        if "email" in lowered:
            bv = df_b[mapping.baseline_column].dropna().astype(str)
            cv = df_c[mapping.compare_column].dropna().astype(str)
            invalid_b = int((~bv.str.contains("@", regex=False)).sum())
            mask = ~cv.str.contains("@", regex=False)
            invalid_c = int(mask.sum())
            rate_c = invalid_c / len(cv) if len(cv) else 0.0
            if invalid_c > invalid_b and rate_c >= 0.01:
                sample = cv[mask].head(10).tolist()
                title, narrative, reco = nar_rule_email(lang, column, invalid_c, rate_c)
                findings.append(make_finding(
                    finding_id=f"business_rule_email_{column}", category="business_rule",
                    severity="medium" if rate_c < 0.05 else "high", title=title, narrative=narrative,
                    columns=[mapping.baseline_column, mapping.compare_column],
                    metrics={"baseline_invalid_count": invalid_b, "compare_invalid_count": invalid_c, "compare_invalid_rate": rate_c},
                    evidence={"sample_values": sample}, recommendation=reco,
                ))

        if any(tok in lowered for tok in ["amount", "value", "price", "revenue", "ca", "montant", "lifetime"]):
            bv = pd.to_numeric(df_b[mapping.baseline_column], errors="coerce")
            cv = pd.to_numeric(df_c[mapping.compare_column], errors="coerce")
            neg_b = int((bv < 0).sum())
            mask = cv < 0
            neg_c = int(mask.sum())
            if neg_c - neg_b > 0:
                sample = cv[mask].astype(str).head(10).tolist()
                title, narrative, reco = nar_rule_negative(lang, column, neg_c, neg_b)
                findings.append(make_finding(
                    finding_id=f"business_rule_negative_{column}", category="business_rule",
                    severity="medium" if (neg_c - neg_b) < 50 else "high", title=title, narrative=narrative,
                    columns=[mapping.baseline_column, mapping.compare_column],
                    metrics={"baseline_negative_count": neg_b, "compare_negative_count": neg_c},
                    evidence={"sample_values": sample}, recommendation=reco,
                ))
    return findings


def _duplicate_findings(pb, pc, mappings, lang):
    findings = []
    rb = float(pb.get("row_duplicate_rate", 0.0))
    rc = float(pc.get("row_duplicate_rate", 0.0))
    delta = rc - rb
    if abs(delta) >= 0.005:
        if delta >= 0.05:
            severity = "high"
        elif delta >= 0.01:
            severity = "medium"
        elif delta > 0:
            severity = "low"
        else:
            severity = "info"
        title, narrative, reco = nar_dup_rows(lang, rb, rc, delta > 0)
        findings.append(make_finding(
            finding_id="duplicates_row_level", category="duplicates", severity=severity,
            title=title, narrative=narrative, columns=[],
            metrics={"baseline_row_duplicate_rate": rb, "compare_row_duplicate_rate": rc, "delta": delta},
            recommendation=reco,
        ))

    bk = pb.get("key_duplicates", {})
    ck = pc.get("key_duplicates", {})
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        bkey = bk.get(mapping.baseline_column)
        ckey = ck.get(mapping.compare_column)
        if not bkey or not ckey:
            continue
        dup_b = int(bkey.get("duplicate_rows", 0))
        dup_c = int(ckey.get("duplicate_rows", 0))
        d = dup_c - dup_b
        if d <= 0:
            continue
        rate_b = float(bkey.get("duplicate_rate", 0.0))
        rate_c = float(ckey.get("duplicate_rate", 0.0))
        if rate_c >= 0.05 or d >= 1000:
            severity = "high"
        elif rate_c >= 0.01 or d >= 100:
            severity = "medium"
        else:
            severity = "low"
        title, narrative, reco = nar_dup_key(lang, mapping.compare_column, dup_b, dup_c, rate_b, rate_c)
        findings.append(make_finding(
            finding_id=f"duplicates_key_{mapping.compare_column}", category="duplicates", severity=severity,
            title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
            metrics={"baseline_duplicate_rows": dup_b, "compare_duplicate_rows": dup_c,
                     "baseline_duplicate_rate": rate_b, "compare_duplicate_rate": rate_c},
            recommendation=reco,
        ))
    return findings


def _quality_findings(mappings, pb, pc, lang):
    findings = []
    bp = pb.get("column_profiles", {})
    cp = pc.get("column_profiles", {})
    for mapping in mappings:
        if not mapping.baseline_column or not mapping.compare_column:
            continue
        bprof = bp.get(mapping.baseline_column, {})
        cprof = cp.get(mapping.compare_column, {})
        rate_b = float(bprof.get("null_rate", 0.0))
        rate_c = float(cprof.get("null_rate", 0.0))
        unique_b = int(bprof.get("unique_count", 0))
        unique_c = int(cprof.get("unique_count", 0))

        if rate_c >= 0.999 and rate_b < 0.999:
            title, narrative, reco = nar_quality_all_null(lang, mapping.compare_column, rate_c)
            findings.append(make_finding(
                finding_id=f"quality_all_null_{mapping.compare_column}", category="quality", severity="critical",
                title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
                metrics={"baseline_null_rate": rate_b, "compare_null_rate": rate_c}, recommendation=reco,
            ))
        if unique_b > 10 and unique_c <= 1 and rate_c < 0.99:
            title, narrative, reco = nar_quality_constant(lang, mapping.compare_column, unique_b)
            findings.append(make_finding(
                finding_id=f"quality_constant_{mapping.compare_column}", category="quality", severity="medium",
                title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
                metrics={"baseline_unique_count": unique_b, "compare_unique_count": unique_c}, recommendation=reco,
            ))
        if unique_b > 20 and unique_c < unique_b * 0.2:
            title, narrative, reco = nar_quality_cardinality(lang, mapping.compare_column, unique_b, unique_c)
            findings.append(make_finding(
                finding_id=f"quality_cardinality_drop_{mapping.compare_column}", category="quality", severity="low",
                title=title, narrative=narrative, columns=[mapping.baseline_column, mapping.compare_column],
                metrics={"baseline_unique_count": unique_b, "compare_unique_count": unique_c}, recommendation=reco,
            ))
    return findings


def generate_findings(
    df_baseline, df_compare, profile_baseline, profile_compare, mappings,
    meta_baseline=None, meta_compare=None, lang: Optional[str] = None,
) -> list[Finding]:
    meta_baseline = meta_baseline or {}
    meta_compare = meta_compare or {}
    lang = lang or "fr"

    findings: list[Finding] = []

    common = [m for m in mappings if m.baseline_column and m.compare_column]
    if not common:
        title, narrative, reco = nar_schema_no_common(lang)
        findings.append(make_finding(
            finding_id="schema_no_common_columns", category="schema", severity="high",
            title=title, narrative=narrative, columns=[], metrics={"common_column_count": 0}, recommendation=reco,
        ))

    findings.extend(_volume_findings(profile_baseline, profile_compare, meta_baseline, meta_compare, lang))
    findings.extend(_schema_findings(mappings, profile_baseline, profile_compare, lang))
    findings.extend(_null_findings(mappings, profile_baseline, profile_compare, lang))
    findings.extend(_distribution_findings(df_baseline, df_compare, profile_baseline, profile_compare, mappings, lang))
    findings.extend(_outlier_findings(df_baseline, df_compare, profile_baseline, profile_compare, mappings, lang))
    findings.extend(_business_rule_findings(df_baseline, df_compare, mappings, lang))
    findings.extend(_duplicate_findings(profile_baseline, profile_compare, mappings, lang))
    findings.extend(_quality_findings(mappings, profile_baseline, profile_compare, lang))

    return _deduplicate_findings(findings)
