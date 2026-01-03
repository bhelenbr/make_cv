#!/usr/bin/env python3
import json
import os
from scholarly import scholarly
from scholarly import ProxyGenerator

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser
from bibtexautocomplete.core import main as btac


import re
import string
import argparse
from datetime import date
import sys

from .bib_add_keywords import add_keyword
from .bib_get_entries_orcid import make_bibtex_id_list


from bs4 import BeautifulSoup
import requests

from . import global_prefs

# copied from http://myhttpheader.com
myRequestHeader = {
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
'Accept-Language':'en-US,en;q=0.9',
'Accept-Encoding':'gzip, deflate, br',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# pip3 install scholarly
# pip3 uninstall urllib3
# pip3 install 'urllib3<=2'

def process_entry(paperbibentry,pub_id,year):
	if 'booktitle' in paperbibentry.keys():
		paperbibentry['ENTRYTYPE'] = 'inproceedings'
	elif 'note' in paperbibentry.keys():
		paperbibentry['ENTRYTYPE'] = 'misc'
	paperbibentry['google_pub_id'] = pub_id
	add_keyword(paperbibentry)
	IDstring = re.search('^[A-z]+', paperbibentry['author']).group(0)
	IDstring += year
	hasletter = re.search('^[A-z]+', paperbibentry['title'])
	if hasletter:
		IDstring += re.search('^[A-z]+', paperbibentry['title']).group(0)
	paperbibentry['ID'] = IDstring

def getyear(paperbibentry):
	if "year" in paperbibentry.keys(): 
		return int(paperbibentry["year"])
	if "date" in paperbibentry.keys():
		return int(paperbibentry["date"][:4])
	return 0

def bib_get_entries(bibfile, author_id, years, outputfile, scraper_id=None):
	
	# Set up a ProxyGenerator object to use free proxies
	# This needs to be done only once per session
	# Helps avoid Google Scholar locking out 
	if scraper_id:
		pg = ProxyGenerator()
		success = pg.ScraperAPI(scraper_id)
		if success:
			print('ScraperAPI in use')
			scholarly.use_proxy(pg)
		
	# Get Google Scholar Data for Author	
	author = scholarly.search_author_id(author_id)
	author = scholarly.fill(author, sections=['indices', 'publications'])

	# Set starting year for search
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0
		
	# Load bibfile
	tbparser = BibTexParser(common_strings=True)
	tbparser.alt_dict['url'] = 'url'	# this prevents change 'url' to 'link'
	tbparser.expect_multiple_parse = True
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file, tbparser)
	entries = bib_database.entries
	
	bib_entry_ids = make_bibtex_id_list(bibfile)
	
	
	# Create list of titles in bibfile compressing out nonalphanumeric characters
	titles = [re.sub('[\\W_]', '', entry['title']).lower() if 'title' in entry.keys() else None for entry in entries]
	# Create list of google publication ids if they exist
	google_pub_ids = [entry["google_pub_id"] if "google_pub_id" in entry.keys() else None for entry in entries]
	
	# Loop through Google Scholar entries
	for pub in author['publications']:
		if 'pub_year' in pub['bib']:
			year = pub['bib']['pub_year']
		else:
			continue
		
		if not(int(year) >= begin_year):
			continue
		
		# Skip if matching publication id
		au_pub_id = pub['author_pub_id']
		pub_id = au_pub_id[au_pub_id.find(':') + 1:]
		if pub_id in google_pub_ids:
			continue
			
		################  Using bibtex autocomplete ########################
		print('Trying to complete this record using bibtex autocomplete:')
		try:
			print(pub['bib']['citation'] + ' ' + pub['bib']['title'])
		except KeyError:
			print(pub['bib']['title'])
		
		# try to fill entry using bibtex autocomplete?
		with open('btac.bib', 'w',encoding='utf-8') as tempfile:
			tempfile.write('@article{' + pub_id + ',\n title={' + pub['bib']['title'] + '},\n}')
		btac(['-s','-i','-f','-m','btac.bib'])
		
		with open('btac.bib',encoding='utf-8') as bibtex_file:
			bibtex_str = bibtex_file.read()
		
		if bibtex_str.find('author') > -1  and bibtex_str.find('title') > -1:
			year_match = re.search(r'year\s*=\s*{(\d+)}', bibtex_str)
			title_match = re.search(r'(?:,|\n)\s*title\s*=\s*{(.+?)},', bibtex_str)
			doi_match = re.search(r'(?:,|\n)\s*doi\s*=\s*{(.+?)},', bibtex_str)
			
			if doi_match:
				doi = doi_match.group()
				if any(doi.lower() == entry_doi for _, entry_doi in bib_entry_ids):
					continue

			# Skip if matching title/date string
			title_id = ''.join(word.lower() for word in title_match.group().split() if (word.isalpha()  and word.isascii()))
			title_id += year
			if any(title_id == entry_title_id for entry_title_id, _ in bib_entry_ids):
				if doi is None:
					continue
			
			bibtex_str = re.sub("&amp;", "\\&", bibtex_str)
			bibtex_str = re.sub(" #", "\\#", bibtex_str)
			bib_database = bibtexparser.loads(bibtex_str, tbparser)
			print(BibTexWriter()._entry_to_bibtex(bib_database.entries[-1]))
			YN = 'Y'
			if not global_prefs.quiet:
				YN = input('Is this entry correct and ready to be added?\nOnce an entry is added any changes must be done manually.\n[Y/N]?')
			if YN.upper() == 'Y':
				process_entry(bib_database.entries[-1],pub_id,year)
				continue
			else:
				bib_database.entries.pop()
		else:
			print('BibTeX Autocomplete failed: missing author or title')
		
		##################  Using Google Scholar #############################
		if global_prefs.scrapeGoogle:
			print('Trying to complete this record using Google Scholar (This gets blocked a lot):')
			pub_filled = scholarly.fill(pub)		
			if 'url_related_articles' in pub_filled.keys():
				scholar_id = pub_filled['url_related_articles'].split("q=related:")[1].split(":")[0]
				output_query = f"https://scholar.google.com/scholar?hl=en&q=info:{scholar_id}:scholar.google.com/&output=cite&scirp=0&hl=en"
				response = requests.get(output_query,headers=myRequestHeader)
				soup = BeautifulSoup(response.content, 'html.parser')
				# Find link to BibTeX
				a_tag = soup.find("a", class_="gs_citi")
				if a_tag and a_tag.get("href"):
					bibtex_url = a_tag["href"]
				elif scraper_id:
					payload = { 'api_key': scraper_id, 'url': output_query}
					response = requests.get('https://api.scraperapi.com/', params=payload)
					if a_tag and a_tag.get("href"):
						bibtex_url = a_tag["href"]
					else:
						print('Scraper got blocked: \n' +output_query)
						continue
				else:
					print('Google blocked request, try using a scraper id from www.scraperapi.com or just download entry from google scholar yourself from: \n' +output_query)
					continue
				
				# try to follow BibTeX link to get citation
				response = requests.get(bibtex_url,headers=myRequestHeader)
				if (response.text.find('Error 403 (Forbidden)') > -1):
					if scraper_id:
						payload = { 'api_key': scraper_id, 'url': bibtex_url}
						response = requests.get('https://api.scraperapi.com/', params=payload)
						if (response.text.find('Error 403 (Forbidden)') > -1) and scraper_id:
							print('Scraper got blocked: ' +bibtex_url)
							continue
					else:
						print('Google blocked request, try using a scraper id from www.scraperapi.com or just download entry from google scholar yourself from: \n' +bibtex_url)
						continue				
				
				# Process response
				bibtex_str = response.text
				print(bibtex_str)
				YN = 'Y'
				if not global_prefs.quiet:
					YN = input('Is this entry correct and ready to be added?\nOnce an entry is added any changes must be done manually.\n[Y/N]?')
				if YN.upper() == 'Y':
					bib_database = bibtexparser.loads(bibtex_str, tbparser)
					process_entry(bib_database.entries[-1],pub_id,year)				
					continue
	
	writer = BibTexWriter()
	writer.order_entries_by = None
	with open(outputfile, 'w',encoding='utf-8') as thebibfile:
		bibtex_str = bibtexparser.dumps(bib_database, writer)
		thebibfile.write(bibtex_str)
	
	for file in ['dump.text', 'btac.bib']:
		try:
			os.remove(file)
		except OSError as err:
			print("")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script adds citations counts to a bib file')
	parser.add_argument('-o', '--output',default="scholarship1.bib",help='the name of the output file')
	parser.add_argument('-y', '--years',default="1",type=int,help='the number of years to go back, default is 1 year')
	parser.add_argument('bibfile',help='the .bib file to add the citations to')
	parser.add_argument('-a', '--author_id',default="",help='the Google Scholar id for the author. If not provided it will look for a file titled "google_id" in the current working directory')
	parser.add_argument('-s', '--scraperID',help='A scraper ID in case Google Scholar is blocking requests')		  
	args = parser.parse_args()
	
	if (not args.author_id):
		with open("google_id") as google_file:
			args.author_id = google_file.readline().strip('\n\r')
		
	bib_get_entries(args.bibfile,args.author_id,args.years,args.output,args.scraperID)