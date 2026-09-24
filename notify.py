#!/usr/bin/env python3
"""
Send a daily heating oil price update to a phone via ntfy (https://ntfy.sh).

Reads irving_oil_prices.csv and posts the latest price plus the change over
the previous 1, 7 and 30 days to the ntfy topic in the NTFY_TOPIC env var.
If NTFY_TOPIC is not set, nothing is sent.

Optional env vars:
  NTFY_SERVER  ntfy server (default https://ntfy.sh)
  NTFY_TOKEN   access token, for reserved topics or self-hosted servers
  SITE_URL     page opened when the notification is tapped

Usage:
  python notify.py            # send
  python notify.py --dry-run  # print the message instead
"""

import csv
import json
import os
import sys
import urllib.request
from datetime import date, timedelta

CSV_FILE = 'irving_oil_prices.csv'
DEFAULT_SITE_URL = 'https://chrowe.github.io/log-heating-oil-price/'
PERIODS = [(1, '1 day'), (7, '7 days'), (30, '30 days')]


def read_prices(path=CSV_FILE):
    with open(path, newline='') as f:
        rows = [(date.fromisoformat(r['date']), float(r['price']))
                for r in csv.DictReader(f) if r.get('price')]
    return sorted(rows)


def price_on_or_before(rows, day):
    """Latest price recorded on or before `day` (the CSV has gaps)."""
    match = None
    for d, p in rows:
        if d > day:
            break
        match = p
    return match


def arrow(change):
    if change > 0:
        return '▲'
    if change < 0:
        return '▼'
    return '–'


def format_change(current, previous):
    change = current - previous
    pct = change / previous * 100 if previous else 0
    return f'{arrow(change)} ${abs(change):.3f} ({pct:+.1f}%)', change


def build_message(rows):
    """Return (title, body, tag) for the latest price in `rows`."""
    today, current = rows[-1]

    # 1 day compares against the previous entry, whatever its date.
    lines = []
    day_change = None
    if len(rows) > 1:
        text, day_change = format_change(current, rows[-2][1])
        lines.append(f'1 day: {text}')
    for days, label in PERIODS[1:]:
        previous = price_on_or_before(rows, today - timedelta(days=days))
        if previous is not None:
            text, _ = format_change(current, previous)
            lines.append(f'{label}: {text}')

    title = f'Heating oil: ${current:.3f}/gal'
    if day_change is not None:
        title += f' ({arrow(day_change)} ${abs(day_change):.3f})'

    if not day_change:
        tag = 'heavy_minus_sign'
    elif day_change > 0:
        tag = 'chart_with_upwards_trend'
    else:
        tag = 'chart_with_downwards_trend'

    return title, '\n'.join(lines), tag


def send(title, body, tag):
    # JSON publishing keeps the non-ASCII arrows out of HTTP headers.
    server = os.environ.get('NTFY_SERVER') or 'https://ntfy.sh'
    payload = {
        'topic': os.environ['NTFY_TOPIC'],
        'title': title,
        'message': body,
        'tags': [tag],
        'click': os.environ.get('SITE_URL') or DEFAULT_SITE_URL,
    }
    headers = {'Content-Type': 'application/json'}
    token = os.environ.get('NTFY_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(server.rstrip('/'),
                                 data=json.dumps(payload).encode('utf-8'),
                                 headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f'ntfy responded {resp.status}')


def main(argv):
    title, body, tag = build_message(read_prices())
    if '--dry-run' in argv:
        print(title)
        print(body)
        return
    if not os.environ.get('NTFY_TOPIC'):
        print('NTFY_TOPIC not set; skipping notification')
        return
    send(title, body, tag)


if __name__ == '__main__':
    main(sys.argv[1:])
