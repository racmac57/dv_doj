"""Verify the transformations were applied correctly"""

import pandas as pd
from pathlib import Path

df = pd.read_excel('processed_data/_2023_2025_10_31_dv_fixed_transformed.xlsx', nrows=10)

print("="*80)
print("VERIFICATION OF TRANSFORMATIONS")
print("="*80)

print("\n1. OffenseDate column:")
if 'OffenseDate' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Sample: {df['OffenseDate'].head(3).tolist()}")
    print(f"   Type: {type(df['OffenseDate'].iloc[0])}")
    print(f"   Dtype: {df['OffenseDate'].dtype}")
else:
    print("   [MISSING]")

print("\n2. Time column:")
if 'Time' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Sample: {df['Time'].head(3).tolist()}")
    print(f"   Dtype: {df['Time'].dtype}")
else:
    print("   [MISSING]")

print("\n3. TotalTime column:")
if 'TotalTime' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Sample: {df['TotalTime'].head(3).tolist()}")
    print(f"   Dtype: {df['TotalTime'].dtype}")
else:
    print("   [MISSING]")

print("\n4. VictimAge column:")
if 'VictimAge' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Sample: {df['VictimAge'].head(5).tolist()}")
    print(f"   Dtype: {df['VictimAge'].dtype}")
else:
    print("   [MISSING]")

print("\n5. VictimRace (consolidated):")
if 'VictimRace' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Value counts: {df['VictimRace'].value_counts().to_dict()}")
    print(f"   Sample: {df['VictimRace'].head(10).tolist()}")
else:
    print("   [MISSING]")
    
print("\n6. VictimEthnicity (consolidated):")
if 'VictimEthnicity' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Value counts: {df['VictimEthnicity'].value_counts().to_dict()}")
else:
    print("   [MISSING]")

print("\n7. Sex columns (renamed):")
if 'FemaleVictim' in df.columns:
    print(f"   [OK] FemaleVictim exists")
else:
    print("   ✗ FemaleVictim missing!")
if 'MaleVictim' in df.columns:
    print(f"   [OK] MaleVictim exists")
else:
    print("   ✗ MaleVictim missing!")

print("\n8. DayOfWeek (consolidated):")
if 'DayOfWeek' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Value counts: {df['DayOfWeek'].value_counts().to_dict()}")
else:
    print("   [MISSING]")

print("\n9. MunicipalityCode:")
if 'MunicipalityCode' in df.columns:
    print(f"   [OK] Exists")
    print(f"   Unique values: {df['MunicipalityCode'].unique()}")
else:
    print("   [MISSING]")

print("\n" + "="*80)
print(f"Total columns: {len(df.columns)}")
print("="*80)

