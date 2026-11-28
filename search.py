#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:46:00 2023

@author: Chris.Rowe

Scrapes heating oil prices from the Eastrise fuel buying program, one pytest
test per zip code.

The page's HTML already holds every dealer's prices as JSON, so each run first
downloads the page and reads that (#50). If anything about the JSON looks
wrong, the run falls back to driving the page with Playwright. Each run adds a
line to scrape_log.csv saying which source was used.

Set SCRAPE_SOURCE to force one path:
  SCRAPE_SOURCE=json        JSON only; fail instead of falling back
  SCRAPE_SOURCE=playwright  skip the JSON step
"""

from playwright.sync_api import Page, expect
from datetime import date
from csv import writer
import json
import os
import time
import urllib.request
import pytest


url = 'https://www.eastrise.com/personal/fuel-buying-program/'
ZIP_CODES = ['05048', '05602']
DEALER_CSV = 'oil_prices_by_dealer.csv'
SCRAPE_LOG = 'scrape_log.csv'
JSON_VAR = 'vsecuVheatDealers'
# Prices outside this range mean the JSON is wrong, not that oil is that price.
PRICE_RANGE = (1.0, 15.0)
DOWNLOAD_ATTEMPTS = 3


class JsonError(Exception):
    """The JSON step failed; the message says why."""


@pytest.fixture(scope='session')
def today():
    """The date for every row and log line in this run (both paths)."""
    return date.today().strftime('%Y-%m-%d')


def download_page():
    # Cloudflare rejects urllib's default User-Agent (error 1010).
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt == DOWNLOAD_ATTEMPTS:
                raise JsonError(f'download failed after {attempt} attempts: {e}')
            time.sleep(5 * attempt)


def parse_dealers(html, var=JSON_VAR):
    marker = f'var {var} = '
    start = html.find(marker)
    if start == -1:
        raise JsonError(f'variable {var} not found')
    try:
        dealers, _ = json.JSONDecoder().raw_decode(html, start + len(marker))
    except json.JSONDecodeError as e:
        raise JsonError(f'JSON did not parse: {e}')
    if not isinstance(dealers, list):
        raise JsonError(f'{var} is not a list')
    return dealers


def rows_for_zip(dealers, zip_code):
    """[zip, dealer, gallons, price] rows, matching what the Playwright path keeps."""
    rows = []
    for dealer in dealers:
        for fuel in dealer.get('fuel_data') or []:
            # ZIP+4 entries such as 05602-3541 count for 05602.
            zips = {z.split('-')[0].strip() for z in fuel.get('zip_codes_serviced') or []}
            if zip_code not in zips:
                continue
            for p in fuel.get('prices') or []:
                # The label is what the page shows in the fuel column, which
                # the Playwright path filters on.
                if not str(p.get('fuel_type_label', '')).strip().lower().startswith('oil'):
                    continue
                try:
                    price = float(p['vheat_price'])
                except (KeyError, TypeError, ValueError):
                    # e.g. "Contact Bournes"
                    continue
                rows.append([zip_code, dealer['name'].strip(), p['gallons'].strip(), price])
    return rows


def check_rows(rows_by_zip):
    for zip_code, rows in rows_by_zip.items():
        if not rows:
            raise JsonError(f'no oil prices for {zip_code}')
        for _, dealer, _, price in rows:
            if not PRICE_RANGE[0] <= price <= PRICE_RANGE[1]:
                raise JsonError(f'{dealer} price {price} for {zip_code} is outside {PRICE_RANGE}')
    if not any(r[1] == 'Irving Oil' for r in rows_by_zip[ZIP_CODES[0]]):
        raise JsonError(f'Irving Oil not listed for {ZIP_CODES[0]}')


def json_rows():
    """{zip: rows} for every zip in ZIP_CODES, or raise JsonError."""
    dealers = parse_dealers(download_page())
    try:
        rows_by_zip = {z: rows_for_zip(dealers, z) for z in ZIP_CODES}
    except (AttributeError, KeyError, TypeError) as e:
        raise JsonError(f'unexpected dealer data: {e!r}')
    check_rows(rows_by_zip)
    return rows_by_zip


def log_source(day, source, detail=''):
    new = not os.path.exists(SCRAPE_LOG)
    with open(SCRAPE_LOG, 'a', newline='') as f:
        w = writer(f)
        if new:
            w.writerow(['date', 'source', 'detail'])
        w.writerow([day, source, detail])


@pytest.fixture(scope='session')
def json_prices(today, pytestconfig):
    """Run the JSON step once per run. Returns {zip: rows}, or None to fall back."""
    forced = os.environ.get('SCRAPE_SOURCE', '').strip().lower()
    if forced == 'playwright':
        log_source(today, 'playwright', 'forced by SCRAPE_SOURCE')
        return None
    try:
        rows_by_zip = json_rows()
    except JsonError as e:
        if forced == 'json':
            pytest.fail(f'JSON step failed: {e}')
        log_source(today, 'playwright', f'JSON: {e}')
        # pytest captures output, which would hide the warning from Actions.
        capture = pytestconfig.pluginmanager.getplugin('capturemanager')
        with capture.global_and_fixture_disabled():
            print(f'::warning::Falling back to Playwright (JSON: {e})', flush=True)
        return None
    log_source(today, 'json')
    return rows_by_zip


def scrape_with_playwright(page: Page, zip_code, today):
    page.goto(url)

    # Fails early if the Eastrise page layout changes. The page sometimes takes
    # longer than Playwright's 5-second default to load (#48), so wait longer here.
    search_button = page.get_by_role("main", name="Main site content").get_by_role("button", name="Search")
    expect(search_button).to_have_attribute("type", "submit", timeout=30_000)

    page.get_by_label("Zip Code").fill(zip_code)

    page.get_by_role("group", name="Fuel Type(s)").get_by_text("oil").click()

    search_button.click()

    dealers = page.locator("#vheat-find-a-dealer-root div.co-dealer")
    expect(dealers.first).to_be_visible()

    rows = []
    for dealer in dealers.all():
        name = dealer.locator("h3.co-dealer--name").inner_text().strip()
        for tr in dealer.locator("div.co-dealer--pricing tbody tr").all():
            fuel, gallons, price = [td.strip() for td in tr.locator("td").all_inner_texts()]
            if not fuel.lower().startswith('oil'):
                continue
            try:
                price = float(price)
            except ValueError:
                # e.g. "Contact Bournes"
                continue
            rows.append([today, zip_code, name, gallons, price])
    return rows


@pytest.mark.parametrize('zip_code', ZIP_CODES)
def test_scrape_prices(request, json_prices, today, zip_code):
    if json_prices is not None:
        rows = [[today] + r for r in json_prices[zip_code]]
    else:
        # Only start a browser when falling back.
        rows = scrape_with_playwright(request.getfixturevalue('page'), zip_code, today)

    print(rows)
    assert rows, f"no oil prices found for {zip_code}"

    # Check before writing anything, so a failed test that gets rerun
    # (--reruns in run.yml) doesn't leave half-written rows behind.
    if zip_code == ZIP_CODES[0]:
        irving = [r for r in rows if r[2] == 'Irving Oil']
        assert irving, "Irving Oil not listed"

    with open(DEALER_CSV, 'a', newline='') as f_object:
        writer(f_object).writerows(rows)

    # Keep the original Irving series (home zip code) going
    if zip_code == ZIP_CODES[0]:
        with open('irving_oil_prices.csv', 'a') as f_object:
            writer(f_object).writerow([today, irving[0][4]])
