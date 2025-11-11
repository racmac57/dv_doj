import pandas as pd


def test_yes_no_to_bool_mapping() -> None:
    df = pd.DataFrame({"YN": ["Y", "N", "Yes", "No", "y", "n"]})
    # replace with real mapper when present
    mapped = df["YN"].str.lower().isin(["y", "yes", "true", "t", "1"])
    assert mapped.tolist() == [True, False, True, False, True, False]

