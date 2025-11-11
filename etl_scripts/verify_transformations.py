"""Generate verification report for transformed DV dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd

DEFAULT_INPUT = Path("processed_data")
DEFAULT_OUTPUT = Path("logs")


def _select_input_file(src: Path) -> Path:
    if src.is_file():
        return src
    candidates = sorted(src.glob("*_dv_fixed_transformed.csv"))
    if not candidates:
        candidates = sorted(src.glob("*_transformed.csv"))
    if not candidates:
        candidates = sorted(src.glob("*_dv_fixed_transformed.xlsx"))
    if not candidates:
        candidates = sorted(src.glob("*_transformed.xlsx"))
    if not candidates:
        raise FileNotFoundError(f"No transformed DV files found in {src}")
    return candidates[0]


def _load_tabular(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(path, engine="pyarrow")
        except (ImportError, ValueError):
            return pd.read_csv(path, low_memory=False)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, engine="openpyxl")
    raise ValueError(f"Unsupported input format: {path}")


def _column_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    total_records = len(df)
    for column in df.columns:
        series = df[column]
        nulls = int(series.isna().sum())
        metrics[column] = {
            "non_null": int(total_records - nulls),
            "nulls": nulls,
            "null_rate": float(nulls / total_records) if total_records else 0.0,
            "dtype": str(series.dtype),
        }
    return metrics


def _key_checks(df: pd.DataFrame) -> Dict[str, Any]:
    checks = {}
    keys = ["OffenseDate", "VictimRace", "VictimEthnicity", "FemaleVictim", "MaleVictim", "DayOfWeek"]
    for key in keys:
        checks[key] = {
            "present": key in df.columns,
            "sample": df[key].head(3).tolist() if key in df.columns else [],
        }
    return checks


def build_report(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "column_metrics": _column_metrics(df),
        "key_checks": _key_checks(df),
    }


def main(src=None, out=None) -> Path | None:
    src_path = Path(src) if src else DEFAULT_INPUT
    out_dir = Path(out) if out else DEFAULT_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        input_file = _select_input_file(src_path)
    except FileNotFoundError as exc:
        print(exc)
        return None

    df = _load_tabular(input_file)
    report = build_report(df)
    report_path = out_dir / "verify_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    print("=" * 80)
    print("VERIFICATION REPORT")
    print("=" * 80)
    print(f"Input file: {input_file}")
    print(f"Total records: {report['total_records']}")
    print(f"Total columns: {report['total_columns']}")
    print(f"Report saved to: {report_path}")
    print("=" * 80)

    return report_path


if __name__ == "__main__":
    main()
