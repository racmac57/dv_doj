"""Examine DV file structure for transformations"""

from pathlib import Path

import pandas as pd


def _find_dv_file() -> Path:
    candidates = [
        Path("raw_data/csv/_2023_2025_10_31_dv.csv"),
        Path("processed_data/_2023_2025_10_31_dv_fixed.csv"),
        Path("raw_data/xlsx/_2023_2025_10_31_dv.xlsx"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No DV source file found. Expected CSV in raw_data/csv or fallback Excel workbook."
    )


def _load_sample(path: Path, nrows: int = 10) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(path, engine="pyarrow", nrows=nrows)
        except (ImportError, ValueError):
            return pd.read_csv(path, low_memory=False, nrows=nrows)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, nrows=nrows, engine="openpyxl")
    raise ValueError(f"Unsupported file type: {path}")


def main() -> None:
    dv_file = _find_dv_file()
    df = _load_sample(dv_file, nrows=10)

    print("=" * 80)
    print("COLUMN STRUCTURE ANALYSIS")
    print("=" * 80)
    print(f"Source file: {dv_file}")

    if len(df.columns) > 12:
        col_m = df.columns[12]
        print(f"\nColumn M (index 12): '{col_m}'")
        print(f"Sample values: {df[col_m].head().tolist()}")
        print(f"Data type: {df[col_m].dtype}")

    print("\nColumns with 'Offense' or 'Date':")
    offense_cols = [c for c in df.columns if "offense" in str(c).lower() or "offence" in str(c).lower()]
    date_cols = [c for c in df.columns if "date" in str(c).lower()]
    print(f"  Offense: {offense_cols}")
    print(f"  Date: {date_cols}")

    print("\nTime-related columns:")
    time_cols = [c for c in df.columns if "time" in str(c).lower()]
    for tc in time_cols:
        print(f"  {tc}: {df[tc].head(3).tolist()}, dtype={df[tc].dtype}")

    if "gMunicipalityCode" in df.columns:
        print(f"\nMunicipalityCode unique values: {df['gMunicipalityCode'].unique()}")
    elif "MunicipalityCode" in df.columns:
        print(f"\nMunicipalityCode unique values: {df['MunicipalityCode'].unique()}")

    if "VictimAge" in df.columns:
        print(f"\nVictimAge sample: {df['VictimAge'].head(10).tolist()}")
        print(f"VictimAge dtype: {df['VictimAge'].dtype}")
        print(f"VictimAge unique: {df['VictimAge'].unique()[:20]}")

    print("\nVictimRace columns:")
    race_cols = [c for c in df.columns if "VictimRace" in str(c)]
    for rc in race_cols:
        if df[rc].dtype == bool:
            true_count = df[rc].eq(True).sum()
        else:
            true_count = df[rc].astype(str).str.strip().str.upper().isin(["X", "O", "TRUE"]).sum()
        print(f"  {rc}: True count = {true_count}")

    print("\nVictimEthnic columns:")
    ethnic_cols = [c for c in df.columns if "VictimEthnic" in str(c)]
    for ec in ethnic_cols:
        if df[ec].dtype == bool:
            true_count = df[ec].eq(True).sum()
        else:
            true_count = df[ec].astype(str).str.strip().str.upper().isin(["X", "O", "TRUE"]).sum()
        print(f"  {ec}: True count = {true_count}")

    print("\nVictimSex columns:")
    sex_cols = [c for c in df.columns if "VictimSex" in str(c)]
    for sc in sex_cols:
        print(f"  {sc}")

    print("\nDay of week columns:")
    dow_cols = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for dow in dow_cols:
        if dow in df.columns:
            if df[dow].dtype == bool:
                true_count = df[dow].eq(True).sum()
            else:
                true_count = df[dow].astype(str).str.strip().str.upper().isin(["X", "O", "TRUE"]).sum()
            print(f"  {dow}: True count = {true_count}")

    print("\nFirst 20 columns with indices:")
    for i, col in enumerate(df.columns[:20]):
        print(f"  {i:2d}. {col}")


if __name__ == "__main__":
    main()

