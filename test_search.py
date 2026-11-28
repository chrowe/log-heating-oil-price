from datetime import date, datetime, timezone

from search import local_today


def test_local_today_after_midnight_utc():
    # A late run on the evening of Nov 26 in Vermont (#14)
    now = datetime(2026, 11, 27, 1, 7, tzinfo=timezone.utc)
    assert local_today(now) == date(2026, 11, 26)


def test_local_today_after_midnight_utc_in_summer():
    # EDT is UTC-4
    now = datetime(2026, 7, 2, 3, 30, tzinfo=timezone.utc)
    assert local_today(now) == date(2026, 7, 1)


def test_local_today_same_day():
    now = datetime(2026, 11, 27, 19, 4, tzinfo=timezone.utc)
    assert local_today(now) == date(2026, 11, 27)
