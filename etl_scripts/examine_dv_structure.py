"""Examine DV file structure for transformations"""

import pandas as pd
from pathlib import Path

dv_file = Path('raw_data/xlsx/_2023_2025_10_31_dv.xlsx')
df = pd.read_excel(dv_file, nrows=10)

print("="*80)
print("COLUMN STRUCTURE ANALYSIS")
print("="*80)

# Column M (index 12, 13th column)
if len(df.columns) > 12:
    col_m = df.columns[12]
    print(f"\nColumn M (index 12): '{col_m}'")
    print(f"Sample values: {df[col_m].head().tolist()}")
    print(f"Data type: {df[col_m].dtype}")

# Check for Offense Date in any form
print("\nColumns with 'Offense' or 'Date':")
offense_cols = [c for c in df.columns if 'offense' in str(c).lower() or 'offence' in str(c).lower()]
date_cols = [c for c in df.columns if 'date' in str(c).lower()]
print(f"  Offense: {offense_cols}")
print(f"  Date: {date_cols}")

# Time columns
print("\nTime-related columns:")
time_cols = [c for c in df.columns if 'time' in str(c).lower()]
for tc in time_cols:
    print(f"  {tc}: {df[tc].head(3).tolist()}, dtype={df[tc].dtype}")

# MunicipalityCode
if 'gMunicipalityCode' in df.columns:
    print(f"\nMunicipalityCode unique values: {df['gMunicipalityCode'].unique()}")
elif 'MunicipalityCode' in df.columns:
    print(f"\nMunicipalityCode unique values: {df['MunicipalityCode'].unique()}")

# VictimAge
if 'VictimAge' in df.columns:
    print(f"\nVictimAge sample: {df['VictimAge'].head(10).tolist()}")
    print(f"VictimAge dtype: {df['VictimAge'].dtype}")
    print(f"VictimAge unique: {df['VictimAge'].unique()[:20]}")

# Victim Race columns
print("\nVictimRace columns:")
race_cols = [c for c in df.columns if 'VictimRace' in str(c)]
for rc in race_cols:
    print(f"  {rc}: True count = {df[rc].eq(True).sum() if df[rc].dtype == bool else df[rc].astype(str).str.strip().isin(['X', 'O']).sum()}")

# VictimEthnic columns
print("\nVictimEthnic columns:")
ethnic_cols = [c for c in df.columns if 'VictimEthnic' in str(c)]
for ec in ethnic_cols:
    print(f"  {ec}: True count = {df[ec].eq(True).sum() if df[ec].dtype == bool else df[ec].astype(str).str.strip().isin(['X', 'O']).sum()}")

# VictimSex columns
print("\nVictimSex columns:")
sex_cols = [c for c in df.columns if 'VictimSex' in str(c) or 'VictimSex' in str(c)]
for sc in sex_cols:
    print(f"  {sc}")

# Day of week columns
print("\nDay of week columns:")
dow_cols = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
for dow in dow_cols:
    if dow in df.columns:
        print(f"  {dow}: True count = {df[dow].eq(True).sum() if df[dow].dtype == bool else df[dow].astype(str).str.strip().isin(['X', 'O']).sum()}")

# Show first 20 column names with indices
print("\nFirst 20 columns with indices:")
for i, col in enumerate(df.columns[:20]):
    print(f"  {i:2d}. {col}")

