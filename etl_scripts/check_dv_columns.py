"""Quick script to check for Offense Date and suffix columns"""

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
    raise FileNotFoundError("No DV file found. Expected CSV export or fallback Excel workbook.")


def _load_columns(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            df = pd.read_csv(path, engine="pyarrow", nrows=1)
        except (ImportError, ValueError):
            df = pd.read_csv(path, low_memory=False, nrows=1)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        df = pd.read_excel(path, nrows=1, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file type: {path}")
    return list(df.columns)


def main() -> None:
    dv_file = _find_dv_file()
    cols = _load_columns(dv_file)

    print(f"Source file: {dv_file}")

    print("Checking for Offense Date column...")
    offense_date = [c for c in cols if "offense" in c.lower() and "date" in c.lower()]
    if offense_date:
        print(f"Found: {offense_date}")
    else:
        print("No 'Offense Date' column found")
        date_cols = [c for c in cols if "date" in c.lower()]
        print(f"Date columns found: {date_cols[:10]}")

    print("\nChecking for suffix columns (_I, _H, _M, _W, _B)...")
    suffix_cols = [c for c in cols if any(c.endswith(s) for s in ["_I", "_H", "_M", "_W", "_B"])]
    print(f"Found {len(suffix_cols)} columns with suffixes:")
    for c in suffix_cols[:20]:
        print(f"  {c}")


if __name__ == "__main__":
    main()

