# NJ CAD/RMS and Domestic Violence Data Analysis Project

## Project Overview

This repository contains an end-to-end workflow for analyzing CAD/RMS and Domestic Violence data reported to the State of New Jersey between January 2023 and October 31, 2025. It includes automation for exporting Excel files, AI-assisted data profiling, ETL utilities, and documentation to support data quality reviews, demographic insights, and GIS-ready outputs.

## Repository Layout

```text
dv_doj/
├── raw_data/
│   ├── xlsx/                         # Source Excel workbooks
│   └── csv/                          # Optional CSV inputs
├── output/                           # Auto-generated CSV exports
├── analysis/
│   └── ai_responses/                 # AI-generated analysis reports
├── etl_scripts/                      # All Python utilities and pipelines
│   ├── ai_data_analyzer.py           # Main AI data profiler
│   ├── base_etl.py                   # ETL framework and helpers
│   ├── export_excel_sheets_to_csv.py # Excel ➜ CSV converter
│   ├── fix_dv_headers.py             # DV header normalization
│   ├── transform_dv_data.py          # DV data consolidation
│   ├── map_dv_to_rms_locations.py    # DV ↔ RMS location mapping
│   ├── verify_transformations.py     # Transformation QA checks
│   ├── check_dv_columns.py           # Column diagnostics
│   ├── examine_dv_structure.py       # Structural inspection helper
│   ├── git_automation.py             # Git/GitHub automation utilities
│   └── quick_analysis.py             # Lightweight inspection script
├── processed_data/                   # Cleaned & transformed data
├── logs/                             # Pipeline and analysis logs
├── notebooks/                        # Jupyter exploration notebooks
├── data/                             # Additional reference data
├── docs/
│   └── archive/                      # Historical docs, guides, requirements
├── PROJECT_SUMMARY.md                # Project-wide summary
└── README.md                         # You are here
```

## Quick Start

1. **Install dependencies**

   ```bash
   make setup
   ```

   This creates `.venv`, installs the project in editable mode, and adds QA tooling (`ruff`, `mypy`, `pytest`).  
   Prefer `pip install -e .` if `make` is unavailable.

2. **Convert Excel workbooks to CSV (optional)**

   ```bash
   python etl.py export --src raw_data/xlsx --out output
   ```

   CSV exports are written to `output/` and logged in `output/conversion_summary.json`.

3. **Profile the data with AI**

   ```bash
   python etl.py profile --src output --out analysis/ai_responses
   ```

   The script inspects every Excel/CSV file in `raw_data/` and `output/`, producing detailed JSON reports in `analysis/ai_responses/`.

4. **Build or run ETL pipelines**

   ```bash
   python etl.py transform --src processed_data --out processed_data
   ```

   The CLI orchestrates the header fix, data transformation, mapping, and verification helpers.

5. **Explore results**
   - Review AI outputs in `analysis/ai_responses/`
   - Inspect cleaned files in `processed_data/`
   - Use notebooks in `notebooks/` for ad hoc analysis

## Tooling Overview

- **Environment** — `pyproject.toml` pins runtime dependencies; `make setup` provisions a local `.venv`.
- **CLI** — `python etl.py` exposes `export`, `profile`, `transform`, `map`, and `verify` workflows (implemented with Click).
- **Quality Gates** — `make qa` runs `ruff`, `mypy`, and `pytest`; `make fmt` auto-formats imports and style issues.
- **Tests** — Lightweight fixtures in `tests/fixtures/mini/` keep regressions in check (`make test`).
- **CI** — `.github/workflows/ci.yml` executes the same lint/type/test pipeline on Windows runners for every push and PR.

### CLI Commands

Run the commands from the repository root using the project virtual environment (`.venv\Scripts\python` on Windows):

| Command | Purpose | Example |
| --- | --- | --- |
| `export` | Convert Excel workbooks to CSV. | `python etl.py export --src raw_data/xlsx --out output` |
| `profile` | Generate AI-driven profiling reports. | `python etl.py profile --src output --out analysis/ai_responses` |
| `transform` | Apply DV-specific transformations. | `python etl.py transform --src processed_data --out processed_data` |
| `map` | Join DV and RMS data for mapping. | `python etl.py map --src processed_data --out processed_data` |
| `verify` | Emit a JSON verification report. | `python etl.py verify --src processed_data --out logs` |

## Data Snapshot

- `_2023_2025_10_31_dv.xlsx` (245 KB) – summary DV reporting
- `_2023_2025_10_31_dv_cad.xlsx` (19 MB) – CAD incidents
- `_2023_2025_10_31_dv_rms.xlsx` (17 MB) – RMS records
- Time span: January 2023 through October 31, 2025

Converted CSV counterparts are stored in `output/`. All sensitive data should remain within raw/processed directories and is excluded from version control.

## Working With the Data

1. Place raw Excel or CSV files into `raw_data/xlsx/` or `raw_data/csv/`.
2. Run `ai_data_analyzer.py` to generate:
   - Column inventories with samples
   - Random record spot checks
   - Data-quality metrics (nulls, outliers, suspicious values)
   - AI prompts for deeper exploration
3. Use ETL scripts to clean and standardize:
   - `etl_scripts/fix_dv_headers.py` – normalize column names and booleans
   - `etl_scripts/transform_dv_data.py` – consolidate race, ethnicity, time fields, and more
   - `etl_scripts/map_dv_to_rms_locations.py` – join DV cases to RMS locations for GIS
   - `etl_scripts/verify_transformations.py` – confirm transformations succeeded
4. Load cleaned data into visualization tools, GIS, or downstream analytics.

## Tools & Automation

- **`etl_scripts/ai_data_analyzer.py`**  
  Automates profiling of every source file and saves JSON reports with human-readable findings and AI-ready prompts.

- **`etl_scripts/base_etl.py`**  
  Provides the `BaseETL` framework plus demographic helpers for reusable Extract-Transform-Load pipelines.

- **`etl_scripts/export_excel_sheets_to_csv.py`**  
  Batch converts each sheet in supported Excel workbooks to CSV with progress bars, error handling, and execution logs.

- **`etl_scripts/git_automation.py`**  
  Wraps Git commands to initialize repositories, commit/push changes, create tags, and sync with GitHub.

## Outputs & Logging

- `analysis/ai_responses/`  
  `{filename}_analysis_{timestamp}.json` and `{filename}_prompts_{timestamp}.json` contain profiling results and follow-up prompt templates.

- `processed_data/`  
  Stores cleaned datasets, such as `_2023_2025_10_31_dv_fixed_transformed.xlsx`, ready for reporting or GIS use.

- `logs/analysis.log`  
  Captures ETL and analyzer execution details for troubleshooting.

## Git & GitHub Workflow

Manual workflow:

```bash
git add .
git commit -m "Describe your changes"
git push origin main
```

Automation (optional):

```bash
python etl_scripts/git_automation.py --status
python etl_scripts/git_automation.py --commit-push "Your commit message"
```

The remote repository is hosted at `https://github.com/racmac57/dv_doj.git`. Make sure your Git credentials are configured (GitHub token or HTTPS credentials) before pushing changes.

## Additional Documentation

- `PROJECT_SUMMARY.md` – high-level overview of objectives and accomplishments
- `docs/archive/START_HERE.md` – orientation guide and project history
- `docs/archive/ANALYSIS_SUMMARY.md` – synthesized findings from prior data reviews
- `docs/archive/QUICKSTART.md` – concise walkthrough for new users
- `docs/archive/SETUP_GIT.md` – step-by-step instructions for configuring GitHub access
- `docs/archive/TRANSFORMATION_SUMMARY.md` – detailed transformation notes
- `docs/data_dictionary.md` – canonical field definitions, types, and examples
- `docs/pii_policy.md` – expectations for handling sensitive information
- `docs/mappings/` – CSV lookup tables referenced by the ETL pipeline

The archived documents capture historical context, prior analysis, and setup guides.

## Need Help?

1. Review `logs/analysis.log` for execution issues.
2. Check AI reports in `analysis/ai_responses/` for data anomalies.
3. Consult the documentation listed above for deeper dives.

Happy analyzing!
