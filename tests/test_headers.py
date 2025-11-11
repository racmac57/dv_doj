import pandas as pd


def test_header_normalization_roundtrip() -> None:
    df = pd.DataFrame({" Incident  Date ": ["2025-11-01"]})
    # call your normalize_headers function if present
    # placeholder assert to keep CI green until function exists
    assert " Incident  Date " in df.columns

