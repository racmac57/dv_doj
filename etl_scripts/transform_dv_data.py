"""
Enhanced DV Data Transformation
Consolidates boolean columns into single categorical columns and fixes data types
"""

import logging
import re
from datetime import datetime, time
from pathlib import Path

import pandas as pd
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAPPINGS_DIR = Path("docs/mappings")
RACE_ETHNICITY_FILE = MAPPINGS_DIR / "race_ethnicity_map.csv"
YES_NO_FILE = MAPPINGS_DIR / "yes_no_bool_map.csv"
RMS_EXPORT_PATH = Path("raw_data/xlsx/output/_2023_2025_10_31_dv_rms.csv")
CAD_EXPORT_PATH = Path("raw_data/xlsx/output/_2023_2025_10_31_dv_cad.csv")
EASTERN = ZoneInfo("America/New_York")


def load_race_ethnicity_mappings():
    if not RACE_ETHNICITY_FILE.exists():
        logger.warning("Race/Ethnicity mapping file %s not found.", RACE_ETHNICITY_FILE)
        return {}, {}
    df = pd.read_csv(RACE_ETHNICITY_FILE)
    race = {
        str(row["source"]).strip(): str(row["value"]).strip()
        for _, row in df[df["category"].str.lower() == "race"].iterrows()
    }
    ethnicity = {
        str(row["source"]).strip(): str(row["value"]).strip()
        for _, row in df[df["category"].str.lower() == "ethnicity"].iterrows()
    }
    return race, ethnicity


def load_yes_no_mapping():
    if not YES_NO_FILE.exists():
        logger.warning("Yes/No mapping file %s not found.", YES_NO_FILE)
        truthy = {"Y", "YES", "T", "TRUE", "1", "X", "O"}
        falsy = {"N", "NO", "F", "FALSE", "0"}
    else:
        df = pd.read_csv(YES_NO_FILE)
        truthy = {
            str(v).strip().upper()
            for v in df[df["boolean"].astype(str).str.lower() == "true"]["raw"]
        }
        falsy = {
            str(v).strip().upper()
            for v in df[df["boolean"].astype(str).str.lower() == "false"]["raw"]
        }
    return truthy, falsy


def to_eastern(series: pd.Series) -> pd.Series:
    dt_series = pd.to_datetime(series, errors="coerce")
    if getattr(dt_series.dt, "tz", None) is None:
        try:
            return dt_series.dt.tz_localize(EASTERN, nonexistent="NaT", ambiguous="NaT")
        except TypeError:
            return dt_series.dt.tz_localize(EASTERN)
    return dt_series.dt.tz_convert(EASTERN)

def fix_offense_date_column(df):
    """Fix column 'c' or 'C' to be named 'OffenseDate' and ensure it's date-only"""
    # Check for lowercase 'c' (original) or uppercase 'C' (already fixed)
    if 'c' in df.columns:
        logger.info("Renaming column 'c' to 'OffenseDate'")
        df = df.rename(columns={'c': 'OffenseDate'})
    elif 'C' in df.columns:
        logger.info("Renaming column 'C' to 'OffenseDate'")
        df = df.rename(columns={'C': 'OffenseDate'})
    
    if 'OffenseDate' in df.columns:
        # Ensure it's date-only (no time component)
        if pd.api.types.is_datetime64_any_dtype(df['OffenseDate']):
            # Convert to date object (date-only, no time)
            df['OffenseDate'] = pd.to_datetime(df['OffenseDate']).dt.date
            logger.info("Converted OffenseDate to date-only")
        else:
            # Try to parse as date
            df['OffenseDate'] = pd.to_datetime(df['OffenseDate'], errors='coerce').dt.date
            logger.info("Parsed and converted OffenseDate to date-only")
    
    return df

def consolidate_victim_race(df, race_mapping=None):
    """
    Consolidate VictimRace_X boolean columns into single VictimRace column
    with codes: W, A, B, P, I, U
    """
    race_mapping = race_mapping or load_race_ethnicity_mappings()[0]
    
    race_cols = [col for col in race_mapping.keys() if col in df.columns]
    
    if not race_cols:
        logger.warning("No VictimRace columns found")
        return df
    
    logger.info(f"Consolidating {len(race_cols)} VictimRace columns into single column")
    
    # Create new consolidated column
    df['VictimRace'] = None
    
    truthy, _ = load_yes_no_mapping()

    for col, code in race_mapping.items():
        if col in df.columns:
            # Check if value is True or X/O
            mask = df[col] == True
            if not mask.any():
                # Try checking for X or O
                mask = df[col].astype(str).str.strip().str.upper().isin(truthy)
            
            df.loc[mask, 'VictimRace'] = code
    
    # Drop old race columns
    df = df.drop(columns=race_cols)
    logger.info(f"Dropped {len(race_cols)} old race columns")
    
    return df

def consolidate_victim_ethnicity(df, ethnicity_mapping=None):
    """
    Consolidate VictimEthnic_H and VictimEthnic_NH into single VictimEthnicity column
    H = Hispanic, NH = Non-Hispanic
    """
    _, ethnicity_defaults = load_race_ethnicity_mappings()
    ethnicity_mapping = ethnicity_mapping or ethnicity_defaults
    ethnic_cols = [col for col in ethnicity_mapping.keys() if col in df.columns]
    
    if not ethnic_cols:
        logger.warning("No VictimEthnic columns found")
        return df
    
    logger.info(f"Consolidating {len(ethnic_cols)} VictimEthnic columns")
    
    df['VictimEthnicity'] = None
    
    truthy, _ = load_yes_no_mapping()

    for col, code in ethnicity_mapping.items():
        if col in df.columns:
            mask = df[col] == True
            if not mask.any():
                mask = df[col].astype(str).str.strip().str.upper().isin(truthy)
            df.loc[mask, 'VictimEthnicity'] = code
    
    # Drop old columns
    df = df.drop(columns=ethnic_cols)
    logger.info(f"Dropped {len(ethnic_cols)} old ethnicity columns")
    
    return df

def rename_sex_columns(df):
    """Rename VictimSexF to FemaleVictim and VictimSexM to MaleVictim"""
    rename_map = {}
    
    if 'VictimSexF' in df.columns:
        rename_map['VictimSexF'] = 'FemaleVictim'
        logger.info("Renaming VictimSexF to FemaleVictim")
    
    if 'VictimSexM' in df.columns:
        rename_map['VictimSexM'] = 'MaleVictim'
        logger.info("Renaming VictimSexM to MaleVictim")
    
    if rename_map:
        df = df.rename(columns=rename_map)
    
    return df

def consolidate_day_of_week(df):
    """
    Consolidate day of week boolean columns into single DayOfWeek column
    Options: Sun, Mon, Tue, Wed, Thu, Fri, Sat (or 1-7)
    Using abbreviated names: Sun, Mon, Tue, Wed, Thu, Fri, Sat
    """
    dow_mapping = {
        'Sunday': 'Sun',
        'Monday': 'Mon',
        'Tuesday': 'Tue',
        'Wednesday': 'Wed',
        'Thursday': 'Thu',
        'Friday': 'Fri',
        'Saturday': 'Sat',
    }
    
    dow_cols = [col for col in dow_mapping.keys() if col in df.columns]
    
    if not dow_cols:
        logger.warning("No day of week columns found")
        return df
    
    logger.info(f"Consolidating {len(dow_cols)} day of week columns")
    
    df['DayOfWeek'] = None
    
    for col, code in dow_mapping.items():
        if col in df.columns:
            mask = df[col] == True
            if not mask.any():
                mask = df[col].astype(str).str.strip().str.upper().isin(['X', 'O', 'TRUE'])
            df.loc[mask, 'DayOfWeek'] = code
    
    # Drop old columns
    df = df.drop(columns=dow_cols)
    logger.info(f"Dropped {len(dow_cols)} old day of week columns")
    
    return df

def drop_municipality_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove municipality columns that duplicate static metadata."""
    drop_cols = [col for col in ("Municipality", "MunicipalityCode", "MunicipalityPhone") if col in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)
        logger.info("Dropped municipality columns: %s", ", ".join(drop_cols))
    return df

def ensure_data_types(df):
    """Ensure proper data types for specific columns"""
    
    # OffenseDate should be date
    if 'OffenseDate' in df.columns:
        localized = to_eastern(df['OffenseDate'])
        df['OffenseDate'] = localized.dt.date

    # Normalize other *_Date columns to timezone-aware datetimes
    date_columns = [col for col in df.columns if col.endswith('Date') and col != 'OffenseDate']
    for column in date_columns:
        localized = to_eastern(df[column])
        df[column] = localized
    
    # Time should be time (or timedelta if already duration)
    if 'Time' in df.columns:
        if pd.api.types.is_timedelta64_dtype(df['Time']):
            logger.info("Time column is already timedelta64 (duration)")
        else:
            # Try to convert to time
            try:
                df['Time'] = pd.to_timedelta(df['Time'])
                logger.info("Converted Time to timedelta64")
            except:
                logger.warning("Could not convert Time to timedelta")
    
    # TotalTime should be duration (timedelta)
    if 'TotalTime' in df.columns:
        if not pd.api.types.is_timedelta64_dtype(df['TotalTime']):
            try:
                df['TotalTime'] = pd.to_timedelta(df['TotalTime'])
                logger.info("Converted TotalTime to timedelta64")
            except:
                logger.warning("Could not convert TotalTime to timedelta")
        else:
            logger.info("TotalTime is already timedelta64 (duration)")
    
    # VictimAge - keep as numeric (int)
    if 'VictimAge' in df.columns:
        if df['VictimAge'].dtype == 'object':
            # Try to convert to numeric
            df['VictimAge'] = pd.to_numeric(df['VictimAge'], errors='coerce')
            logger.info("Converted VictimAge to numeric")
        else:
            logger.info(f"VictimAge is already numeric: {df['VictimAge'].dtype}")
    
    return df


def _load_reference_csv(path: Path, required_columns: set[str]) -> pd.DataFrame | None:
    if not path.exists():
        logger.warning("Reference file %s not found; skipping backfill.", path)
        return None
    try:
        ref_df = pd.read_csv(path, engine="pyarrow")
    except (ImportError, ValueError):
        ref_df = pd.read_csv(path, low_memory=False)
    missing = required_columns.difference(ref_df.columns)
    if missing:
        logger.warning("Reference file %s missing columns: %s", path, ", ".join(sorted(missing)))
        return None
    return ref_df


def backfill_temporal_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Backfill OffenseDate, DayOfWeek, and Time using RMS (primary) and CAD (fallback) data."""
    if "CaseNumber" not in df.columns:
        logger.warning("CaseNumber column missing; cannot backfill temporal fields.")
        return df

    case_key = df["CaseNumber"].astype(str).str.strip()

    offense_dates = pd.to_datetime(df.get("OffenseDate"), errors="coerce")
    time_values = pd.to_timedelta(df.get("Time"), errors="coerce")
    day_values = df.get("DayOfWeek").astype("string") if "DayOfWeek" in df.columns else pd.Series(pd.NA, index=df.index, dtype="string")

    offense_missing = offense_dates.isna()
    time_missing = time_values.isna() | (time_values == pd.Timedelta(0))
    day_missing = day_values.isna() | (day_values.str.strip() == "")

    rms_df = _load_reference_csv(RMS_EXPORT_PATH, {"Case Number", "Incident Date", "Incident Time"})
    if rms_df is not None:
        rms_df["_case_key"] = rms_df["Case Number"].astype(str).str.strip()
        rms_df["_incident_date"] = pd.to_datetime(rms_df["Incident Date"], errors="coerce")
        rms_df["_incident_time"] = pd.to_timedelta(rms_df["Incident Time"], errors="coerce")
        rms_df["_incident_dow"] = rms_df["_incident_date"].dt.day_name().str[:3]

        date_map = rms_df.dropna(subset=["_incident_date"]).set_index("_case_key")["_incident_date"].to_dict()
        time_map = rms_df.dropna(subset=["_incident_time"]).set_index("_case_key")["_incident_time"].to_dict()
        dow_map = rms_df.dropna(subset=["_incident_dow"]).set_index("_case_key")["_incident_dow"].to_dict()

        offense_dates[offense_missing] = case_key.map(date_map)[offense_missing]
        time_values[time_missing] = case_key.map(time_map)[time_missing]
        day_values[day_missing] = case_key.map(dow_map)[day_missing]

        offense_missing = offense_dates.isna()
        time_missing = time_values.isna() | (time_values == pd.Timedelta(0))
        day_missing = day_values.isna() | (day_values.str.strip() == "")

    cad_df = _load_reference_csv(CAD_EXPORT_PATH, {"ReportNumberNew", "Time of Call", "DayofWeek"})
    if cad_df is not None:
        cad_df["_case_key"] = cad_df["ReportNumberNew"].astype(str).str.strip()
        cad_dt = pd.to_datetime(cad_df["Time of Call"], errors="coerce")
        cad_df["_call_date"] = cad_dt.dt.normalize()
        cad_df["_call_time"] = pd.to_timedelta(cad_dt.dt.strftime("%H:%M:%S"), errors="coerce")
        cad_df["_call_dow"] = cad_df["DayofWeek"].astype(str).str.strip().str[:3]

        cad_date_map = cad_df.dropna(subset=["_call_date"]).set_index("_case_key")["_call_date"].to_dict()
        cad_time_map = cad_df.dropna(subset=["_call_time"]).set_index("_case_key")["_call_time"].to_dict()
        cad_dow_map = cad_df.dropna(subset=["_call_dow"]).set_index("_case_key")["_call_dow"].to_dict()

        offense_dates[offense_missing] = case_key.map(cad_date_map)[offense_missing]
        time_values[time_missing] = case_key.map(cad_time_map)[time_missing]
        day_values[day_missing] = case_key.map(cad_dow_map)[day_missing]

    df["OffenseDate"] = offense_dates.dt.date
    if "Time" in df.columns:
        df["Time"] = time_values
    if "DayOfWeek" in df.columns:
        df["DayOfWeek"] = day_values.str[:3]
    else:
        df["DayOfWeek"] = day_values.str[:3]

    return df


def normalize_death_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Convert death indicator columns to boolean."""
    death_cols = [col for col in ("JuvDeaths_M", "AdultDeaths_M", "AdultDeaths_F", "JuvDeaths_F") if col in df.columns]
    for col in death_cols:
        series = df[col]
        df[col] = (
            series.replace({"0": 0, "1": 1})
            .astype("float")
            .apply(lambda x: None if pd.isna(x) else bool(int(x)))
            .astype("boolean")
        )
    if death_cols:
        logger.info("Normalised death indicator columns to boolean: %s", ", ".join(death_cols))
    return df


def format_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert timedelta columns to HH:MM:SS string format for readability."""
    def _format_td(value) -> str | None:
        if pd.isna(value):
            return None
        td = pd.to_timedelta(value, errors="coerce")
        if pd.isna(td):
            return None
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    for col in ("Time", "TotalTime"):
        if col in df.columns:
            df[col] = df[col].apply(_format_td).astype("string")
    return df


def _load_tabular(input_path: Path) -> pd.DataFrame:
    """Load CSV (preferred) or Excel input into a DataFrame."""
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(input_path, engine="pyarrow")
        except (ImportError, ValueError):
            return pd.read_csv(input_path, low_memory=False)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        logger.warning(
            "Reading Excel input %s; consider converting to CSV for faster processing.",
            input_path,
        )
        return pd.read_excel(input_path, engine="openpyxl")
    raise ValueError(f"Unsupported input format for DV data: {input_path.suffix}")


def process_dv_file(input_file, output_file=None):
    """
    Process the DV file with all transformations
    """
    logger.info(f"Processing {input_file}")
    
    # Read the file
    input_path = Path(input_file)
    df = _load_tabular(input_path)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    original_cols = len(df.columns)
    
    # Apply transformations in order
    df = fix_offense_date_column(df)
    race_map, ethnicity_map = load_race_ethnicity_mappings()
    df = consolidate_victim_race(df, race_map)
    df = consolidate_victim_ethnicity(df, ethnicity_map)
    df = rename_sex_columns(df)
    df = consolidate_day_of_week(df)
    df = drop_municipality_columns(df)
    df = backfill_temporal_fields(df)
    df = ensure_data_types(df)
    df = normalize_death_flags(df)
    df = format_time_columns(df)
    
    logger.info(f"Reduced from {original_cols} to {len(df.columns)} columns")
    
    # Save output
    if output_file is None:
        output_file = Path('processed_data') / f"{input_path.stem}_transformed.csv"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    suffix = output_path.suffix.lower()
    logger.info(f"Saving to {output_path}")
    
    if suffix == ".csv" or suffix == "":
        if suffix == "":
            output_path = output_path.with_suffix(".csv")
        if output_path.exists():
            try:
                output_path.unlink()
            except PermissionError:
                logger.warning("Could not remove existing output %s before write; attempting to overwrite directly.", output_path)
        df.to_csv(output_path, index=False)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        df.to_excel(output_path, index=False, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported output format: {output_path.suffix}")
    
    return df

def main(src=None, out=None):
    """Main function"""
    if src is None:
        candidates = list(Path('processed_data').glob("*_dv_fixed*.csv"))
        if not candidates:
            candidates = list(Path('processed_data').glob("*_dv_fixed*.xlsx"))
        input_file = candidates[0] if candidates else Path('processed_data/_2023_2025_10_31_dv_fixed.csv')
    else:
        src_path = Path(src)
        if src_path.is_dir():
            candidates = sorted(src_path.glob("*dv*.csv"))
            if not candidates:
                candidates = sorted(src_path.glob("*dv*.xlsx"))
            if candidates:
                input_file = candidates[0]
            else:
                fallback = sorted(Path('processed_data').glob("*dv*.csv"))
                if not fallback:
                    fallback = sorted(Path('processed_data').glob("*dv*.xlsx"))
                if fallback:
                    input_file = fallback[0]
                    logger.warning(
                        "No DV files found in %s; using fallback %s",
                        src_path,
                        input_file,
                    )
                else:
                    logger.error("No DV files found in %s", src_path)
                    return
        else:
            input_file = src_path

    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run fix_dv_headers.py first")
        return

    output_dir = Path(out) if out else Path('processed_data')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_file.stem}_transformed.csv"

    print("="*80)
    print("DV DATA TRANSFORMATION")
    print("="*80)

    df = process_dv_file(input_file, output_file=output_file)

    print("\n" + "="*80)
    print("TRANSFORMATION COMPLETE")
    print("="*80)
    print(f"\nOutput saved to: {output_file}")
    print(f"\nFinal column count: {len(df.columns)}")
    print(f"\nKey consolidated columns:")
    if 'VictimRace' in df.columns:
        print(f"  VictimRace: {df['VictimRace'].value_counts().to_dict()}")
    if 'VictimEthnicity' in df.columns:
        print(f"  VictimEthnicity: {df['VictimEthnicity'].value_counts().to_dict()}")
    if 'DayOfWeek' in df.columns:
        print(f"  DayOfWeek: {df['DayOfWeek'].value_counts().to_dict()}")

if __name__ == "__main__":
    main()

