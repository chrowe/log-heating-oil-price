#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:46:00 2023

@author: Chris.Rowe
"""

from playwright.sync_api import Page, expect
from datetime import date
from csv import writer
import pytest


url = 'https://www.eastrise.com/personal/fuel-buying-program/'


    

ZIP_CODES = ['05048', '05602']
DEALER_CSV = 'oil_prices_by_dealer.csv'


@pytest.mark.parametrize('zip_code', ZIP_CODES)
def test_search_button_exists(page: Page, zip_code):
    page.goto(url)

    # create a locator
    search_button = page.get_by_role("main", name="Main site content").get_by_role("button", name="Search")

    # Expect an attribute "to be strictly equal" to the value.
    expect(search_button).to_have_attribute("type", "submit")

    page.get_by_label("Zip Code").fill(zip_code)

    page.get_by_role("group", name="Fuel Type(s)").get_by_text("oil").click()

    search_button.click()

    dealers = page.locator("#vheat-find-a-dealer-root div.co-dealer")
    expect(dealers.first).to_be_visible()

    today = date.today().strftime('%Y-%m-%d')
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

    print(rows)
    assert rows, f"no oil prices found for {zip_code}"

    with open(DEALER_CSV, 'a', newline='') as f_object:
        writer(f_object).writerows(rows)

    # Keep the original Irving series (home zip code) going
    if zip_code == ZIP_CODES[0]:
        irving = [r for r in rows if r[2] == 'Irving Oil']
        assert irving, "Irving Oil not listed"
        with open('irving_oil_prices.csv', 'a') as f_object:
            writer(f_object).writerow([today, irving[0][4]])
