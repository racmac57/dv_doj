from datetime import datetime


def _cascade(incident_date, between_date, report_date):
    return incident_date or between_date or report_date


def test_date_cascade_prefers_incident_date() -> None:
    a = datetime(2025, 11, 4)
    b = datetime(2025, 11, 5)
    c = datetime(2025, 11, 6)
    assert _cascade(a, b, c) == a


def test_date_cascade_uses_between_when_incident_missing() -> None:
    b = datetime(2025, 11, 5)
    c = datetime(2025, 11, 6)
    assert _cascade(None, b, c) == b


def test_date_cascade_falls_back_to_report_date() -> None:
    c = datetime(2025, 11, 6)
    assert _cascade(None, None, c) == c

