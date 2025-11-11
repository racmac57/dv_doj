# PII Policy for DV DOJ ETL Project

Updated: 2025-11-11

## Purpose

Safeguard personally identifiable information contained in CAD/RMS domestic violence data in alignment with New Jersey statutes and comparable GDPR principles. All contributors must ensure that PII never appears in commits, shared artifacts, or automated outputs.

## PII Categories

- **Direct identifiers**: Names, full addresses, Social Security numbers, phone/email, dates of birth, driver’s licence numbers, licence plates.
- **Indirect identifiers**: Precise geocodes, detailed incident timestamps, badge/officer IDs, CaseNumbers when linked to an individual, medical record numbers.

## Redaction Requirements

1. **Identification**
   - Scan incoming data for identifiers using pattern detection (e.g., `\d{3}-\d{2}-\d{4}` for SSNs, email regex, US phone patterns).
   - Review narrative text fields for free-form PII.
2. **Methods**
   - Replace values with `[REDACTED]`, hashed surrogate (SHA-256) or deterministic pseudonym (`anon_###`) depending on analytical need.
   - For geospatial work, aggregate or jitter coordinates before export to public maps.
3. **Tooling**
   - Integrate scrubbing helpers into ETL flows (e.g., in `etl_scripts/base_etl.py`) via `pandas.Series.replace` or third-party libraries such as `presidio-analyzer` or `faker`.
   - Ensure `verify_transformations.py` (or successor checks) logs redaction coverage.
4. **Verification**
   - After transformations, execute redaction tests/pytest fixtures that simulate PII leaks.
   - Retain log evidence that scrubbing ran (avoid logging raw values).

## Handling & Storage

- Never commit raw PII; `.gitignore` keeps `raw_data/`, `processed_data/`, `output/`, and `logs/` out of Git.
- Work only on secured local drives or encrypted network shares approved by the City of Hackensack.
- Logs or analytics outputs must redact sensitive fields before writing to disk.
- Any dataset shared externally must be anonymised and accompanied by a statement that PII has been removed. External recipients should sign NDAs when appropriate.

## Compliance & Governance

- **Audits**: Conduct quarterly reviews of redaction routines using automated tests and manual spot-checks.
- **Incident response**: Report suspected exposure to the project maintainer or City of Hackensack security office within 24 hours; rotate credentials and revoke access as needed.
- **Acknowledgement**: Contributors should confirm policy awareness (e.g., via PR checklist or onboarding form) before working with DV data.

## Examples

| Before | After |
| --- | --- |
| `Victim: Jane Doe, Addr: 123 Main St, Hackensack` | `Victim: [REDACTED], Addr: [REDACTED]` |
| `Phone: 201-555-1212` | `Phone: [REDACTED]` |
| `CaseNumber: 23-000123` | `CaseNumber: anon_case_001` |

## Roadmap

- Add optional Presidio/Faker integration for automatic redaction in CLI flows.
- Enable GitHub secret/PII scanning and pre-commit hooks that detect sensitive patterns.
- Expand contributor documentation/training that outlines DV-specific sensitivities.

Failure to follow this policy may result in removal of repository access and notification of the appropriate legal authority.
