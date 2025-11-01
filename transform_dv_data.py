"""
Enhanced DV Data Transformation
Consolidates boolean columns into single categorical columns and fixes data types
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime, time
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def consolidate_victim_race(df):
    """
    Consolidate VictimRace_X boolean columns into single VictimRace column
    with codes: W, A, B, P, I, U
    """
    race_mapping = {
        'VictimRace_W': 'W',  # White
        'VictimRace_A': 'A',  # Asian
        'VictimRace_B': 'B',  # Black/African American
        'VictimRace_P': 'P',  # Native Hawaiian/Other Pacific Islander
        'VictimRace_I': 'I',  # American Indian/Alaska Native
        'VictimRace_U': 'U',  # Unknown
    }
    
    race_cols = [col for col in race_mapping.keys() if col in df.columns]
    
    if not race_cols:
        logger.warning("No VictimRace columns found")
        return df
    
    logger.info(f"Consolidating {len(race_cols)} VictimRace columns into single column")
    
    # Create new consolidated column
    df['VictimRace'] = None
    
    for col, code in race_mapping.items():
        if col in df.columns:
            # Check if value is True or X/O
            mask = df[col] == True
            if not mask.any():
                # Try checking for X or O
                mask = df[col].astype(str).str.strip().str.upper().isin(['X', 'O', 'TRUE'])
            
            df.loc[mask, 'VictimRace'] = code
    
    # Drop old race columns
    df = df.drop(columns=race_cols)
    logger.info(f"Dropped {len(race_cols)} old race columns")
    
    return df

def consolidate_victim_ethnicity(df):
    """
    Consolidate VictimEthnic_H and VictimEthnic_NH into single VictimEthnicity column
    H = Hispanic, NH = Non-Hispanic
    """
    ethnic_cols = [col for col in df.columns if 'VictimEthnic' in col]
    
    if not ethnic_cols:
        logger.warning("No VictimEthnic columns found")
        return df
    
    logger.info(f"Consolidating {len(ethnic_cols)} VictimEthnic columns")
    
    df['VictimEthnicity'] = None
    
    # Hispanic
    if 'VictimEthnic_H' in df.columns:
        mask = df['VictimEthnic_H'] == True
        if not mask.any():
            mask = df['VictimEthnic_H'].astype(str).str.strip().str.upper().isin(['X', 'O', 'TRUE'])
        df.loc[mask, 'VictimEthnicity'] = 'H'
    
    # Non-Hispanic
    if 'VictimEthnic_NH' in df.columns:
        mask = df['VictimEthnic_NH'] == True
        if not mask.any():
            mask = df['VictimEthnic_NH'].astype(str).str.strip().str.upper().isin(['X', 'O', 'TRUE'])
        df.loc[mask, 'VictimEthnicity'] = 'NH'
    
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
        if not pd.api.types.is_datetime64_any_dtype(df['OffenseDate']):
            df['OffenseDate'] = pd.to_datetime(df['OffenseDate']).dt.date
        else:
            df['OffenseDate'] = pd.to_datetime(df['OffenseDate']).dt.date
    
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

def process_dv_file(input_file, output_file=None):
    """
    Process the DV file with all transformations
    """
    logger.info(f"Processing {input_file}")
    
    # Read the file
    df = pd.read_excel(input_file, engine='openpyxl')
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    original_cols = len(df.columns)
    
    # Apply transformations in order
    df = fix_offense_date_column(df)
    df = ensure_data_types(df)
    df = consolidate_victim_race(df)
    df = consolidate_victim_ethnicity(df)
    df = rename_sex_columns(df)
    df = consolidate_day_of_week(df)
    df = handle_municipality_code(df)
    
    logger.info(f"Reduced from {original_cols} to {len(df.columns)} columns")
    
    # Save output
    if output_file is None:
        output_file = Path('processed_data') / f"{Path(input_file).stem}_transformed.xlsx"
    
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving to {output_file}")
    
    # Save as Excel
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # Also save as CSV for easy import
    csv_file = output_file.with_suffix('.csv')
    df.to_csv(csv_file, index=False)
    logger.info(f"Also saved as CSV: {csv_file}")
    
    return df

def main():
    """Main function"""
    # Use the already-fixed file as input
    input_file = Path('processed_data/_2023_2025_10_31_dv_fixed.xlsx')
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run fix_dv_headers.py first")
        return
    
    print("="*80)
    print("DV DATA TRANSFORMATION")
    print("="*80)
    
    df = process_dv_file(input_file)
    
    print("\n" + "="*80)
    print("TRANSFORMATION COMPLETE")
    print("="*80)
    print(f"\nOutput saved to: processed_data/_2023_2025_10_31_dv_fixed_transformed.xlsx")
    print(f"CSV version: processed_data/_2023_2025_10_31_dv_fixed_transformed.csv")
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

