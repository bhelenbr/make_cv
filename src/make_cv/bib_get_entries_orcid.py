#!/usr/bin/env python3
import json
import os
import re
import string
import argparse
from datetime import date
import sys
import time
import chromedriver_autoinstaller
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser
from bibtexautocomplete.core import main as btac

from .bib_add_keywords import add_keyword


def getyear(paperbibentry):
    if "year" in paperbibentry.keys():
        return int(paperbibentry["year"])
    if "date" in paperbibentry.keys():
        return int(paperbibentry["date"][:4])
    return 0


def get_entries_from_orcid(orcid,years):

    orcid_url = "https://orcid.org/" + orcid

    # Set starting year for search
    if years > 0:
        today = date.today()
        year = today.year
        begin_year = year - years
    else:
        begin_year = 0

    # Set up Chrome options to run headlessly
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")

    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(orcid_url)

    # Wait for the page to load (you might need to adjust the sleep time)
    time.sleep(5)  # Wait for 5 seconds
    wait = WebDriverWait(driver, 10)

    # Find all panel elements
    panel_elements = driver.find_elements(By.CSS_SELECTOR, 'app-panel[panelid="work-stack"]')

    # A list to store the data
    orcid_entries = []
    year_pattern = r'\d{4}'

    # Loop through each panel element and extract the corresponding information
    for panel_element in panel_elements:
        # Find the title element
        title_element = panel_element.find_element(By.CSS_SELECTOR, 'h4.work-title.orc-font-body.ng-star-inserted')
        title_text = title_element.text.strip()

        # Find the journal name element
        journal_element = panel_element.find_element(By.CSS_SELECTOR, 'div.general-data.ng-star-inserted')
        journal_name = journal_element.text.strip()

        # Extract year (assuming it's inside another general-data div with year info)
        year_elements = panel_element.find_elements(By.CSS_SELECTOR, 'div.general-data')

        # Try to find a matching year
        year = None
        for year_element in year_elements:
            text = year_element.text.strip()
            if re.match(year_pattern, text):
                match_year = re.search(r'\d+', text)
                year = int(match_year.group())
                break  # Once we find the correct year, stop
        if year<begin_year:
            break
        # Find the DOI element
        doi_element = panel_element.find_element(By.CSS_SELECTOR, 'a.underline.ng-star-inserted')
        doi = doi_element.get_attribute('href')

        # Store the data in a dictionary
        entry = {
            "title": title_text,
            "journal": journal_name,
            "year": year,
            "doi": doi
        }
        orcid_entries.append(entry)

    # Close the WebDriver
    driver.quit()
    return orcid_entries


def bib_get_entries_orcid(bibfile, orcid, years, outputfile):
    newentries = []

    # Load bibfile
    tbparser = BibTexParser(common_strings=True)
    tbparser.homogenize_fields = False
    tbparser.alt_dict['url'] = 'url'  # Prevents change 'url' to 'link'
    tbparser.expect_multiple_parse = True

    with open(bibfile) as bibtex_file:
        bibtex_str = bibtex_file.read()

    bib_database = bibtexparser.loads(bibtex_str, tbparser)
    entries = bib_database.entries

    # Set arguments for btac
    sys.argv.clear()
    sys.argv.extend(['', '-i', '-f', '-m', 'btac.bib'])

    orcid_entries = get_entries_from_orcid(orcid,years)

    # Loop through ORCID entries
    for pub in orcid_entries:
        if 'year' not in pub:
            continue

        year = pub['year']
        journal=pub['journal']

        # Match by title
        title = pub['title']
        index = next((i for i, d in enumerate(entries) if d.get('title') == title), None)
        if index is None:
            continue
        
        if (year and entries[index]['year']!=str(year)) or (journal and entries[index]['journal']!=journal):
            continue

        print('Should I try to complete this record using BibTeX autocomplete:')
        print(pub['title'])

        YN = input('Y/N? ')
        if YN.upper() != 'Y':
            continue

        # Try to fill entry using BibTeX autocomplete
        with open('btac.bib', 'w') as tempfile:
            tempfile.write(f"@article{{title={{'{pub['title']}'}}}}")

        btac()
        with open('btac.bib') as bibtex_file:
            bibtex_str = bibtex_file.read()

        bib_database = bibtexparser.loads(bibtex_str, tbparser)
        if 'booktitle' in bib_database.entries[-1].keys():
            bib_database.entries[-1]['ENTRYTYPE'] = 'inproceedings'
        elif 'note' in bib_database.entries[-1].keys():
            bib_database.entries[-1]['ENTRYTYPE'] = 'misc'
        print(BibTexWriter()._entry_to_bibtex(bib_database.entries[-1]))

        YN = input('Is this BTAC entry correct and ready to be added? [Y/N]? ')
        if YN.upper() == 'Y':
            add_keyword(bib_database.entries[-1])
            if 'author' in bib_database.entries[-1].keys():
                IDstring = re.search('^[A-z]+', bib_database.entries[-1]['author']).group(0)
                IDstring += str(year)
                IDstring += re.search('^[A-z]+', bib_database.entries[-1]['title']).group(0)
                bib_database.entries[-1]['ID'] = IDstring
                newentries.append(bib_database.entries[-1]['ID'])
            else:
                print('Skipped entry because it had no author field')

    writer = BibTexWriter()
    writer.order_entries_by = None
    with open(outputfile, 'w') as thebibfile:
        bibtex_str = bibtexparser.dumps(bib_database, writer)
        thebibfile.write(bibtex_str)

    for file in ['dump.text', 'btac.bib']:
        try:
            os.remove(file)
        except OSError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script adds citation counts to a BibTeX file.')
    parser.add_argument('-o', '--output', default="scholarship1.bib", help='The name of the output file.')
    parser.add_argument('-y', '--years', default=1, type=int, help='Number of years to go back, default is 1 year.')
    parser.add_argument('bibfile', help='The .bib file to add citations to.')
    parser.add_argument('-oid', '--orcid', default="", help='The ORCID for the author.')
    args = parser.parse_args()

    bib_get_entries_orcid(args.bibfile, args.orcid, args.years, args.output)





