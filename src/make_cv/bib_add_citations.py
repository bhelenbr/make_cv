#!/usr/bin/env python3
import json
from scholarly import scholarly
from scholarly import ProxyGenerator

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser

import re
import string

import argparse

# pip3 install scholarly
# pip3 uninstall urllib3
# pip3 install 'urllib3<=2'



def bib_add_citations(bibfile,author_id,outputfile,scraper_id=None):

	# Set up a ProxyGenerator object to use free proxies
	# This needs to be done only once per session
	# Helps avoid google scholar locking out 
	if scraper_id:
		pg = ProxyGenerator()
		success = pg.ScraperAPI(scraper_id)
		if success:
			print('ScraperAPI in use')
			scholarly.use_proxy(pg)
		
	# Get Google Scholar Data for Author	
	author = scholarly.search_author_id(author_id)
	author = scholarly.fill(author,sections=['indices','publications'])

	# Load bibfile
	# homogenize_fields: Sanitize BibTeX field names, for example change `url` to `link` etc.
	tbparser = BibTexParser(common_strings=True)
	tbparser.homogenize_fields = False  # no dice
	tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file, tbparser)
	entries = bib_database.entries
	
	# Create list of titles in bibfile compressing out nonalphanumeric characters
	titles = [re.sub('[\\W_]', '', entry['title']).lower() if 'title' in entry.keys() else None for entry in entries]
	# Create list of google publication ids if they exist
	google_pub_ids = [entry["google_pub_id"] if "google_pub_id" in entry.keys() else None for entry in entries]
	
	# Loop through google scholar entries
	for pub in author['publications']:
		ncites = pub['num_citations']
		if int(ncites) < 1:
			continue

		# First try to match by publication id
		au_pub_id = pub['author_pub_id']
		pub_id = au_pub_id[au_pub_id.find(':')+1:]
		indices = [i for i, x in enumerate(google_pub_ids) if x == pub_id]
		if len(indices) == 1:
			# found match
			entries[indices[0]]['citations'] = str(ncites)
			continue
		
		# Try to match by title
		cite_title = re.sub('[\\W_]', '', pub['bib']['title']).lower()
		citestring = pub['bib']['citation']
		
		indices = [i for i, x in enumerate(titles) if x == cite_title]
		if len(indices) == 1:
			# found match
			entries[indices[0]]['citations'] = str(ncites)
			entries[indices[0]]['google_pub_id'] = str(pub_id)
			continue
			
		if len(indices) > 1:
			# try to match something else?
			# could try secondary matches with these
			# journal = re.search('^[A-z. ]+',citestring).group(0)
			# startpage = re.search('[0-9]+-',citestring).group(0)
			# startpage = startpage[:len(startpage)-1]
			# year = pub['bib']['pub_year']
			vol = re.search('[0-9]+',citestring)
			if vol:
				vol = vol.group(0)
				vol_list = []
				for i in indices:
					if "volume" in entries[i].keys():
						vol_list.append(entries[i]['volume'])
					elif "pages" in entries[i].keys():
						pages = re.search('[0-9]+',entries[i]['pages'])
						if pages:
							pages = re.search('[0-9]+',pages.group(0))
							vol_list.append(pages)
						else:
							vol_list.append('-1')
							
				vol_indices = [i for i, x in enumerate(vol_list) if x == vol]
				
				if len(vol_indices) == 1:
					entries[indices[vol_indices[0]]]['citations'] = str(ncites)	
					entries[indices[vol_indices[0]]]['google_pub_id'] = str(pub_id)				
				else:
					print('couldnt find unique match based on volume for ' +pub['bib']['title'] +citestring + ' ' +pub_id)
			else:
				print('no volumes for ' +pub['bib']['title'] +' ' +citestring + ' ' +pub_id)
		else:
			print('no title match for ' +pub['bib']['title'] +' ' +citestring + ' ' +pub_id)
	
	writer = BibTexWriter()
	writer.order_entries_by = None
	with open(outputfile, 'w',encoding='utf-8') as thebibfile:
		bibtex_str = bibtexparser.dumps(bib_database,writer)
		thebibfile.write(bibtex_str)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script adds citations counts to a bib file')
	parser.add_argument('-o', '--output',default="scholarship1.bib",help='the name of the output file')
	parser.add_argument('bibfile',help='the .bib file to add the citations to')
	parser.add_argument('-a', '--author_id',default="",help='the google scholar id for the author. If not provided it will look for a file titled "google_id" in the current working directory')
	parser.add_argument('-s', '--scraperID',help='A scraper ID in case Google Scholar is blocking requests')          
	args = parser.parse_args()
	
	if (not args.author_id):
		with open("google_id") as google_file:
			args.author_id = google_file.readline().strip('\n\r')
	
	bib_add_citations(args.bibfile,args.author_id,args.output,args.scraperID)
