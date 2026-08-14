#!/usr/bin/env python3
import json
from pybliometrics.scopus import AuthorRetrieval, AuthorSearch, AbstractRetrieval, CitationOverview
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser

import re
import string

import argparse

from .bib_get_entries_orcid import make_bibtex_id_list
from .bib_get_entries_orcid import make_title_id
from .bib_get_entries_scopus import scopus_metadata

def bib_add_citations_scopus(bibfile,author_id,outputfile):
	try:
		author = AuthorRetrieval(author_id)
		eids = author.get_documents(refresh=10)
	except:
		print("Unable to get author data using Scopus.  Make sure you have Scopus access")
		return

	# Load bibfile
	# homogenize_fields: Sanitize BibTeX field names, for example change `url` to `link` etc.
	tbparser = BibTexParser(common_strings=True)
	tbparser.homogenize_fields = False  # no dice
	tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file, tbparser)
	entries = bib_database.entries

	# Create list of existing index, title ids, and dois
	titles = make_bibtex_id_list(entries)
	
	# Create list of scopus publication ids if they exist
	scopus_eids = [entry["eid"] if "eid" in entry.keys() else None for entry in entries]

	for doc in eids:

		# Extract a usable identifier (EID/Scopus ID/DOI) from the returned document
		eid_val = getattr(doc, "eid")
		ab = AbstractRetrieval(eid_val, view="FULL")
		try:
			meta = scopus_metadata(ab)
		except Exception:
			continue

		ncites = ab.citedby_count
		if int(ncites) < 1:
			continue

		# First try to match by publication id
		indices = [i for i, x in enumerate(scopus_eids) if x == eid_val]
		if len(indices) == 1:
			# found match
			entries[indices[0]]['citations'] = str(ncites)
			continue

		# Try to match by doi
		doi = getattr(ab, "doi", None)
		if doi != None:
			indices = [i for i, _, d in titles if d == doi.lower()]	
			if len(indices) == 1:
				# found match
				entries[indices[0]]['citations'] = str(ncites)
				entries[indices[0]]['eid'] = str(eid_val)
				continue

		# Try to match by title
		title_id = make_title_id(meta["title"], meta["year"])
		indices = [i for i, x, _ in titles if x == title_id]
		if len(indices) == 1:
			# found match
			entries[indices[0]]['citations'] = str(ncites)
			entries[indices[0]]['eid'] = str(eid_val)
			continue

		if len(indices) > 1:
			# try to match something else?
			# could try secondary matches with these
			# journal = re.search('^[A-z. ]+',citestring).group(0)
			# startpage = re.search('[0-9]+-',citestring).group(0)
			# startpage = startpage[:len(startpage)-1]
			# year = pub['bib']['pub_year']
			vol = getattr(ab,"volume", None)
			if vol:
				vol_list = []
				for i in indices:
					if "volume" in entries[i].keys():
						vol_list.append(entries[i]['volume'])							

				vol_indices = [i for i, x in enumerate(vol_list) if x == vol]
				
				if len(vol_indices) == 1:
					entries[indices[vol_indices[0]]]['citations'] = str(ncites)	
					entries[indices[vol_indices[0]]]['eid'] = str(eid_val)				
				else:
					print('couldnt find unique match based on volume for ' +meta["title"] + ' ' +str(meta["year"]) + ' ' +eid_val)
			else:
				print('no volumes for ' +meta["title"] + ' ' +str(meta["year"]) + ' ' +eid_val)
		else:
			print('no title match for ' +meta["title"] +' ' +str(meta["year"]) + ' ' +eid_val)
	
	writer = BibTexWriter()
	writer.order_entries_by = None
	with open(outputfile, 'w',encoding='utf-8') as thebibfile:
		bibtex_str = bibtexparser.dumps(bib_database,writer)
		thebibfile.write(bibtex_str)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script adds citations counts to a bib file')
	parser.add_argument('-o', '--output',default="scholarship1.bib",help='the name of the output file')
	parser.add_argument('bibfile',help='the .bib file to add the citations to')
	parser.add_argument('-a', '--author_id',default="",help='the scopus id for the author. If not provided it will look for a file titled "scopus_id" in the current working directory')
	parser.add_argument('-s', '--scraperID',help='A scraper ID in case Scopus is blocking requests')          
	args = parser.parse_args()
	
	if (not args.author_id):
		with open("google_id") as google_file:
			args.author_id = google_file.readline().strip('\n\r')
	
	bib_add_citations_scopus(args.bibfile,args.author_id,args.output,args.scraperID)
