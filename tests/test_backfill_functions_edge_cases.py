import numpy as np
import pandas as pd

from etl_scripts.backfill_dv import (
    CONFIG,
    backfill_cad,
    backfill_rms,
    clean_deaths,
    drop_empty_cols,
    flag_missing,
    validate_data,
)


def test_empty_inputs():
    dv = pd.DataFrame()
    result = flag_missing(dv.copy())
    assert result.empty
    assert "CN_Flag" in result.columns
    assert "VA_Flag" in result.columns

    rms = pd.DataFrame(columns=["Case Number"])
    cad = pd.DataFrame(columns=["ReportNumberNew"])
    result = backfill_rms(dv.copy(), rms)
    result = backfill_cad(result, cad)
    assert result.empty


def test_no_merge_matches():
    dv = pd.DataFrame([["99-999999", None, None]], columns=["CaseNumber", "OffenseDate", "Time"])
    rms = pd.DataFrame([["23-000001", "2023-01-01", "00:30:00"]], columns=["Case Number", "Incident Date", "Incident Time"])
    cad = pd.DataFrame([["23-000001", "01/01/2023 00:30"]], columns=["ReportNumberNew", "Time of Call"])

    result = backfill_rms(dv.copy(), rms)
    assert pd.isna(result.iloc[0]["OffenseDate"])
    assert pd.isna(result.iloc[0]["Time"])

    result = backfill_cad(result, cad)
    assert pd.isna(result.iloc[0]["OffenseDate"])


def test_officer_parsing_edge():
    dv = pd.DataFrame([["23-000001", None]], columns=["CaseNumber", "ReviewedBy"])
    rms = pd.DataFrame(
        [
            ["23-000001", None, None, None, None, "Officer"],
            ["23-000001", None, None, None, None, "P.O. 123"],
            ["23-000001", None, None, None, None, "Det. John 123 Doe"],
            ["23-000001", None, None, None, None, "P.O. John Doe"],
            ["23-000001", None, None, None, None, "P.O. J. Doe 123"],
        ],
        columns=["Case Number", "Incident Date", "Incident Time", "FullAddress", "Narrative", "Officer of Record"],
    )

    result = backfill_rms(dv.copy(), rms)
    values = result["ReviewedBy"].dropna().tolist()
    assert "123" in values


def test_time_parsing_failures():
    dv = pd.DataFrame(
        [
            ["23-000001", "25:00:00"],
            ["23-000002", "12:70:00"],
            ["23-000003", "abc"],
            ["23-000004", ""],
        ],
        columns=["CaseNumber", "Time"],
    )

    cad = pd.DataFrame(
        [
            ["23-000001", "01/01/2023 25:00"],
            ["23-000002", "invalid"],
        ],
        columns=["ReportNumberNew", "Time of Call"],
    )

    result = backfill_cad(dv.copy(), cad)
    assert pd.isna(result.iloc[0]["Time"])
    assert pd.isna(result.iloc[1]["Time"])
    assert pd.isna(result.iloc[2]["Time"])
    assert pd.isna(result.iloc[3]["Time"])


def test_age_and_death_extremes():
    df = pd.DataFrame(
        {
            "VictimAge": [-100, 0, 120, 121, np.nan, "abc"],
            "JuvDeaths_M": [-5, 0, 1, "x", np.nan, 0],
        }
    )
    result = clean_deaths(df.copy())
    result, issues, _ = validate_data(result, CONFIG)

    ages = list(result["VictimAge"])
    assert pd.isna(ages[0])
    assert ages[1] == 0
    assert ages[2] == 120
    assert pd.isna(ages[3])
    assert pd.isna(ages[4])
    assert pd.isna(ages[5])

    text = " ".join(issues)
    assert "VictimAge out of" in text
    assert "Negative JuvDeaths_M" in text


def test_drop_empty_and_sparse():
    df = pd.DataFrame({"A": [1, None, None], "B": [None, None, None], "C": [None, None, None], "D": [None, 2, None]})
    result = drop_empty_cols(df.copy())
    assert "B" not in result.columns
    assert "C" not in result.columns
    assert "A" in result.columns
    assert "D" in result.columns


def test_case_number_formats():
    df = pd.DataFrame(
        {
            "CaseNumber": [
                "23-000001",
                "2023-000001",
                "23-1",
                "23-ABCDEF",
                "",
                "  23-000001  ",
            ]
        }
    )
    _, _, metrics = validate_data(df.copy(), CONFIG)
    assert metrics["invalid_case_number_format"] == 5


def test_date_boundaries():
    df = pd.DataFrame({"OffenseDate": ["2022-12-31", "2023-01-01", "2025-12-31", "2026-01-01", "invalid", None]})
    _, _, metrics = validate_data(df.copy(), CONFIG)
    assert metrics["invalid_offense_date"] == 2


def test_race_ethnicity_nulls():
    df = pd.DataFrame({"VictimRace": ["W", "B", None, "", "U", "Z"], "VictimEthnicity": ["H", "NH", None, "", "H", "X"]})
    _, _, metrics = validate_data(df.copy(), CONFIG)
    assert metrics["invalid_victim_race"] == 1
    assert metrics["invalid_victim_ethnicity"] == 1


def test_duplicate_resolution():
    dv = pd.DataFrame(
        [
            ["23-000001", "2023-01-01", 25],
            ["23-000001", "2023-01-02", 30],
            ["23-000002", "2023-01-03", 35],
        ],
        columns=["CaseNumber", "OffenseDate", "VictimAge"],
    )
    rms = pd.DataFrame([["23-000001", "2023-01-05"]], columns=["Case Number", "Incident Date"])
    result = backfill_rms(dv.copy(), rms)
    merged = result[result["CaseNumber"] == "23-000001"]
    assert len(merged) == 2
    assert merged.iloc[0]["OffenseDate"] == "2023-01-01"
    assert merged.iloc[0]["Incident Date"] == "2023-01-05"


def test_cad_time_parsing():
    cad = pd.DataFrame(
        [
            ["23-000001", "01/01/2023 00:30"],
            ["23-000002", "2023-01-02T14:22:10"],
            ["23-000003", "invalid"],
        ],
        columns=["ReportNumberNew", "Time of Call"],
    )
    dv = pd.DataFrame([["23-000001", None], ["23-000002", None], ["23-000003", None]], columns=["CaseNumber", "Time"])
    result = backfill_cad(dv.copy(), cad)
    assert pd.to_timedelta(result.iloc[0]["Time"]).total_seconds() == 1800
    assert pd.to_timedelta(result.iloc[1]["Time"]).total_seconds() == 51730
    assert pd.isna(result.iloc[2]["Time"])


def test_validate_empty():
    df = pd.DataFrame()
    _, issues, metrics = validate_data(df.copy(), CONFIG)
    assert metrics["total_records"] == 0
    assert metrics["total_issues"] == 0
    assert "VALIDATION SUMMARY" in issues[-3]


def test_rms_in_place_backfill():
    dv = pd.DataFrame(
        [
            ["23-000001", None, None, None, None],
            ["23-000002", "2023-01-02", None, None, None],
        ],
        columns=["CaseNumber", "OffenseDate", "Time", "FullAddress", "Narrative"],
    )
    rms = pd.DataFrame(
        [
            ["23-000001", "2023-01-01", "00:30:00", "100 Main St", "Domestic dispute"],
            ["23-000002", "2023-01-02", "14:22:10", "200 Elm St", "Follow-up"],
        ],
        columns=["Case Number", "Incident Date", "Incident Time", "FullAddress", "Narrative"],
    )

    result = backfill_rms(dv.copy(), rms)
    r0 = result.iloc[0]
    assert r0["OffenseDate"] == "2023-01-01"
    assert pd.to_timedelta(r0["Time"]).total_seconds() == 1800
    assert r0["FullAddress"] == "100 Main St"
    assert r0["Narrative"] == "Domestic dispute"

    r1 = result.iloc[1]
    assert r1["OffenseDate"] == "2023-01-02"
    assert pd.to_timedelta(r1["Time"]).total_seconds() == 51730
    assert r1["FullAddress"] == "200 Elm St"
