import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import json


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    valid_municipalities: set[str] = field(default_factory=lambda: {"Hackensack"})
    valid_races: set[str] = field(default_factory=lambda: {"W", "B", "A", "I", "P", "U"})
    valid_ethnicities: set[str] = field(default_factory=lambda: {"H", "NH"})
    min_age: int = 0
    max_age: int = 120
    date_start: str = "2023-01-01"
    date_end: str = "2025-12-31"
    case_number_pattern: str = r"^\d{2}-\d{6}$"
    death_columns: List[str] = field(default_factory=lambda: [
        "JuvDeaths_M",
        "AdultDeaths_M",
        "AdultDeaths_F",
        "JuvDeaths_F",
    ])


DEFAULT_DV = Path("processed_data/_2023_2025_10_31_dv_fixed_transformed_transformed.csv")
DEFAULT_RMS = Path("raw_data/xlsx/output/_2023_2025_10_31_dv_rms.csv")
DEFAULT_CAD = Path("raw_data/xlsx/output/_2023_2025_10_31_dv_cad.csv")
DEFAULT_OUT = Path("processed_data/dv_final.csv")
DEFAULT_LOG_DIR = Path("logs")
CONFIG = ValidationConfig()

__all__ = [
    "CONFIG",
    "backfill_cad",
    "backfill_rms",
    "clean_deaths",
    "drop_empty_cols",
    "flag_missing",
    "validate_data",
]


def _read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, engine="pyarrow")
    except (ImportError, ValueError):
        return pd.read_csv(path, low_memory=False)


def load_sources(
    dv_path: Path = DEFAULT_DV,
    rms_path: Path = DEFAULT_RMS,
    cad_path: Path = DEFAULT_CAD,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    log.info("Loading DV data from %s", dv_path)
    dv = _read_csv(dv_path)
    log.info("Loading RMS export from %s", rms_path)
    rms = _read_csv(rms_path)
    log.info("Loading CAD export from %s", cad_path)
    cad = _read_csv(cad_path)
    log.info("Loaded DV=%s rows, RMS=%s rows, CAD=%s rows", len(dv), len(rms), len(cad))
    return dv, rms, cad


CASE_PATTERN = re.compile(CONFIG.case_number_pattern)


def standardise_case_number(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.upper()
    normalized = normalized.replace({"NAN": pd.NA, "NONE": pd.NA, "NULL": pd.NA, "": pd.NA})
    return normalized


def flag_missing_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "CaseNumber" not in df.columns:
        df["CaseNumber"] = pd.NA
    if "VictimAge" not in df.columns:
        df["VictimAge"] = pd.NA
    df["CN_Flag"] = df["CaseNumber"].isna()
    df["VA_Flag"] = df["VictimAge"].isna()
    return df


def _extract_reviewer(text: str | float) -> str | None:
    if pd.isna(text):
        return None
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    if not cleaned:
        return None
    id_match = re.search(r"(\d+)$", cleaned)
    if id_match:
        return id_match.group(1)
    cleaned = re.sub(r"\s+\d+$", "", cleaned)
    tokens = cleaned.replace(".", "").split()
    if len(tokens) >= 2:
        first_initial = tokens[-2][0].upper()
        last_name = tokens[-1].title()
        return f"{first_initial}. {last_name}"
    return tokens[0].title()


def backfill_from_rms(df: pd.DataFrame, rms: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "CaseNumber" not in df.columns:
        df["CaseNumber"] = pd.NA
    if "ReviewedBy" not in df.columns:
        df["ReviewedBy"] = pd.NA
    for col in ["OffenseDate", "Time", "FullAddress", "Narrative"]:
        if col not in df.columns:
            df[col] = pd.NA
    rms = rms.rename(columns={"Case Number": "CaseNumber"})
    keep_cols = [
        "CaseNumber",
        "Incident Date",
        "Incident Time",
        "FullAddress",
        "Narrative",
        "Officer of Record",
    ]
    missing_cols = set(keep_cols) - set(rms.columns)
    if missing_cols:
        log.warning("RMS export missing expected columns: %s", ", ".join(sorted(missing_cols)))
        keep_cols = [c for c in keep_cols if c in rms.columns]
    rms_subset = rms[keep_cols].copy()
    df = df.merge(rms_subset, on="CaseNumber", how="left", suffixes=("", "_RMS"))
    source_dates = "Incident Date_RMS" if "Incident Date_RMS" in df.columns else "Incident Date"
    if source_dates in df.columns:
        df["OffenseDate"] = df["OffenseDate"].fillna(df[source_dates])
    source_times = "Incident Time_RMS" if "Incident Time_RMS" in df.columns else "Incident Time"
    if source_times in df.columns:
        df["Time"] = df["Time"].apply(_coerce_time)
        df["Time"] = df["Time"].fillna(df[source_times].apply(_coerce_time))
    source_reviewer = "Officer of Record_RMS" if "Officer of Record_RMS" in df.columns else "Officer of Record"
    if source_reviewer in df.columns:
        reviewer = df[source_reviewer].apply(_extract_reviewer)
        df["ReviewedBy"] = df["ReviewedBy"].fillna(reviewer)
    addr_col = "FullAddress_RMS" if "FullAddress_RMS" in df.columns else "FullAddress"
    if addr_col in df.columns and "FullAddress" in df.columns:
        df["FullAddress"] = df["FullAddress"].fillna(df[addr_col])
    narr_col = "Narrative_RMS" if "Narrative_RMS" in df.columns else "Narrative"
    if narr_col in df.columns and "Narrative" in df.columns:
        df["Narrative"] = df["Narrative"].fillna(df[narr_col])

    return df


def _parse_cad_datetime(value: Any) -> pd.Timestamp | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    time_part = value.strip().split()[-1]
    if "T" in value:
        time_part = value.split("T", 1)[1]
    if ":" in time_part:
        try:
            parts = time_part.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            if hour > 23 or minute > 59:
                return None
        except ValueError:
            return None
    return parsed


def backfill_from_cad(df: pd.DataFrame, cad: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "CaseNumber" not in df.columns:
        df["CaseNumber"] = pd.NA
    rename_map = {
        "ReportNumberNew": "CaseNumber",
        "Time of Call": "TimeOfCall",
        "FullAddress2": "CAD_Address",
        "CADNotes": "CAD_Notes",
    }
    cad = cad.rename(columns=rename_map)
    required = {"CaseNumber", "TimeOfCall"}
    missing_cols = required - set(cad.columns)
    if missing_cols:
        log.warning("CAD export missing expected columns: %s", ", ".join(sorted(missing_cols)))
    if "TimeOfCall" in cad.columns:
        cad_parsed = cad["TimeOfCall"].apply(_parse_cad_datetime)
        cad_parsed = pd.to_datetime(cad_parsed, errors="coerce")
    else:
        cad_parsed = pd.Series(pd.NaT, index=cad.index, dtype="datetime64[ns]")
    cad["CAD_Date"] = cad_parsed.dt.date
    cad["CAD_Time"] = cad_parsed.dt.time
    cad["CAD_Day"] = cad_parsed.dt.day_name()

    merge_cols = [c for c in ["CaseNumber", "CAD_Date", "CAD_Time", "CAD_Day", "CAD_Address", "CAD_Notes"] if c in cad.columns]
    cad_subset = cad[merge_cols].copy()

    for col in ["OffenseDate", "Time", "DayOfWeek"]:
        if col not in df.columns:
            df[col] = pd.NA

    df = df.merge(cad_subset, on="CaseNumber", how="left", suffixes=("", "_CAD"))

    if "CAD_Date" in df.columns:
        df["OffenseDate"] = df["OffenseDate"].fillna(df["CAD_Date"].astype("string"))
    if "CAD_Time" in df.columns:
        df["Time"] = df["Time"].apply(_coerce_time)
        cad_time_td = df["CAD_Time"].apply(_coerce_time)
        df["Time"] = df["Time"].fillna(cad_time_td)
    if "CAD_Day" in df.columns:
        df["DayOfWeek"] = df["DayOfWeek"].fillna(df["CAD_Day"].astype(str).str[:3])

    return df


def clean_death_counts(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["JuvDeaths_M", "AdultDeaths_M", "AdultDeaths_F", "JuvDeaths_F"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        log.info("Dropping %s all-null columns", len(empty_cols))
        df = df.drop(columns=empty_cols)
    return df


def final_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    # Drop rows where CaseNumber is entirely missing and contains no other data
    if "CaseNumber" in df.columns:
        missing_cn = df["CaseNumber"].isna()
        if missing_cn.any():
            empty_rows = df.loc[missing_cn].drop(columns=[c for c in ["CN_Flag", "VA_Flag"] if c in df.columns]).isna().all(axis=1)
            drop_idx = empty_rows[empty_rows].index
            if len(drop_idx):
                log.info("Dropping %s rows with no data and missing CaseNumber", len(drop_idx))
                df = df.drop(index=drop_idx)

    before = len(df)
    if "CaseNumber" in df.columns:
        df.drop_duplicates(subset="CaseNumber", keep="first", inplace=True)
    dropped = before - len(df)
    if dropped:
        log.info("Dropped %s duplicate CaseNumber rows", dropped)

    if "CaseNumber" in df.columns:
        case_series = df["CaseNumber"].astype("string")
        valid_case_mask = case_series.notna() & case_series.str.match(CASE_PATTERN)
        removed = (~valid_case_mask).sum()
        if removed:
            log.info("Removing %s rows with invalid or missing CaseNumber", int(removed))
        df = df.loc[valid_case_mask].copy()

    # Standardise whitespace on string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip()

    if "DayOfWeek" in df.columns:
        df["DayOfWeek"] = df["DayOfWeek"].astype(str).str.strip().str[:3].replace({"nan": pd.NA})

    df["Time"] = df["Time"].apply(_coerce_time)
    df["TotalTime"] = pd.to_timedelta(df.get("TotalTime"), errors="coerce")
    df["OffenseDate"] = pd.to_datetime(df.get("OffenseDate"), errors="coerce").dt.date

    return df


def run_backfill(
    dv_path: Path = DEFAULT_DV,
    rms_path: Path = DEFAULT_RMS,
    cad_path: Path = DEFAULT_CAD,
    out_path: Path = DEFAULT_OUT,
    log_dir: Path = DEFAULT_LOG_DIR,
) -> Path:
    dv, rms, cad = load_sources(dv_path, rms_path, cad_path)

    dv["CaseNumber"] = standardise_case_number(dv["CaseNumber"])
    dv = flag_missing_fields(dv)
    dv = backfill_from_rms(dv, rms)
    dv = backfill_from_cad(dv, cad)
    dv = clean_death_counts(dv)
    dv = drop_empty_columns(dv)
    dv = final_cleanup(dv)
    dv, issues, metrics = validate_data(dv, CONFIG)

    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "validation_report.txt").write_text("\n".join(issues), encoding="utf-8")
    (log_dir / "quality_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    dv.to_csv(out_path, index=False)
    log.info("Saved final DV dataset to %s (rows=%s, cols=%s)", out_path, len(dv), len(dv.columns))
    return out_path


def main(
    dv: str | Path | None = None,
    rms: str | Path | None = None,
    cad: str | Path | None = None,
    out: str | Path | None = None,
    log_dir: str | Path | None = None,
) -> Path:
    dv_path = Path(dv) if dv else DEFAULT_DV
    rms_path = Path(rms) if rms else DEFAULT_RMS
    cad_path = Path(cad) if cad else DEFAULT_CAD
    out_path = Path(out) if out else DEFAULT_OUT
    logs_path = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
    return run_backfill(dv_path, rms_path, cad_path, out_path, logs_path)


def validate_data(df: pd.DataFrame, config: ValidationConfig = CONFIG) -> tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    df = df.copy()
    issue_lines: List[str] = []
    metrics: Dict[str, Any] = {
        "total_records": int(len(df)),
        "validation_time": datetime.now().isoformat(),
    }

    # Case numbers
    if "CaseNumber" in df.columns:
        raw_cn = df["CaseNumber"].astype("string")
        cn_series = raw_cn.str.strip()
        missing = cn_series.isna().sum()
        spacing = (raw_cn.notna()) & (raw_cn != cn_series)
        invalid_pattern = (~cn_series.fillna("").str.match(config.case_number_pattern, na=False)).sum()
        invalid = int(invalid_pattern + spacing.sum())
        metrics["missing_case_number"] = int(missing)
        metrics["invalid_case_number_format"] = int(invalid)
        if missing:
            issue_lines.append(f"Missing CaseNumber: {missing}")
        if invalid:
            issue_lines.append(f"Invalid CaseNumber format: {invalid}")
        df["CaseNumber"] = cn_series
    else:
        metrics["missing_case_number"] = 0
        metrics["invalid_case_number_format"] = 0

    # Municipality
    if "Municipality" in df.columns:
        muni_series = df["Municipality"].astype("string")
        invalid_muni = (~muni_series.isna()) & (~muni_series.isin(config.valid_municipalities))
        invalid_muni_count = int(invalid_muni.sum())
        metrics["invalid_municipality"] = invalid_muni_count
        if invalid_muni_count:
            issue_lines.append(f"Invalid Municipality: {invalid_muni_count}")
    else:
        metrics["invalid_municipality"] = 0

    # Race/Ethnicity
    if "VictimRace" in df.columns:
        race_series = df["VictimRace"].astype("string").str.strip().replace({"": pd.NA})
        invalid_race = (~race_series.isna()) & (~race_series.isin(config.valid_races))
        invalid_race_count = int(invalid_race.sum())
        metrics["invalid_victim_race"] = invalid_race_count
        if invalid_race_count:
            issue_lines.append(f"Invalid VictimRace: {invalid_race_count}")
        df["VictimRace"] = race_series
    else:
        metrics["invalid_victim_race"] = 0
    if "VictimEthnicity" in df.columns:
        eth_series = df["VictimEthnicity"].astype("string").str.strip().replace({"": pd.NA})
        invalid_eth = (~eth_series.isna()) & (~eth_series.isin(config.valid_ethnicities))
        invalid_eth_count = int(invalid_eth.sum())
        metrics["invalid_victim_ethnicity"] = invalid_eth_count
        if invalid_eth_count:
            issue_lines.append(f"Invalid VictimEthnicity: {invalid_eth_count}")
        df["VictimEthnicity"] = eth_series
    else:
        metrics["invalid_victim_ethnicity"] = 0

    # Victim age
    if "VictimAge" in df.columns:
        df["VictimAge"] = pd.to_numeric(df["VictimAge"], errors="coerce")
        out_of_range_mask = ~df["VictimAge"].between(config.min_age, config.max_age)
        out_of_range = int(out_of_range_mask.sum())
        metrics["victim_age_out_of_range"] = out_of_range
        if out_of_range:
            issue_lines.append(f"VictimAge out of [{config.min_age}-{config.max_age}]: {out_of_range}")
            df.loc[out_of_range_mask, "VictimAge"] = pd.NA
    else:
        metrics["victim_age_out_of_range"] = 0

    # Offense dates
    if "OffenseDate" in df.columns:
        converted = pd.to_datetime(df["OffenseDate"], errors="coerce")
        df["OffenseDate"] = converted.dt.date
        start = pd.to_datetime(config.date_start).date()
        end = pd.to_datetime(config.date_end).date()
        valid_mask = converted.notna()
        invalid_range = valid_mask & (~converted.dt.date.between(start, end))
        invalid_date = int(invalid_range.sum())
        metrics["invalid_offense_date"] = invalid_date
        if invalid_date:
            issue_lines.append(f"OffenseDate outside {start}-{end}: {invalid_date}")
    else:
        metrics["invalid_offense_date"] = 0

    # Time parsing
    if "Time" in df.columns:
        df["Time"] = df["Time"].apply(_coerce_time)
        invalid_time = df["Time"].isna().sum()
        metrics["invalid_time"] = int(invalid_time)
        if invalid_time:
            issue_lines.append(f"Invalid Time format: {invalid_time}")
    else:
        metrics["invalid_time"] = 0

    # Death columns
    for col in config.death_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            negatives = (df[col] < 0).sum()
            metrics[f"negative_{col.lower()}"] = int(negatives)
            if negatives:
                issue_lines.append(f"Negative {col}: {negatives}")
        else:
            metrics[f"negative_{col.lower()}"] = 0

    # Duplicates
    if "CaseNumber" in df.columns:
        dup_count = df.duplicated(subset="CaseNumber", keep=False).sum() // 2
        metrics["duplicate_case_numbers"] = int(dup_count)
        if dup_count:
            issue_lines.append(f"Duplicate CaseNumber: {dup_count} pairs")
    else:
        metrics["duplicate_case_numbers"] = 0

    summary_lines = [
        f"\nVALIDATION SUMMARY ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
        f"Total Records: {len(df)}",
        f"Issues Found: {len(issue_lines)}",
    ]
    metrics["total_issues"] = len(issue_lines)
    issues = issue_lines + summary_lines
    return df, issues, metrics


def flag_missing(df: pd.DataFrame) -> pd.DataFrame:
    return flag_missing_fields(df)


def backfill_rms(df: pd.DataFrame, rms: pd.DataFrame) -> pd.DataFrame:
    return backfill_from_rms(df, rms)


def backfill_cad(df: pd.DataFrame, cad: pd.DataFrame) -> pd.DataFrame:
    return backfill_from_cad(df, cad)


def clean_deaths(df: pd.DataFrame) -> pd.DataFrame:
    return clean_death_counts(df)


def drop_empty_cols(df: pd.DataFrame) -> pd.DataFrame:
    return drop_empty_columns(df)


TIME_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")


def _coerce_time(value: Any) -> Any:
    if pd.isna(value):
        return None
    value_str = str(value).strip()
    match = TIME_PATTERN.match(value_str)
    if match:
        h, m, s = match.groups()
        h_i, m_i, s_i = int(h), int(m), int(s or 0)
        if h_i > 23 or m_i > 59 or s_i > 59:
            return None
        return pd.to_timedelta(f"{h_i:02d}:{m_i:02d}:{s_i:02d}")
    if "day" in value_str.lower():
        return None
    return pd.to_timedelta(value_str, errors="coerce")


if __name__ == "__main__":
    main()
