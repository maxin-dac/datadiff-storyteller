from __future__ import annotations

from typing import Any, Optional

try:
    import streamlit as _st
except Exception: 
    _st = None

DEFAULT_LANG = "fr"
AVAILABLE_LANGS = ("fr", "en")

TRANSLATIONS: dict[str, dict[str, str]] = {
    # Navigation groups
    "nav_group_start": {"fr": "Démarrage", "en": "Getting started"},
    "nav_group_analysis": {"fr": "Analyse", "en": "Analysis"},
    "nav_group_export": {"fr": "Export", "en": "Export"},
    "nav_views": {"fr": "Écrans de l'application", "en": "Application views"},
    # Page titles
    "page_home": {"fr": "Accueil", "en": "Home"},
    "page_upload": {"fr": "Importer", "en": "Import"},
    "page_overview": {"fr": "Vue d'ensemble", "en": "Overview"},
    "page_schema": {"fr": "Schéma", "en": "Schema"},
    "page_quality": {"fr": "Qualité", "en": "Quality"},
    "page_distributions": {"fr": "Distributions", "en": "Distributions"},
    "page_anomalies": {"fr": "Anomalies", "en": "Anomalies"},
    "page_report": {"fr": "Rapport", "en": "Report"},
    # Brand
    "brand_name": {"fr": "DataDiff Storyteller", "en": "DataDiff Storyteller"},
    "brand_sub": {"fr": "Comparateur de datasets", "en": "Dataset comparator"},
    "lang_label": {"fr": "Langue", "en": "Language"},
    # Home / guide
    "home_title": {"fr": "Accueil", "en": "Home"},
    "home_subtitle": {
        "fr": "Point d'entrée, guide rapide et état de la session courante.",
        "en": "Entry point, quick guide and current session status.",
    },
    "sec_how": {"fr": "Comment utiliser l'application", "en": "How to use the app"},
    "guide_1": {
        "fr": "<strong>Importer</strong> : charger la version de référence et la version à comparer.",
        "en": "<strong>Import</strong>: load the reference version and the version to compare.",
    },
    "guide_2": {
        "fr": "<strong>Analyser</strong> : consulter le schéma, la qualité, les distributions et les anomalies.",
        "en": "<strong>Analyse</strong>: review schema, quality, distributions and anomalies.",
    },
    "guide_3": {
        "fr": "<strong>Restituer</strong> : exporter le rapport en Markdown, JSON ou HTML.",
        "en": "<strong>Deliver</strong>: export the report as Markdown, JSON or HTML.",
    },
    "sec_session": {"fr": "État de la session", "en": "Session status"},
    "home_no_analysis": {
        "fr": "Aucune analyse disponible",
        "en": "No analysis available",
    },
    "home_no_analysis_msg": {
        "fr": "Ouvrez la page Importer pour charger deux fichiers CSV et lancer une comparaison.",
        "en": "Open the Import page to load two CSV files and start a comparison.",
    },
    "home_has_analysis_1": {
        "fr": "Une analyse est déjà disponible dans cette session.",
        "en": "An analysis is already available in this session.",
    },
    "home_has_analysis_2": {
        "fr": "Findings totaux : {total}. Findings critiques : {critical}.",
        "en": "Total findings: {total}. Critical findings: {critical}.",
    },
    "home_has_analysis_3": {
        "fr": "Ouvrez Importer pour lancer une nouvelle comparaison, ou la page Vue d'ensemble pour consulter les résultats.",
        "en": "Open Import to run a new comparison, or the Overview page to review the results.",
    },
    # Upload
    "upload_title": {"fr": "Importer les données", "en": "Import data"},
    "upload_subtitle": {
        "fr": "Chargez deux fichiers CSV et lancez une comparaison structurée.",
        "en": "Load two CSV files and run a structured comparison.",
    },
    "sidebar_import_settings": {"fr": "Paramètres d'import", "en": "Import settings"},
    "opt_max_rows": {"fr": "Lignes maximales par fichier", "en": "Max rows per file"},
    "opt_max_rows_help": {
        "fr": "Limite la charge mémoire pendant l'analyse Pandas.",
        "en": "Limits memory usage during the Pandas analysis.",
    },
    "opt_separator": {"fr": "Séparateur", "en": "Separator"},
    "opt_separator_help": {
        "fr": "Laissez automatique pour laisser l'outil détecter le séparateur.",
        "en": "Leave automatic to let the tool detect the separator.",
    },
    "sep_auto": {"fr": "Automatique", "en": "Automatic"},
    "sep_comma": {"fr": "Virgule", "en": "Comma"},
    "sep_semicolon": {"fr": "Point-virgule", "en": "Semicolon"},
    "sep_tab": {"fr": "Tabulation", "en": "Tab"},
    "sep_pipe": {"fr": "Tube", "en": "Pipe"},
    "opt_encoding": {"fr": "Encodage", "en": "Encoding"},
    "opt_encoding_help": {
        "fr": "Laissez auto pour tester plusieurs encodages courants.",
        "en": "Leave auto to try several common encodings.",
    },
    "enc_auto": {"fr": "auto", "en": "auto"},
    "opt_duckdb": {"fr": "Profilage DuckDB expérimental", "en": "Experimental DuckDB profiling"},
    "opt_duckdb_help": {
        "fr": "Utilise DuckDB pour calculer les profils. L'analyse détaillée reste basée sur Pandas dans ce MVP.",
        "en": "Uses DuckDB to compute profiles. Detailed analysis still relies on Pandas in this MVP.",
    },
    "sec_files": {"fr": "Fichiers à comparer", "en": "Files to compare"},
    "file_baseline": {"fr": "Version de référence", "en": "Reference version"},
    "file_baseline_help": {
        "fr": "Premier fichier, souvent la version antérieure.",
        "en": "First file, usually the earlier version.",
    },
    "file_compare": {"fr": "Version à comparer", "en": "Version to compare"},
    "file_compare_help": {
        "fr": "Second fichier, souvent la version postérieure.",
        "en": "Second file, usually the later version.",
    },
    "sec_run": {"fr": "Lancer l'analyse", "en": "Run the analysis"},
    "btn_analyze": {"fr": "Analyser les fichiers importés", "en": "Analyze imported files"},
    "err_two_files": {"fr": "Veuillez sélectionner deux fichiers CSV.", "en": "Please select two CSV files."},
    "spinner_analyzing": {"fr": "Chargement, profilage et comparaison...", "en": "Loading, profiling and comparing..."},
    "warn_no_common": {
        "fr": "Les deux fichiers ne partagent aucune colonne commune après normalisation. La comparaison sera limitée au schéma et au volume.",
        "en": "The two files share no common column after normalization. Comparison will be limited to schema and volume.",
    },
    "success_done": {
        "fr": "Analyse terminée. Consultez Vue d'ensemble, Qualité, Distributions, Anomalies et Rapport.",
        "en": "Analysis complete. See Overview, Quality, Distributions, Anomalies and Report.",
    },
    "err_analysis": {"fr": "Erreur pendant l'analyse : {error}", "en": "Error during analysis: {error}"},
    "sec_current_session": {"fr": "Session courante", "en": "Current session"},
    "info_no_analysis_yet": {
        "fr": "Aucune analyse n'a encore été lancée dans cette session.",
        "en": "No analysis has been run yet in this session.",
    },
    "btn_reset": {"fr": "Réinitialiser l'analyse", "en": "Reset analysis"},
    "kpi_baseline": {"fr": "baseline", "en": "baseline"},
    "kpi_compare": {"fr": "compare", "en": "compare"},
    "kpi_findings_count": {"fr": "findings_count", "en": "findings_count"},
    "kpi_common_columns": {"fr": "common_columns", "en": "common_columns"},
    # Overview
    "overview_title": {"fr": "Vue d'ensemble", "en": "Overview"},
    "overview_subtitle": {"fr": "Synthèse des changements les plus importants.", "en": "Summary of the most important changes."},
    "sec_kpi": {"fr": "Indicateurs clés", "en": "Key indicators"},
    "kpi_health": {"fr": "Score de santé", "en": "Health score"},
    "kpi_grade": {"fr": "Grade {grade}", "en": "Grade {grade}"},
    "kpi_rows": {"fr": "Lignes", "en": "Rows"},
    "kpi_rows_baseline": {"fr": "Baseline : {value}", "en": "Baseline: {value}"},
    "kpi_volume_change": {"fr": "Variation de volume", "en": "Volume change"},
    "kpi_rows_delta": {"fr": "{value} lignes", "en": "{value} rows"},
    "kpi_columns": {"fr": "Colonnes", "en": "Columns"},
    "kpi_critical": {"fr": "Critiques", "en": "Critical"},
    "kpi_critical_help": {"fr": "Actions immédiates", "en": "Immediate action"},
    "kpi_high": {"fr": "Élevés", "en": "High"},
    "kpi_high_help": {"fr": "À investiguer", "en": "To investigate"},
    "kpi_medium": {"fr": "Moyens", "en": "Medium"},
    "kpi_medium_help": {"fr": "Surveillance", "en": "Monitoring"},
    "kpi_total": {"fr": "Total findings", "en": "Total findings"},
    "kpi_total_help": {"fr": "Changements structurés", "en": "Structured changes"},
    "sec_exec_summary": {"fr": "Résumé exécutif", "en": "Executive summary"},
    "sec_null_rates": {"fr": "Taux de valeurs manquantes", "en": "Missing-value rates"},
    "chart_null_title": {"fr": "Comparaison des taux de valeurs manquantes", "en": "Missing-rate comparison"},
    "info_no_common_col": {"fr": "Aucune colonne commune à comparer.", "en": "No common column to compare."},
    "sec_top_findings": {"fr": "Principaux findings", "en": "Top findings"},
    "success_no_finding": {"fr": "Aucun finding significatif détecté.", "en": "No significant finding detected."},
    # Schema
    "schema_title": {"fr": "Schéma", "en": "Schema"},
    "schema_subtitle": {
        "fr": "Colonnes ajoutées, supprimées, renommées et types modifiés.",
        "en": "Added, removed, renamed columns and modified types.",
    },
    "sec_mappings": {"fr": "Correspondances de colonnes", "en": "Column mappings"},
    "col_baseline_column": {"fr": "baseline_column", "en": "baseline_column"},
    "col_compare_column": {"fr": "compare_column", "en": "compare_column"},
    "col_mapping_type": {"fr": "mapping_type", "en": "mapping_type"},
    "col_confidence": {"fr": "Confiance", "en": "Confidence"},
    "info_no_mapping": {"fr": "Aucune correspondance de colonne disponible.", "en": "No column mapping available."},
    "sec_schema_findings": {"fr": "Findings de schéma", "en": "Schema findings"},
    "success_no_schema": {"fr": "Aucun changement de schéma significatif détecté.", "en": "No significant schema change detected."},
    # Quality
    "quality_title": {"fr": "Qualité des données", "en": "Data quality"},
    "quality_subtitle": {
        "fr": "Valeurs manquantes, doublons et dégradations structurales.",
        "en": "Missing values, duplicates and structural degradations.",
    },
    "sec_quality_kpi": {"fr": "Indicateurs de qualité", "en": "Quality indicators"},
    "kpi_dup_rows_baseline": {"fr": "Doublons lignes baseline", "en": "Baseline row duplicates"},
    "kpi_dup_rows_lines": {"fr": "{value} lignes", "en": "{value} rows"},
    "kpi_dup_rows_compare": {"fr": "Doublons lignes comparaison", "en": "Compare row duplicates"},
    "kpi_null_findings": {"fr": "Findings nulls", "en": "Null findings"},
    "kpi_null_findings_help": {"fr": "Valeurs manquantes", "en": "Missing values"},
    "kpi_quality_findings": {"fr": "Findings qualité", "en": "Quality findings"},
    "kpi_quality_findings_help": {"fr": "Colonnes nulles ou constantes", "en": "All-null or constant columns"},
    "sec_null_compare": {"fr": "Comparaison des valeurs manquantes", "en": "Missing-value comparison"},
    "col_column": {"fr": "column", "en": "column"},
    "col_baseline": {"fr": "baseline", "en": "baseline"},
    "col_compare": {"fr": "compare", "en": "compare"},
    "col_delta": {"fr": "delta", "en": "delta"},
    "chart_null_by_col": {"fr": "Taux de valeurs manquantes par colonne", "en": "Missing rate by column"},
    "sec_quality_findings": {"fr": "Findings de qualité", "en": "Quality findings"},
    "success_no_quality": {"fr": "Aucune dégradation de qualité majeure détectée.", "en": "No major quality degradation detected."},
    # Distributions
    "dist_title": {"fr": "Distributions", "en": "Distributions"},
    "dist_subtitle": {
        "fr": "Évolution des distributions numériques et catégorielles.",
        "en": "Evolution of numeric and categorical distributions.",
    },
    "sel_column": {"fr": "Colonne à analyser", "en": "Column to analyze"},
    "sec_dist_stats": {"fr": "Statistiques comparées", "en": "Compared statistics"},
    "col_metric": {"fr": "metric", "en": "metric"},
    "info_not_enough_numeric": {
        "fr": "Pas assez de valeurs numériques non nulles dans au moins une des deux versions pour afficher les graphiques de distribution.",
        "en": "Not enough non-null numeric values in at least one version to draw distribution charts.",
    },
    "info_no_category": {"fr": "Aucune catégorie non nulle disponible pour cette colonne.", "en": "No non-null category available for this column."},
    "info_no_profile": {"fr": "Cette colonne n'a pas de profil numérique ou catégoriel comparable.", "en": "This column has no comparable numeric or categorical profile."},
    "sec_dist_findings": {"fr": "Findings de distribution", "en": "Distribution findings"},
    "success_no_dist": {"fr": "Aucun changement de distribution significatif pour cette colonne.", "en": "No significant distribution change for this column."},
    "chart_hist_title": {"fr": "Distribution de {column}", "en": "Distribution of {column}"},
    "chart_box_title": {"fr": "Boxplot comparatif de {column}", "en": "Comparative boxplot of {column}"},
    "chart_cat_title": {"fr": "Répartition catégorielle de {column}", "en": "Categorical breakdown of {column}"},
    "axis_density": {"fr": "Densité", "en": "Density"},
    "axis_share": {"fr": "Part relative", "en": "Relative share"},
    "axis_category": {"fr": "Catégorie", "en": "Category"},
    "legend_baseline": {"fr": "Baseline", "en": "Baseline"},
    "legend_compare": {"fr": "Comparaison", "en": "Compare"},
    # Anomalies
    "anom_title": {"fr": "Anomalies", "en": "Anomalies"},
    "anom_subtitle": {"fr": "Valeurs extrêmes et violations de règles métier simples.", "en": "Extreme values and simple business-rule violations."},
    "sec_anom_summary": {"fr": "Synthèse", "en": "Summary"},
    "success_no_anom": {"fr": "Aucune anomalie majeure détectée.", "en": "No major anomaly detected."},
    "anom_count": {"fr": "{value} anomalies ou règles métier violées.", "en": "{value} anomalies or business-rule violations."},
    "sec_anom_details": {"fr": "Détails", "en": "Details"},
    "exp_sample_values": {"fr": "Valeurs exemples", "en": "Sample values"},
    # Report
    "report_title": {"fr": "Rapport", "en": "Report"},
    "report_subtitle": {"fr": "Export du récit automatique et des findings structurés.", "en": "Export of the automatic narrative and structured findings."},
    "sec_report_findings": {"fr": "Findings", "en": "Findings"},
    "sec_exports": {"fr": "Exports", "en": "Exports"},
    "btn_md": {"fr": "Télécharger Markdown", "en": "Download Markdown"},
    "btn_json": {"fr": "Télécharger JSON", "en": "Download JSON"},
    "btn_html": {"fr": "Télécharger HTML", "en": "Download HTML"},
    # Report document labels
    "doc_app_title": {"fr": "DataDiff Storyteller - Rapport", "en": "DataDiff Storyteller - Report"},
    "doc_subtitle": {"fr": "Rapport comparatif de dataset", "en": "Dataset comparison report"},
    "doc_baseline": {"fr": "Baseline", "en": "Baseline"},
    "doc_compare": {"fr": "Comparaison", "en": "Comparison"},
    "doc_baseline_rows": {"fr": "Lignes baseline", "en": "Baseline rows"},
    "doc_compare_rows": {"fr": "Lignes comparaison", "en": "Compare rows"},
    "doc_generated_at": {"fr": "Généré le", "en": "Generated at"},
    "doc_exec_summary": {"fr": "Résumé exécutif", "en": "Executive summary"},
    "doc_changes": {"fr": "Changements détectés", "en": "Detected changes"},
    "doc_no_change": {"fr": "Aucun changement significatif détecté.", "en": "No significant change detected."},
    "doc_columns": {"fr": "Colonnes", "en": "Columns"},
    "doc_category": {"fr": "Catégorie", "en": "Category"},
    "doc_recommendation": {"fr": "Recommandation", "en": "Recommendation"},
    "doc_metrics": {"fr": "Métriques", "en": "Metrics"},
    "doc_evidence": {"fr": "Preuves", "en": "Evidence"},
    "doc_footer": {"fr": "Rapport généré par DataDiff Storyteller.", "en": "Report generated by DataDiff Storyteller."},
    # Finding card labels
    "card_columns": {"fr": "Colonnes :", "en": "Columns:"},
    "card_category": {"fr": "Catégorie :", "en": "Category:"},
    "card_recommendation": {"fr": "Recommandation :", "en": "Recommendation:"},
    "card_no_reco": {"fr": "Aucune recommandation automatique.", "en": "No automatic recommendation."},
    "card_na": {"fr": "n/a", "en": "n/a"},
    # Narrative connectors
    "nar_intro": {
        "fr": "La comparaison entre {a} et {b} porte sur {ra} lignes contre {rb} lignes. {n} changements ont été détectés.",
        "en": "The comparison between {a} and {b} covers {ra} rows against {rb} rows. {n} changes were detected.",
    },
    "nar_none": {
        "fr": "Aucun changement significatif n'a été détecté entre les deux versions du dataset sur les axes analysés.",
        "en": "No significant change was detected between the two dataset versions on the analyzed axes.",
    },
    "nar_regarding": {"fr": "Concernant {label} :", "en": "Regarding {label}:"},
    "nar_reco_title": {"fr": "Recommandations prioritaires :", "en": "Priority recommendations:"},
    # Category labels
    "cat_schema": {"fr": "schéma", "en": "schema"},
    "cat_volume": {"fr": "volume", "en": "volume"},
    "cat_nulls": {"fr": "valeurs manquantes", "en": "missing values"},
    "cat_distribution": {"fr": "distributions", "en": "distributions"},
    "cat_outliers": {"fr": "valeurs extrêmes", "en": "extreme values"},
    "cat_duplicates": {"fr": "doublons", "en": "duplicates"},
    "cat_quality": {"fr": "qualité générale", "en": "overall quality"},
    "cat_business_rule": {"fr": "règles métier", "en": "business rules"},
}


def _session_lang() -> str:
    if _st is None:
        return DEFAULT_LANG
    try:
        value = _st.session_state.get("lang", DEFAULT_LANG)
    except Exception:
        value = DEFAULT_LANG
    return value if value in AVAILABLE_LANGS else DEFAULT_LANG


def get_lang() -> str:
    return _session_lang()


def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    use_lang = lang if lang in AVAILABLE_LANGS else _session_lang()
    entry = TRANSLATIONS.get(key)
    if entry is None:
        text = key
    else:
        text = entry.get(use_lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def category_label(category: str, lang: Optional[str] = None) -> str:
    return t(f"cat_{category}", lang=lang)


# ---------------------------------------------------------------------------
# Narration templates (FR / EN). Each returns (title, narrative, recommendation).
# ---------------------------------------------------------------------------
def _pct(value, lang):
    if value is None:
        return "n/a"
    return f"{value:.1%}" if lang == "fr" else f"{value:.1%}"


def _fnum(value, digits=2):
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def nar_volume(lang, rows_b, rows_c, delta_rows, delta_pct):
    if lang == "fr":
        direction = "augmenté" if delta_rows > 0 else "diminué" if delta_rows < 0 else "resté stable"
        narrative = (
            f"Le volume de lignes est {direction} de {abs(delta_rows):,} lignes, "
            f"passant de {rows_b:,} à {rows_c:,} ({_pct(delta_pct, lang)})."
        ).replace(",", " ")
        title = "Évolution du volume de lignes"
        reco = (
            "Vérifier si le changement de volume est attendu "
            "(nouvelle période, nouveau périmètre, filtrage, duplication)."
        )
    else:
        direction = "increased" if delta_rows > 0 else "decreased" if delta_rows < 0 else "stayed stable"
        narrative = (
            f"The row volume {direction} by {abs(delta_rows):,} rows, "
            f"going from {rows_b:,} to {rows_c:,} ({_pct(delta_pct, lang)})."
        )
        title = "Row volume change"
        reco = "Check whether the volume change is expected (new period, new scope, filtering, duplication)."
    return title, narrative, reco


def nar_schema_added(lang, column):
    if lang == "fr":
        return (
            f"Colonne ajoutée : {column}",
            f"La colonne {column} est présente uniquement dans la seconde version.",
            "Vérifier si cette colonne doit être intégrée aux modèles aval, aux rapports ou aux tests de qualité.",
        )
    return (
        f"Added column: {column}",
        f"The column {column} is present only in the second version.",
        "Check whether this column should be integrated into downstream models, reports or quality tests.",
    )


def nar_schema_removed(lang, column):
    if lang == "fr":
        return (
            f"Colonne supprimée : {column}",
            f"La colonne {column} était présente dans la première version mais absente de la seconde.",
            "Confirmer que la suppression est intentionnelle et qu'aucune dépendance aval ne casse.",
        )
    return (
        f"Removed column: {column}",
        f"The column {column} was present in the first version but missing in the second.",
        "Confirm the removal is intentional and that no downstream dependency breaks.",
    )


def nar_schema_renamed(lang, b, c, confidence):
    if lang == "fr":
        return (
            f"Colonne possiblement renommée : {b} -> {c}",
            f"La colonne {b} semble avoir été renommée en {c}. Le score de correspondance est de {confidence:.2f}.",
            "Valider le renommage avec le producteur du dataset et mettre à jour les requêtes ou pipelines dépendants.",
        )
    return (
        f"Possible renamed column: {b} -> {c}",
        f"The column {b} seems to have been renamed to {c}. The match score is {confidence:.2f}.",
        "Validate the rename with the dataset producer and update dependent queries or pipelines.",
    )


def nar_schema_type(lang, b, c, dtype_b, dtype_c, interpretation):
    if lang == "fr":
        return (
            f"Type modifié sur {c}",
            (
                f"La colonne {b} avait le type {dtype_b} dans la première version, alors que {c} "
                f"a le type {dtype_c} dans la seconde. Il s'agit d'un {interpretation}."
            ),
            "Vérifier les conversions implicites, notamment sur les identifiants, montants, dates et téléphones.",
        )
    return (
        f"Modified type on {c}",
        (
            f"The column {b} had type {dtype_b} in the first version, while {c} "
            f"has type {dtype_c} in the second. This is a {interpretation}."
        ),
        "Check implicit conversions, especially on identifiers, amounts, dates and phones.",
    )


def nar_schema_no_common(lang):
    if lang == "fr":
        return (
            "Aucune colonne commune détectée",
            (
                "Les deux datasets ne partagent aucune colonne après normalisation des noms. "
                "La comparaison de contenu est donc limitée au schéma et au volume."
            ),
            "Vérifier que les deux fichiers correspondent au même périmètre métier ou déclarer manuellement des correspondances de colonnes.",
        )
    return (
        "No common column detected",
        (
            "The two datasets share no column after name normalization. "
            "Content comparison is therefore limited to schema and volume."
        ),
        "Verify both files cover the same business scope or declare column mappings manually.",
    )


def nar_nulls(lang, column, rate_b, rate_c, delta, increasing):
    if lang == "fr":
        if increasing:
            title = f"Augmentation des valeurs manquantes sur {column}"
            narrative = (
                f"La colonne {column} a vu son taux de valeurs manquantes passer de "
                f"{_pct(rate_b, lang)} à {_pct(rate_c, lang)}, soit une hausse de {_pct(delta, lang)}."
            )
            reco = "Identifier la source d'alimentation de cette colonne et vérifier si un champ obligatoire est devenu optionnel."
        else:
            title = f"Diminution des valeurs manquantes sur {column}"
            narrative = (
                f"La colonne {column} a vu son taux de valeurs manquantes passer de "
                f"{_pct(rate_b, lang)} à {_pct(rate_c, lang)}, soit une amélioration de {_pct(abs(delta), lang)}."
            )
            reco = "Cette amélioration est positive, mais vérifier qu'elle ne résulte pas d'un remplacement par des valeurs par défaut non significatives."
    else:
        if increasing:
            title = f"Increase in missing values on {column}"
            narrative = (
                f"The column {column} saw its missing-value rate go from "
                f"{_pct(rate_b, lang)} to {_pct(rate_c, lang)}, an increase of {_pct(delta, lang)}."
            )
            reco = "Identify the source feeding this column and check whether a mandatory field became optional."
        else:
            title = f"Decrease in missing values on {column}"
            narrative = (
                f"The column {column} saw its missing-value rate go from "
                f"{_pct(rate_b, lang)} to {_pct(rate_c, lang)}, an improvement of {_pct(abs(delta), lang)}."
            )
            reco = "This improvement is positive, but check it does not result from replacement by non-meaningful default values."
    return title, narrative, reco


def nar_dist_numeric(lang, column, psi, med_b, med_c, mean_b, mean_c, strength):
    if lang == "fr":
        return (
            f"Changement de distribution numérique sur {column}",
            (
                f"La distribution numérique de {column} a changé. Le PSI est de {psi:.3f}, ce qui indique un déplacement {strength}. "
                f"La médiane passe de {_fnum(med_b)} à {_fnum(med_c)}. La moyenne passe de {_fnum(mean_b)} à {_fnum(mean_c)}."
            ),
            "Analyser si ce déplacement correspond à une évolution métier réelle ou à un problème d'extraction, de filtre ou d'encodage.",
        )
    return (
        f"Numeric distribution change on {column}",
        (
            f"The numeric distribution of {column} changed. The PSI is {psi:.3f}, indicating a {strength} shift. "
            f"The median moves from {_fnum(med_b)} to {_fnum(med_c)}. The mean moves from {_fnum(mean_b)} to {_fnum(mean_c)}."
        ),
        "Assess whether this shift reflects a real business evolution or an extraction, filter or encoding issue.",
    )


def nar_dist_categorical(lang, column, parts):
    joined = " ".join(parts)
    if lang == "fr":
        return (
            f"Changement de distribution catégorielle sur {column}",
            f"La distribution catégorielle de {column} a évolué. {joined}",
            "Vérifier si les nouvelles catégories sont autorisées par le référentiel métier et si les mappings aval les prennent en charge.",
        )
    return (
        f"Categorical distribution change on {column}",
        f"The categorical distribution of {column} evolved. {joined}",
        "Check whether new categories are allowed by the business reference and whether downstream mappings support them.",
    )


def nar_outliers(lang, column, count, lower, upper, rate_b, rate_c):
    if lang == "fr":
        return (
            f"Apparition de valeurs extrêmes sur {column}",
            (
                f"La colonne {column} contient {count} valeurs hors des bornes observées dans la première version "
                f"[{_fnum(lower)}, {_fnum(upper)}]. Le taux de valeurs extrêmes passe de {_pct(rate_b, lang)} à {_pct(rate_c, lang)}."
            ),
            "Contrôler les valeurs extrêmes nouvelles et déterminer si elles résultent d'une erreur de saisie, d'un problème d'unité ou d'une réelle évolution métier.",
        )
    return (
        f"Emergence of extreme values on {column}",
        (
            f"The column {column} contains {count} values outside the bounds observed in the first version "
            f"[{_fnum(lower)}, {_fnum(upper)}]. The extreme-value rate moves from {_pct(rate_b, lang)} to {_pct(rate_c, lang)}."
        ),
        "Control the new extreme values and determine whether they come from a typo, a unit issue or a real business evolution.",
    )


def nar_rule_age(lang, column, invalid_c, invalid_b, new_invalid):
    if lang == "fr":
        return (
            f"Valeurs d'âge invalides sur {column}",
            (
                f"La colonne {column} contient {invalid_c} valeurs hors plage [0, 120], contre {invalid_b} dans la première version. "
                f"Cela représente {new_invalid} valeurs invalides supplémentaires."
            ),
            "Ajouter une contrainte de plage sur l'âge et tracer la source des valeurs supérieures à 120 ou négatives.",
        )
    return (
        f"Invalid age values on {column}",
        (
            f"The column {column} contains {invalid_c} values outside the [0, 120] range, against {invalid_b} in the first version. "
            f"That is {new_invalid} additional invalid values."
        ),
        "Add a range constraint on age and trace the source of values above 120 or negative.",
    )


def nar_rule_email(lang, column, invalid_c, rate_c):
    if lang == "fr":
        return (
            f"Adresses email invalides sur {column}",
            f"La colonne {column} contient {invalid_c} valeurs sans symbole @, soit {_pct(rate_c, lang)} des emails non nuls.",
            "Mettre en place une validation de format email à l'ingestion et contrôler les sources de saisie manuelle.",
        )
    return (
        f"Invalid email addresses on {column}",
        f"The column {column} contains {invalid_c} values without an @ symbol, i.e. {_pct(rate_c, lang)} of non-null emails.",
        "Set up email format validation at ingestion and control manual entry sources.",
    )


def nar_rule_negative(lang, column, neg_c, neg_b):
    if lang == "fr":
        return (
            f"Valeurs négatives sur {column}",
            f"La colonne {column} contient {neg_c} valeurs négatives, contre {neg_b} dans la première version.",
            "Vérifier si les valeurs négatives sont autorisées (avoirs, remboursements) ou si elles indiquent une anomalie.",
        )
    return (
        f"Negative values on {column}",
        f"The column {column} contains {neg_c} negative values, against {neg_b} in the first version.",
        "Check whether negative values are allowed (credits, refunds) or indicate an anomaly.",
    )


def nar_dup_rows(lang, rate_b, rate_c, increasing):
    if lang == "fr":
        direction = "augmenté" if increasing else "diminué"
        return (
            "Évolution des doublons de lignes complètes",
            f"Le taux de doublons de lignes complètes a {direction}, passant de {_pct(rate_b, lang)} à {_pct(rate_c, lang)}.",
            "Vérifier les étapes d'append, les jointures et les exports partiels pouvant générer des lignes dupliquées.",
        )
    direction = "increased" if increasing else "decreased"
    return (
        "Full-row duplicate evolution",
        f"The full-row duplicate rate {direction}, going from {_pct(rate_b, lang)} to {_pct(rate_c, lang)}.",
        "Check append steps, joins and partial exports that may generate duplicated rows.",
    )


def nar_dup_key(lang, column, dup_b, dup_c, rate_b, rate_c):
    if lang == "fr":
        return (
            f"Doublons sur la clé {column}",
            (
                f"Le nombre de lignes dupliquées sur {column} est passé de {dup_b} à {dup_c}. "
                f"Le taux de doublons passe de {_pct(rate_b, lang)} à {_pct(rate_c, lang)}."
            ),
            "Contrôler l'unicité de cette clé avant agrégation, jointure ou chargement dans un data warehouse.",
        )
    return (
        f"Duplicates on key {column}",
        (
            f"The number of duplicated rows on {column} went from {dup_b} to {dup_c}. "
            f"The duplicate rate moves from {_pct(rate_b, lang)} to {_pct(rate_c, lang)}."
        ),
        "Control the uniqueness of this key before aggregation, join or loading into a data warehouse.",
    )


def nar_quality_all_null(lang, column, rate_c):
    if lang == "fr":
        return (
            f"Colonne devenue entièrement nulle : {column}",
            f"La colonne {column} est désormais quasiment entièrement nulle, avec un taux de valeurs manquantes de {_pct(rate_c, lang)}.",
            "Bloquer temporairement l'usage de cette colonne et investiguer l'étape d'extraction responsable.",
        )
    return (
        f"Column became entirely null: {column}",
        f"The column {column} is now almost entirely null, with a missing-value rate of {_pct(rate_c, lang)}.",
        "Temporarily block the use of this column and investigate the responsible extraction step.",
    )


def nar_quality_constant(lang, column, unique_b):
    if lang == "fr":
        return (
            f"Colonne devenue constante : {column}",
            f"La colonne {column} ne contient plus qu'une valeur unique principale, contre {unique_b} valeurs uniques auparavant.",
            "Vérifier si un filtre, une jointure ou une valeur par défaut a écrasé la variabilité attendue.",
        )
    return (
        f"Column became constant: {column}",
        f"The column {column} now holds a single main unique value, against {unique_b} unique values before.",
        "Check whether a filter, join or default value overwrote the expected variability.",
    )


def nar_quality_cardinality(lang, column, unique_b, unique_c):
    if lang == "fr":
        return (
            f"Forte baisse de cardinalité sur {column}",
            f"Le nombre de valeurs uniques de {column} est passé de {unique_b} à {unique_c}.",
            "Contrôler si cette réduction est liée à un filtrage métier ou à une perte de données.",
        )
    return (
        f"Strong cardinality drop on {column}",
        f"The number of unique values of {column} went from {unique_b} to {unique_c}.",
        "Check whether this reduction is due to business filtering or data loss.",
    )
