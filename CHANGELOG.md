# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

