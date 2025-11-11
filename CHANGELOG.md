# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-11-11

### Added
- `etl_scripts/backfill_dv.py` CSV-first reconciliation script with RMS/CAD backfills, quality flags, and validation-report/metrics outputs.
- Edge-case regression tests in `tests/test_backfill_functions_edge_cases.py` covering missing inputs, malformed officers, time parsing, and duplicate handling.
- Integration/benchmark suite at `tests/integration/test_suite.py` that executes the backfill pipeline on synthetic data and records timing via `pytest-benchmark` (with graceful fallback).

### Changed
- Updated DV ETL helpers (`transform_dv_data.py`, `map_dv_to_rms_locations.py`, `verify_transformations.py`, utility scripts) to prefer CSV inputs using the `pyarrow` engine, falling back to legacy Excel sources when needed.
- Adjusted RMS mapping workflow to prioritize the headered CSV exported under `raw_data/xlsx/output/`, ensuring case-number joins succeed when Excel sheets are unavailable.
- Refined shared ETL loader logic to avoid unsupported `low_memory` flags with the `pyarrow` engine.
- Enriched DV transformations with RMS primary / CAD fallback backfilling for `OffenseDate`, `DayOfWeek`, and `Time`; removed redundant municipality columns; formatted `Time`/`TotalTime` as `HH:MM:SS`; and normalised death indicator fields to booleans.

### Fixed
- Confirmed `python etl.py transform`, `map`, and `verify` run end-to-end against the CSV pipeline after installing the `rich` dependency.

### Documentation
- Refreshed `README.md` and `PROJECT_SUMMARY.md` with the DV backfill workflow, validation artifacts, and updated testing guidance.
- Refreshed `docs/handoff_next_steps.md` to capture the CSV-first workflow expectations and RMS source location guidance.

## [1.3.0] - 2025-11-11

### Added
- `pyproject.toml` with pinned runtime dependencies, Ruff/Mypy/Pytest config, and packaging metadata.
- `Makefile` targets: `setup`, `qa`, `test`, `fmt`, `export`, `etl`, `profile`, `map`, `verify`, `report`.
- `etl.py` Click CLI wrapping export, profile, transform, map, and verify workflows.
- Pytest scaffolding in `tests/` with lightweight fixtures under `tests/fixtures/mini/`.
- GitHub Actions workflow `.github/workflows/ci.yml` running Ruff, Mypy, and Pytest on Windows.
- Documentation: `docs/data_dictionary.md`, `docs/pii_policy.md`, CSV lookup tables in `docs/mappings/`, and source asset README.

### Changed
- Consolidated Python utilities under `etl_scripts/` package with importable `main()` functions.
- `export_excel_sheets_to_csv.py` now supports programmatic execution for the CLI while retaining CLI argument parsing.
- `fix_dv_headers.py` and `transform_dv_data.py` load yes/no, race, and ethnicity mappings from CSV; boolean normalization respects configurable vocab.
- `transform_dv_data.py` localises datetime parsing to `America/New_York` and accepts configurable input/output paths.
- `map_dv_to_rms_locations.py` consumes join configuration from `docs/mappings/location_join_keys.csv`.
- `verify_transformations.py` produces a JSON verification report with record counts and null rates under `logs/`.
- `.gitignore` updated to keep virtual environments, caches, and large data directories outside version control while whitelisting docs/tests CSVs.
- Large reference documents relocated to `docs/source/`.

### Documentation
- Updated `README.md` with Makefile workflow, CLI usage, QA pipeline, and documentation inventory.
- Updated `PROJECT_SUMMARY.md` with toolchain overview, new docs, and refreshed command guidance.
- Refreshed `NEXT_STEPS.md` references to archived documentation paths.

## [1.2.0] - 2025-11-01

### Added
- **DV Data Transformation Pipeline**
  - `fix_dv_headers.py`: Script to fix column headers and convert boolean values
  - `transform_dv_data.py`: Advanced data transformation and consolidation script
  - `map_dv_to_rms_locations.py`: Maps Case Numbers to RMS locations for GIS mapping
  - `verify_transformations.py`: Verification script for data transformations
  - `examine_dv_structure.py`: Utility script to examine DV file structure
  - `check_dv_columns.py`: Utility to check column patterns

### Changed
- **Column Header Fixes**
  - `Case #` → `CaseNumber` (removed # symbol)
  - `gMunicipality` → `Municipality` (removed 'g' prefix)
  - `gMunicipalityCode` → `MunicipalityCode` (removed 'g' prefix)
  - `gMunicipalityPhone` → `MunicipalityPhone` (removed 'g' prefix)
  - `Reviewed By` → `ReviewedBy` (PascalCase conversion)
  - Column `c` → `OffenseDate` (proper naming)

- **Data Type Improvements**
  - `OffenseDate`: Converted to date-only type (no time component)
  - `Time`: Set to `timedelta64` (time/duration type)
  - `TotalTime`: Set to `timedelta64` (duration type)
  - `VictimAge`: Maintained as numeric (`int64`)

- **Column Consolidations**
  - **VictimRace**: Consolidated 6 boolean columns into single categorical column
    - Codes: W (White), A (Asian), B (Black), P (Pacific Islander), I (American Indian), U (Unknown)
    - Reduced from 6 columns to 1 column
  - **VictimEthnicity**: Consolidated 2 boolean columns into single categorical column
    - Codes: H (Hispanic), NH (Non-Hispanic)
    - Reduced from 2 columns to 1 column
  - **DayOfWeek**: Consolidated 7 boolean columns into single categorical column
    - Codes: Sun, Mon, Tue, Wed, Thu, Fri, Sat
    - Reduced from 7 columns to 1 column

- **Column Renaming**
  - `VictimSexF` → `FemaleVictim`
  - `VictimSexM` → `MaleVictim`

- **Boolean Value Conversion**
  - All 'X' and 'O' values converted to boolean `True`
  - Empty/'0' values converted to boolean `False`
  - Applied to indicator columns (days, alcohol, drugs, race flags, etc.)

### New Features
- **GIS Integration**
  - ArcGIS Pro script generation (`arcgis_map_dv_incidents.py`)
  - Automatic Case Number mapping to RMS locations
  - Location data extraction (FullAddress) for mapping
  - Support for geocoding addresses in ArcGIS Pro

- **Data Quality Improvements**
  - Column reduction: 268 → 256 columns (12 columns removed through consolidation)
  - Proper data type enforcement
  - MunicipalityCode constant value detection

### Documentation
- Added `DV_HEADER_FIXES_SUMMARY.md`: Summary of header fixes
- Added `TRANSFORMATION_SUMMARY.md`: Detailed transformation documentation
- Updated `README.md`: Added transformation scripts section
- Updated `PROJECT_SUMMARY.md`: Added transformation features

### Files
- `processed_data/_2023_2025_10_31_dv_fixed.xlsx`: Fixed headers and booleans
- `processed_data/_2023_2025_10_31_dv_fixed_transformed.xlsx`: Fully transformed data
- `processed_data/dv_with_locations.xlsx`: Merged DV + RMS data with locations
- `processed_data/dv_with_locations.csv`: CSV version for ArcGIS import
- `processed_data/arcgis_map_dv_incidents.py`: ArcGIS Pro mapping script

## [1.1.0] - 2025-10-31

### Added
- Initial project setup
- AI data analyzer script
- ETL pipeline framework
- Git automation scripts
- Quick analysis scripts
- Documentation (README, QUICKSTART, SETUP_GIT)

### Features
- Excel to CSV conversion
- AI analysis generation
- Data quality reporting
- Demographic analysis framework
- GitHub integration

## [1.0.0] - 2025-10-31

### Added
- Initial project structure
- Basic ETL framework
- Data analysis tools

