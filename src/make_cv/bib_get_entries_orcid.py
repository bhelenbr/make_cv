#!/usr/bin/env python3
import json
import os
import re
import string
import argparse
from datetime import date
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexautocomplete import BibtexAutocomplete

def parse_bibtex(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content into individual entries
    entries = re.split(r'\n@', content)
    parsed_entries = []

    for entry in entries:
        entry_dict = {}

        # Extract the title field
        title_match = re.search(r'(?:,|\n)\s*title\s*=\s*{(.+?)}', entry)
        if title_match:
            entry_dict['title'] = title_match.group(1)

        # Extract doi
        doi_match = re.search(r'doi\s*=\s*{(.+?)}', entry)
        if doi_match:
            entry_dict['doi']="https://doi.org/"
            entry_dict['doi']+= doi_match.group(1)
        else:
            entry_dict['doi'] = 'None'

        # Extract year
        year_match = re.search(r'year\s*=\s*{(\d+)}', entry)
        if year_match:
            entry_dict['year'] = year_match.group(1)

        # Only include entries with a title and year
        if 'title' in entry_dict and 'year' in entry_dict:
            parsed_entries.append(entry_dict)

    return parsed_entries


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
                match_type = re.search(r'\|\s*(.*)', text)
                if match_type:
                    type = match_type.group(1)  # Get the text after the '|'
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
            "year": str(year),
            "doi": doi,
            "type":type
        }
        orcid_entries.append(entry)

    # Close the WebDriver
    driver.quit()
    return orcid_entries

def bib_get_entries_orcid(bibfile, orcid, years, outputfile):

    bib_entries = parse_bibtex(bibfile)

    orcid_entries = get_entries_from_orcid(orcid,years)

    type_mapping = {
        'Conference paper': 'inproceedings',
        'Journal article': 'article',
        'Book': 'book',
        'Thesis': 'thesis',
        'Dissertation': 'thesis',
        'Report': 'techreport',
        'Book chapter': 'incollection',
        'Patent': 'patent',
        'Other': 'misc',
        # Add more mappings as needed
    }

    # Loop through ORCID entries
    for pub in orcid_entries:
        if 'year' not in pub:
            continue

        # Match by doi
        if pub['doi']:
            index = next((i for i, d in enumerate(bib_entries) if d.get('doi', '').lower() == pub['doi'].lower()), None)
        
        #Match by title if no match found
        if index is None:
            index = next((i for i, d in enumerate(bib_entries) if d.get('title', '').lower() == pub['title'].lower()), None)
            if index is not None:
                if not bib_entries[index]['year'] and pub['year']:
                    pass 
                elif (not pub['year'] or not bib_entries[index]['year'] or bib_entries[index]['year']==pub['year']):
                    continue
        else:
            continue
        
        try:
            type=type_mapping[pub['type']]
        except:
            type='misc'

        print('Should I try to complete this record using BibTeX autocomplete:')
        print(pub['title'])

        YN = input('Y/N? ')
        if YN.upper() != 'Y':
            continue

        citation_key=''.join(''.join(word for word in pub['title'].split() if word.isalpha()))+pub['year']

        # Construct the BibTeX entry as a string
        bibtex_entry = ""
        bibtex_entry += f'@{type}{{{citation_key},\n'
        if pub['year'] and pub['doi']:
            bibtex_entry += f'  title = {{{pub["title"]}}},\n'
            bibtex_entry += f'  year = {{{pub["year"]}}},\n'
            bibtex_entry += f'  doi = {{{pub["doi"]}}}\n'
        elif pub['year']:
            bibtex_entry += f'  title = {{{pub["title"]}}},\n'
            bibtex_entry += f'  year = {{{pub["year"]}}}\n'
        elif pub['doi']:
            bibtex_entry += f'  title = {{{pub["title"]}}},\n'
            bibtex_entry += f'  doi = {{{pub["doi"]}}}\n'
        else:
            bibtex_entry += f'  title = {{{pub["title"]}}}\n'
        bibtex_entry += '}\n'  # Close the entry

        # Try to fill entry using BibTeX autocomplete
        completer = BibtexAutocomplete()
        completer.load_string(bibtex_entry)
        completer.autocomplete()
        completer.write_file("btac.bib")

        with open('btac.bib', 'r') as src_file:
            bibtex_entry = src_file.read()

        print('Is this btac entry correct and ready to be added?\nOnce an entry is added any future changes must be done manually.')
        print(bibtex_entry)
        YN = input('Y/N? ')
        if YN.upper() != 'Y':
            continue

        with open(outputfile, 'a') as dest_file:  # Use 'a' to append
            dest_file.write(bibtex_entry)
        
        


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






