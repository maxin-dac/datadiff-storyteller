# 📁 DataDiff Storyteller

French version: [README.fr.md](README.fr.md)

Compare two versions of a dataset and explain what changed in a clear, business-readable narrative. Instead of returning only a technical diff, the tool produces structured findings, severity scoring, visual diagnostics, and an exportable report.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?style=flat&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-636AFD?style=flat&logo=plotly&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-experimental-FFC000?style=flat&logo=duckdb&logoColor=black)
![Bilingual](https://img.shields.io/badge/Bilingual-FR_%7C_EN-008080?style=flat&logo=translate&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat&logo=opensourceinitiative&logoColor=white)

Table of contents

- [Purpose of the application](#purpose-of-the-application)
- [What the tool analyzes](#what-the-tool-analyzes)
- [Three reading modes](#three-reading-modes)
- [Input data](#input-data)
- [Methodological principles](#methodological-principles)
- [Assumed limitations](#assumed-limitations)
- [Local installation](#local-installation)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

## Purpose of the application

DataDiff Storyteller is designed for data teams that receive two versions of the same extract and need to understand quickly what changed, what is risky, and what should be investigated first.

Typical use cases:

- comparing a customer file from one year to the next;
- validating an export before loading it into a data warehouse;
- reviewing a migration between two pipeline versions;
- detecting quality degradation after an upstream change;
- producing a readable change report for business stakeholders.

The application does not only answer "what is different?". It answers "what does this difference mean?".

Example of the intended output style:

    The phone_number column lost reliability: missing values moved from 12% to 30%.
    The age column now contains values above 120, probably caused by entry errors or encoding issues.
    The subscription_tier distribution introduced a new premium category representing 6% of customers.

## What the tool analyzes

| Dimension | What it detects |
| --- | --- |
| Schema | Added columns, removed columns, probable renames, type changes |
| Volume | Row count evolution, absolute and relative variation |
| Missing values | Null rate increases or decreases per column |
| Distributions | Numeric shifts using PSI and descriptive statistics, categorical changes, new or disappeared categories |
| Outliers | New extreme values compared with baseline bounds |
| Duplicates | Full-row duplicates and duplicate candidates on key-like columns |
| Quality | Columns becoming all-null, constant, or losing cardinality |
| Business rules | Simple documented rules for age, email format, and negative amounts when column names match known keywords |

Each detected change is stored as a structured finding with:

- a stable identifier;
- a category;
- a severity level;
- a title;
- a narrative sentence;
- affected columns;
- technical metrics;
- an optional recommendation;
- optional evidence samples.

## Three reading modes

### Overview

The overview page provides the executive summary:

- health score;
- critical, high, and medium finding counts;
- row volume evolution;
- column count evolution;
- missing-rate comparison;
- top prioritized findings.

This mode is intended for quick triage.

### Diagnostic pages

The diagnostic pages split the analysis into focused views:

- Schema: column mapping, additions, removals, renames, type changes;
- Quality: missing values, duplicates, all-null columns, constant columns;
- Distributions: numeric and categorical comparisons with Plotly charts;
- Anomalies: outliers and business-rule violations with sample values.

This mode is intended for data engineers and analysts who need to investigate root causes.

### Report export

The report page generates a narrative summary and exports the full analysis in three formats:

- Markdown for documentation and pull requests;
- JSON for automation and CI/CD integration;
- HTML for business sharing.

This mode is intended for formal restitution.

## Input data

The MVP accepts delimited text files, mainly CSV.

Supported options in the import page:

- automatic or manual separator detection;
- comma, semicolon, tab, pipe;
- automatic or manual encoding;
- UTF-8, UTF-8 with BOM, Latin-1, CP1252;
- maximum row limit to protect memory.

Data handling in the MVP:

- uploaded files are parsed in application memory;
- analysis results are stored in the Streamlit session state;
- no permanent database storage is implemented;
- no external LLM call is required for the deterministic narrative engine.

## Methodological principles

The application follows strict traceability rules:

- numerical facts are computed first;
- narrative sentences are generated from structured findings;
- no number is invented by the reporting layer;
- missing values are not imputed;
- every signal mentions the affected column and the metric that triggered it;
- every recommendation is tied to a detected change;
- statistical checks are generic and do not depend on a demo dataset;
- business-rule checks are documented and currently keyword-based.

The default narration engine is deterministic. A future LLM layer can reformulate findings, but it should never be allowed to generate facts without constrained input.

## Assumed limitations

These limitations are assumed in the current MVP:

- the public input format is CSV;
- Parquet, SQL tables, and dbt integration are roadmap items;
- business rules currently rely on column-name keywords such as age, email, amount, value, price, revenue, montant, or lifetime;
- rename detection is heuristic and exposes a confidence score;
- very large files may exceed memory limits even with row sampling options;
- DuckDB profiling is available as an experimental path, while the detailed diff engine still relies on pandas;
- statistical thresholds are implemented in code but not yet fully exposed in the UI;
- the tool explains changes, it does not repair data automatically.

## Local installation

Clone the repository:

    git clone https://github.com/maxin-dac/datadiff-storyteller.git
    cd datadiff-storyteller

Create a virtual environment:

    python -m venv .venv

Activate it.

On Linux or macOS:

    source .venv/bin/activate

On Windows cmd:

    .venv\Scripts\activate.bat

On Windows PowerShell:

    .venv\Scripts\Activate.ps1

If PowerShell blocks script execution, either allow current-user scripts:

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

or bypass activation and run the environment Python directly:

    .venv\Scripts\python.exe -m streamlit run Home.py

Install dependencies:

    pip install -r requirements.txt

Start the application:

    streamlit run Home.py

Open:

    http://localhost:8501

## Live Demo

Try DataDiff Storyteller online:

<p align="left">
  <a href="https://datadiff.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Open_Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Open Streamlit Cloud" />
  </a>

  <a href="https://datadiff.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/Open_Render-0A2C3A?style=for-the-badge&logo=render&logoColor=white" alt="Open Render" />
  </a>
</p>

Public demos may cold-start after inactivity. If a link is slow, reload once.

## Project structure

    datadiff-storyteller/
    ├── Home.py
    ├── pages/
    │   ├── 0_Accueil.py
    │   ├── 1_Upload.py
    │   ├── 2_Overview.py
    │   ├── 3_Schema.py
    │   ├── 4_Quality.py
    │   ├── 5_Distributions.py
    │   ├── 6_Anomalies.py
    │   └── 7_Rapport.py
    ├── core/
    │   ├── align.py
    │   ├── analysis.py
    │   ├── diff_engine.py
    │   ├── duckdb_profile.py
    │   ├── findings.py
    │   ├── i18n.py
    │   ├── ingest.py
    │   ├── narrative.py
    │   ├── profile.py
    │   ├── report_builder.py
    │   └── scoring.py
    ├── models/
    │   └── schemas.py
    ├── components/
    │   ├── charts.py
    │   ├── icons.py
    │   └── layout.py
    ├── assets/
    │   ├── icons/
    │   ├── logo.svg
    │   ├── report.css
    │   └── styles.css
    ├── templates/
    │   └── report.html
    ├── scripts/
    │   ├── bump_version.py
    │   └── export_icons.py
    ├── data/
    │   └── .gitkeep
    ├── .github/
    │   └── workflows/
    │       └── version.yml
    ├── .streamlit/
    │   └── config.toml
    ├── .gitignore
    ├── CHANGELOG.md
    ├── Dockerfile
    ├── LICENSE
    ├── README.md
    ├── README.fr.md
    ├── render.yaml
    ├── requirements.txt
    └── VERSION

Local test files and local demo CSV files are intentionally excluded from the public first release.

## Roadmap

High-value next steps:

- manual column mapping UI;
- configurable business rules in YAML or JSON;
- Parquet support;
- direct SQL table comparison;
- CLI mode for CI pipelines;
- historical drift tracking;
- automatic generation of recommended data-quality tests;
- optional local LLM reformulation constrained to structured findings.

## Author

Maxime NDACLEU - Data Analyst and BI

![GitHub](https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white)
![LinkedIn](https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white)

## License

MIT. See the LICENSE file.
