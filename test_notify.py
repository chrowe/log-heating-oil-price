from datetime import date

from notify import build_message, read_prices


def test_read_prices_keeps_last_row_per_date(tmp_path):
    # Same-day rows used to sort by price, so 4.402 could lose to 4.3965 (#15).
    csv = tmp_path / 'irving.csv'
    csv.write_text('date,price\n2026-11-25,4.6481\n2026-11-27,4.402\n2026-11-27,4.3965\n')
    assert read_prices(csv) == [(date(2026, 11, 25), 4.6481), (date(2026, 11, 27), 4.3965)]


def test_one_day_change_is_not_within_a_day(tmp_path):
    csv = tmp_path / 'irving.csv'
    csv.write_text('date,price\n2026-11-25,4.6481\n2026-11-27,4.3965\n2026-11-27,4.402\n')
    _, body, _ = build_message(read_prices(csv))
    assert body.splitlines()[0] == '1 day: ▼ $0.246 (-5.3%)'
