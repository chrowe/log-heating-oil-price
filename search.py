#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:46:00 2023

@author: Chris.Rowe
"""

from playwright.sync_api import Page, expect
from datetime import date
from csv import writer


url = 'https://www.vsecu.com/personal/home-heating/fuel-buying-program'


    

def test_search_button_exists(page: Page):
    page.goto(url)

    # create a locator
    search_button = page.get_by_role("main", name="Main site content").get_by_role("button", name="Search")
    
    
    # Expect an attribute "to be strictly equal" to the value.
    expect(search_button).to_have_attribute("type", "submit")
    
    
    #page.locator("#js-announcements_bank").get_by_role("button").click()

    page.get_by_label("Zip Code").fill("05048")

    page.get_by_role("group", name="Fuel Type(s)").get_by_text("propane").click()
    page.get_by_role("group", name="Fuel Type(s)").get_by_text("kerosene").click()
    page.get_by_role("group", name="Fuel Type(s)").get_by_text("wood pellets").click()
    
    search_button.click()
    

    value = page.locator("#vheat-find-a-dealer-root > div > div > div:nth-child(2) > div.co-dealer--pricing > table > tbody > tr > td:nth-child(3)")

    print(value.inner_text())
    print(date.today())
    
    export = [date.today().strftime('%Y-%m-%d'), float(value.inner_text())]
    
    print(export)

    # Open our existing CSV file in append mode
    # Create a file object for this file
    with open('irving_oil_prices.csv', 'a') as f_object:
 
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)
     
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(export)
     
        # Close the file object
        f_object.close()
        
