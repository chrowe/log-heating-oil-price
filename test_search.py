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


# One set of rows per day (#15)

from search import save_dealer_rows, save_irving_price


def write(path, lines):
    path.write_bytes(''.join(l + '\r\n' for l in lines).encode())


def lines(path):
    return path.read_bytes().decode().split('\r\n')[:-1]


def test_second_run_same_day_replaces_irving_price(tmp_path):
    csv = tmp_path / 'irving.csv'
    write(csv, ['date,price', '2026-11-25,4.6481', '2026-11-27,4.3965'])
    save_irving_price('2026-11-27', 4.402, path=csv)
    assert lines(csv) == ['date,price', '2026-11-25,4.6481', '2026-11-27,4.402']


def test_second_run_same_day_replaces_dealer_rows(tmp_path):
    csv = tmp_path / 'dealers.csv'
    write(csv, [
        'date,zip,dealer,gallons,price',
        '2026-11-27,05048,Irving Oil,300 gallons,4.3965',
        '2026-11-27,05602,Irving Oil,300 gallons,4.3965',
        '2026-11-27,05602,Gone Fuels,300 gallons,4.9',
    ])
    save_dealer_rows([['2026-11-27', '05602', 'Irving Oil', '300 gallons', 4.402]],
                     '2026-11-27', '05602', path=csv)
    assert lines(csv) == [
        'date,zip,dealer,gallons,price',
        '2026-11-27,05048,Irving Oil,300 gallons,4.3965',  # other zip untouched
        '2026-11-27,05602,Irving Oil,300 gallons,4.402',
    ]


def test_old_duplicates_cleaned_up_last_written_wins(tmp_path):
    # The data on main on 2026-11-28: a duplicate Nov 27 and a Nov 28 row that
    # the old UTC code wrote on the evening of Nov 27 (#14).
    csv = tmp_path / 'irving.csv'
    write(csv, ['date,price', '2022-08-29,4.0040', '2022-08-29,4.4693', '2026-11-25,4.6481',
                '2026-11-27,4.3965', '2026-11-28,4.402', '2026-11-27,4.402'])
    save_irving_price('2026-11-28', 4.41, path=csv)
    assert lines(csv) == ['date,price', '2022-08-29,4.4693', '2026-11-25,4.6481',
                          '2026-11-27,4.402', '2026-11-28,4.41']
