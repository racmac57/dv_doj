"""Quick script to check for Offense Date and suffix columns"""

import pandas as pd
from pathlib import Path

dv_file = Path('raw_data/xlsx/_2023_2025_10_31_dv.xlsx')
df = pd.read_excel(dv_file, nrows=1)

cols = list(df.columns)

print("Checking for Offense Date column...")
offense_date = [c for c in cols if 'offense' in c.lower() and 'date' in c.lower()]
if offense_date:
    print(f"Found: {offense_date}")
else:
    print("No 'Offense Date' column found")
    # Check for just 'date' columns
    date_cols = [c for c in cols if 'date' in c.lower()]
    print(f"Date columns found: {date_cols[:10]}")

print("\nChecking for suffix columns (_I, _H, _M, _W, _B)...")
suffix_cols = [c for c in cols if any(c.endswith(s) for s in ['_I', '_H', '_M', '_W', '_B'])]
print(f"Found {len(suffix_cols)} columns with suffixes:")
for c in suffix_cols[:20]:
    print(f"  {c}")

