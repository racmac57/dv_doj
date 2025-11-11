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

def handle_municipality_code(df):
    """Handle MunicipalityCode - if all values are the same, we can note it or remove"""
    if 'MunicipalityCode' in df.columns:
        unique_vals = df['MunicipalityCode'].unique()
        if len(unique_vals) == 1:
            val = unique_vals[0]
            logger.info(f"MunicipalityCode has single value: {val}")
            logger.info("Keeping column but noting it's constant")
            # Could remove: df = df.drop(columns=['MunicipalityCode'])
    
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
    df = ensure_data_types(df)
    race_map, ethnicity_map = load_race_ethnicity_mappings()
    df = consolidate_victim_race(df, race_map)
    df = consolidate_victim_ethnicity(df, ethnicity_map)
    df = rename_sex_columns(df)
    df = consolidate_day_of_week(df)
    df = handle_municipality_code(df)
    
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

