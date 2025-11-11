"""
Integration Test Suite + Lightweight Benchmarks

Runs end-to-end on synthetic data, validates backfills, flags, and quality.
Uses pytest-benchmark for timing (optional).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

try:  # pragma: no cover - optional dependency
    import pytest_benchmark.plugin  # type: ignore
    _HAS_BENCHMARK = True
except ImportError:  # pragma: no cover
    _HAS_BENCHMARK = False

    @pytest.fixture(name="benchmark")
    def _dummy_benchmark_fixture():  # noqa: D401 - simple stub
        class DummyBenchmark:
            def __init__(self):
                class StatsData:
                    mean = 0.0

                class Stats:
                    stats = StatsData()

                self.stats = Stats()

            def __call__(self, func, *args, **kwargs):
                return func(*args, **kwargs)

        return DummyBenchmark()

from etl_scripts import backfill_dv


@pytest.fixture
def temp_env(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    out_dir = tmp_path / "processed_data"
    out_dir.mkdir()
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    dv = pd.DataFrame(
        [
            [
                "23-000001",
                "Hackensack",
                "2023-01-01",
                "00:30:00",
                None,
                25,
                "W",
                "NH",
                True,
                False,
                0,
                0,
                0,
                0,
            ],
            ["23-000002", "Hackensack", None, None, "klosk_j", None, None, None, False, True, 0, 0, 0, 0],
            ["invalid", "Bogota", "2020-01-01", "25:00:00", None, 150, "X", "X", False, False, -1, 0, 0, 0],
            [None, "Hackensack", "2024-06-15", "12:00:00", None, None, "B", "H", True, True, 0, 0, 0, 0],
            ["23-000001", "Hackensack", "2023-01-01", "01:00:00", None, 30, "B", "H", False, True, 0, 0, 0, 0],
            ["23-000003", "Hackensack", "2023-03-01", "14:22:00", None, 45, "A", "NH", True, False, 0, 0, 0, 0],
            ["23-000004", "Hackensack", "2025-12-31", "23:59:00", None, 60, "I", "H", False, True, 0, 0, 0, 0],
            ["23-000005", "Hackensack", "2026-01-01", "00:00:00", None, 18, "P", "NH", True, False, 0, 0, 0, 0],
            ["23-000006", "Hackensack", "2023-06-15", None, None, 35, "U", "H", False, True, 0, 0, 0, 0],
            ["23-000007", "Hackensack", None, "invalid", None, 200, "Z", "X", True, True, 0, 0, 0, 0],
        ],
        columns=[
            "CaseNumber",
            "Municipality",
            "OffenseDate",
            "Time",
            "ReviewedBy",
            "VictimAge",
            "VictimRace",
            "VictimEthnicity",
            "FemaleVictim",
            "MaleVictim",
            "JuvDeaths_M",
            "AdultDeaths_M",
            "AdultDeaths_F",
            "JuvDeaths_F",
        ],
    )
    dv_path = data_dir / "_2023_2025_10_31_dv_fixed_transformed_transformed.csv"
    dv.to_csv(dv_path, index=False)

    rms = pd.DataFrame(
        [
            ["23-000001", "2023-01-01", "00:30:00", "100 Main St", "Domestic dispute", "P.O. John Doe 123"],
            ["23-000002", "2023-01-02", "14:22:10", "200 Elm St", "Follow-up", "Det. Jane Smith 456"],
            ["23-000003", "2023-03-01", "14:22:00", "300 Oak St", "Assault", "P.O. Alex Kim 789"],
            ["23-000006", "2023-06-15", "10:30:00", "600 Pine St", "Harassment", "P.O. Sam Lee 101"],
            ["23-000009", "2023-09-01", "09:00:00", "900 Cedar St", "Non-DV", "P.O. Mike Tan 202"],
        ],
        columns=["Case Number", "Incident Date", "Incident Time", "FullAddress", "Narrative", "Officer of Record"],
    )
    rms_path = data_dir / "_2023_2025_10_31_dv_rms.csv"
    rms.to_csv(rms_path, index=False)

    cad = pd.DataFrame(
        [
            ["23-000001", "01/01/2023 00:30", "100 Main St", "Sunday"],
            ["23-000002", "01/02/2023 14:22", "200 Elm St", "Monday"],
            ["23-000004", "12/31/2025 23:59", "400 Birch St", "Wednesday"],
            ["23-000006", "06/15/2023 10:30", "600 Pine St", "Thursday"],
            ["23-000007", "invalid", "700 Maple St", "Friday"],
        ],
        columns=["ReportNumberNew", "Time of Call", "FullAddress2", "DayofWeek"],
    )
    cad_path = data_dir / "_2023_2025_10_31_dv_cad.csv"
    cad.to_csv(cad_path, index=False)

    env = {
        "dv": dv_path,
        "rms": rms_path,
        "cad": cad_path,
        "out": out_dir / "dv_final.csv",
        "logs": logs_dir,
        "processed_data": out_dir,
    }
    yield env


def patch_paths(monkeypatch: pytest.MonkeyPatch, paths: dict[str, Path]) -> None:
    monkeypatch.setattr(backfill_dv, "DEFAULT_DV", paths["dv"])
    monkeypatch.setattr(backfill_dv, "DEFAULT_RMS", paths["rms"])
    monkeypatch.setattr(backfill_dv, "DEFAULT_CAD", paths["cad"])
    monkeypatch.setattr(backfill_dv, "DEFAULT_OUT", paths["out"])
    monkeypatch.setattr(backfill_dv, "DEFAULT_LOG_DIR", paths["logs"])


def test_integration_suite(monkeypatch: pytest.MonkeyPatch, temp_env: dict[str, Path], benchmark):
    patch_paths(monkeypatch, temp_env)
    result_path = benchmark(backfill_dv.main)
    assert result_path == temp_env["out"]
    result = pd.read_csv(temp_env["out"])
    assert len(result) == 7
    assert result["CN_Flag"].sum() == 0
    assert result["VA_Flag"].sum() == 1

    r1 = result[result["CaseNumber"] == "23-000001"].iloc[0]
    assert r1["OffenseDate"] == "2023-01-01"
    assert pd.isna(r1["Time"])
    assert r1.get("ReviewedBy") in {"123", "123.0", None}
    assert r1["FullAddress"] == "100 Main St"
    assert "Domestic" in r1["Narrative"]

    r2 = result[result["CaseNumber"] == "23-000002"].iloc[0]
    assert r2["OffenseDate"] == "2023-01-02"
    assert pd.isna(r2["Time"])
    assert r2.get("DayOfWeek") in ("Mon", "Monday", None)

    r6 = result[result["CaseNumber"] == "23-000006"].iloc[0]
    assert r6["OffenseDate"] == "2023-06-15"
    assert pd.isna(r6["Time"])

    validation_path = temp_env["logs"] / "validation_report.txt"
    issues = validation_path.read_text()
    for text in [
        "Invalid VictimRace: 1",
        "Invalid VictimEthnicity: 1",
        "VictimAge out of [0-120]: 2",
        "OffenseDate outside",
        "Invalid Time format: 7",
    ]:
        assert text in issues

    metrics_path = temp_env["logs"] / "quality_metrics.json"
    metrics = json.loads(metrics_path.read_text())
    assert "validation_time" in metrics
    metrics.pop("validation_time", None)
    assert metrics == {
        "total_records": 7,
        "missing_case_number": 0,
        "invalid_case_number_format": 0,
        "invalid_municipality": 0,
        "invalid_victim_race": 1,
        "invalid_victim_ethnicity": 1,
        "victim_age_out_of_range": 2,
        "invalid_offense_date": 1,
        "invalid_time": 7,
        "negative_juvdeaths_m": 0,
        "negative_adultdeaths_m": 0,
        "negative_adultdeaths_f": 0,
        "negative_juvdeaths_f": 0,
        "duplicate_case_numbers": 0,
        "total_issues": 5,
    }
    assert benchmark.stats.stats.mean < 2.0


def test_benchmark_only(monkeypatch: pytest.MonkeyPatch, temp_env: dict[str, Path], benchmark):
    patch_paths(monkeypatch, temp_env)
    benchmark(backfill_dv.main)
