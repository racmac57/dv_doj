# Data Dictionary

This document captures the primary fields used throughout the domestic violence ETL workflows. Values are representative samples drawn from anonymised, synthetic records. No personally identifiable information (PII) is stored in the repository.

## Domestic Violence State Form (DV)

| Column | Type | Description | Allowed Values | Example Rows (1-5) |
| --- | --- | --- | --- | --- |
| `CaseNumber` | string | Unique identifier for each DV case. | Alphanumeric, prefixed `DV-`. | DV-1 · DV-2 · DV-3 · DV-4 · DV-5 |
| `IncidentDate` | date | The date the incident occurred. | ISO date (`YYYY-MM-DD`). | 2025-10-01 · 2025-10-05 · 2025-10-07 · 2025-10-09 · 2025-10-11 |
| `BetweenDate` | date | Alternate occurrence date when `IncidentDate` is missing. | ISO date or blank. | — · 2025-10-05 · — · — · — |
| `ReportDate` | date | Date the incident was reported. | ISO date. | 2025-10-02 · 2025-10-06 · 2025-10-08 · 2025-10-10 · 2025-10-12 |
| `VictimYN` | string | Indicator if victim confirmed incident. | `Y`, `N`, `Yes`, `No`, case-insensitive variants. | Y · N · Yes · No · y |
| `VictimRace` | categorical | Race codes mapped to canonical values. | `W`, `B`, `A`, `P`, `I`, `U`. | W · B · A · P · U |
| `VictimEthnicity` | categorical | Ethnicity codes. | `H` (Hispanic), `NH` (Non-Hispanic), `U` (Unknown). | NH · H · NH · U · H |
| `VictimSex` | categorical | Victim sex/gender code. | `F`, `M`, `X`, `U`. | F · M · F · F · M |

## Computer-Aided Dispatch (CAD)

| Column | Type | Description | Allowed Values | Example Rows (1-5) |
| --- | --- | --- | --- | --- |
| `ReportNumberNew` | string | Dispatch report identifier. | Alphanumeric. | CAD-230101 · CAD-230102 · CAD-230103 · CAD-230104 · CAD-230105 |
| `FullAddress2` | string | Normalised dispatch address. | Street + city. | 123 Main St · 456 Oak Ave · 789 Pine Rd · 101 Maple Blvd · 202 Birch Ln |
| `PDZone` | string | Patrol or command zone. | `HQ`, `North`, `East`, `West`, `South`, etc. | HQ · North · East · West · South |
| `Incident` | categorical | Dispatch incident type. | Controlled vocabulary (see `docs/mappings/incident_type_map.csv`). | Threats · Assault · Harassment · Assault · Threats |
| `CallReceived` | datetime | Timestamp incident logged. | ISO datetime (`YYYY-MM-DD HH:MM:SS`) TZ=America/New_York. | 2025-10-01 18:23:00-04:00 · … |
| `TimeResponse` | duration | Time from dispatch to arrival. | HH:MM:SS strings. | 00:02:00 · 00:04:00 · 00:03:00 · 00:05:00 · 00:01:30 |

## Records Management System (RMS)

| Column | Type | Description | Allowed Values | Example Rows (1-5) |
| --- | --- | --- | --- | --- |
| `CaseNumber` | string | Shared join key with DV form. | Matches DV case numbers. | DV-1 · DV-2 · DV-3 · DV-4 · DV-5 |
| `OfficerBadge` | string | Primary reporting officer identifier. | Badge number or code. | 1021 · 1045 · 1188 · 1203 · 1301 |
| `OffenseCode` | string | State offence code. | NJ UCR codes, uppercase. | 2C:12-1A(1) · 2C:25-17 · 2C:12-3A · 2C:25-18 · 2C:12-1B |
| `Disposition` | categorical | Case outcome. | `Closed`, `Pending`, `Arrest`, `Unfounded`, etc. | Closed · Arrest · Pending · Closed · Pending |
| `ReportDate` | datetime | RMS report datetime (America/New_York). | ISO datetime with TZ. | 2025-10-02T09:15:00-04:00 · … |
| `NarrativeLength` | integer | Character length of narrative text. | ≥ 0. | 1420 · 980 · 1633 · 1205 · 873 |

## General Rules

- Date/times are parsed with timezone `America/New_York`. Store as aware datetimes in ETL outputs.
- Boolean flags derive from `docs/mappings/yes_no_bool_map.csv`. Avoid hard-coded mappings in code.
- Approved race/ethnicity codes live in `docs/mappings/race_ethnicity_map.csv` and must be referenced at runtime.
- Incident type canonical names come from `docs/mappings/incident_type_map.csv` to maintain consistent reporting.
- Location joins use `docs/mappings/location_join_keys.csv`.

Please keep this dictionary updated as new fields enter the pipeline.

