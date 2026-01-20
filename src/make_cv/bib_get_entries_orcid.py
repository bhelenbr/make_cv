#!/usr/bin/env python3
import json
import os
import re
import string
import argparse
from datetime import date
import sys
import time

import requests
import re

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexautocomplete import BibtexAutocomplete

from .stringprotect import str2latex
from pylatexenc.latex2text import LatexNodes2Text

from . import global_prefs

def make_title_id(title, year):
	# Strip braces and other BibTeX bracketing
	title_string = LatexNodes2Text().latex_to_text(title).lower()
	title_id = re.sub(r"[^a-z0-9]+", "", title_string)
	title_id += str(year)
	return title_id

def make_bibtex_id_list(entries):
	parsed_entries = []
	for i, entry in enumerate(entries):
		title = entry.get('title') or entry.get('TITLE')
		year_str = getyear(entry)

		# Strip braces and other BibTeX bracketing
		title_id = make_title_id(title,year_str)

		doi = entry.get('doi') or entry.get('DOI')
		doi_val = doi.lower() if doi else None
		parsed_entries.append((i, title_id, doi_val))

	return parsed_entries


def getyear(paperbibentry):
	if "year" in paperbibentry.keys(): 
		return int(paperbibentry["year"])
	if "date" in paperbibentry.keys():
		return int(paperbibentry["date"][:4])
	return 0


# -------------------------------
# Configuration
# -------------------------------

ORCID_API = "https://pub.orcid.org/v3.0"
HEADERS_ORCID = {"Accept": "application/json"}
BIBTEX_TYPE_MAP = {
	"journal-article": "article",
	"conference-paper": "inproceedings",
	"book": "book",
	"book-chapter": "incollection",
	"report": "techreport"
}

# -------------------------------
# Utility helpers
# -------------------------------

def safe_value(d, *keys):
	for k in keys:
		if not isinstance(d, dict):
			return None
		d = d.get(k)
		if d is None:
			return None
	return d


def normalize_key(text):
	if text is None:
		return ""
	text = text.lower()
	text = re.sub(r"[^a-z0-9]+", "", text)
	return text[:20]


def normalize_bibtex(bib):
	bib = bib.replace("–", "--").replace("—", "--")
	return bib.strip() + "\n\n"


# -------------------------------
# ORCID access
# -------------------------------

def get_all_works(orcid):
	url = f"{ORCID_API}/{orcid}/works"
	try:
		r = requests.get(url, headers=HEADERS_ORCID, timeout=10)
		r.raise_for_status()
		return r.json().get("group", [])
	except requests.RequestException as exc:
		print(f"Failed to fetch ORCID works for {orcid}: {exc}")
		return []


def get_work(orcid, put_code):
	url = f"{ORCID_API}/{orcid}/work/{put_code}"
	try:
		r = requests.get(url, headers=HEADERS_ORCID, timeout=10)
		r.raise_for_status()
		return r.json()
	except requests.RequestException as exc:
		print(f"Failed to fetch ORCID work {put_code} for {orcid}: {exc}")
		return None


def extract_doi(work):
	for ext in (work.get("external-ids", {}).get("external-id") or []):
		if ext.get("external-id-type") == "doi":
			return ext.get("external-id-value")
	return None


def extract_authors(work):
	contributors = work.get("contributors", {}).get("contributor", [])
	authors = []
	for c in contributors:
		name = safe_value(c, "credit-name", "value")
		if name:
			authors.append(name)
	return " and ".join(authors) if authors else None

def extract_publication_year(work):
	pd = work.get("publication-date")
	if not pd:
		return None

	year = safe_value(pd, "year", "value")
	if not year:
		return None

	return(year)
	
def extract_orcid_bibtex(work):
	citation = work.get("citation")
	if not citation:
		return None

	if citation.get("citation-type", "").lower() != "bibtex":
		return None

	bib = citation.get("citation-value")
	if not bib or not bib.strip().startswith("@"):
		return None

	bib = bib.strip()

	# If BibTeX already has a DOI, leave it alone
	if re.search(r"\bdoi\s*=", bib, re.IGNORECASE):
		return bib

	# Try to get DOI from ORCID structured metadata
	doi = extract_doi(work)
	if not doi:
		return bib

	# Insert DOI before the closing brace
	bib = bib.rstrip()

	# Remove trailing closing brace
	if bib.endswith("}"):
		bib = bib[:-1].rstrip()

	# Ensure trailing comma before adding DOI
	if not bib.endswith(","):
		bib += ","

	bib += f"\n  doi = {{{doi}}}\n}}"

	return bib


# -------------------------------
# BibTeX writer
# -------------------------------

def bibtex_entry(work):
	work_type = work.get("type", "").lower()
	bib_type = BIBTEX_TYPE_MAP.get(work_type, "misc")
	fields = {
		"title": str2latex(safe_value(work, "title", "title", "value")),
		"author": extract_authors(work),
		"year": safe_value(work, "publication-date", "year", "value"),
		"journal": str2latex(safe_value(work, "journal-title", "value")),
		"doi": extract_doi(work)
	}
	cite_key = make_title_id(fields["title"], fields["year"])
	
	# 1️⃣ ORCID BibTeX takes precedence
	orcid_bib = extract_orcid_bibtex(work)
	if orcid_bib:
		orcid_bib = re.sub(r'{[^,]+', "{" +cite_key, orcid_bib, count=1)
		return normalize_bibtex(orcid_bib)

	bib = [f"@{bib_type}{{{cite_key},"]
	for field, value in fields.items():
		if value:
			bib.append(f"  {field} = {{{value}}},")

	if bib[-1].endswith(","):
		bib[-1] = bib[-1][:-1]

	bib.append("}\n")
	return "\n".join(bib)

def bib_get_entries_orcid(bibfile, orcid, years, outputfile):

	# Set starting year for search
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0
		
	# get list of publication identifiers in existing file
	tbparser = BibTexParser(common_strings=True)
	tbparser.alt_dict['url'] = 'url'	# this prevents change 'url' to 'link'
	tbparser.expect_multiple_parse = True
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file, tbparser)
	entries = bib_database.entries
	bib_entry_ids = make_bibtex_id_list(entries)
		
	# Get all works from orcid
	groups = get_all_works(orcid)
	if not groups:
		print(f"No works returned for ORCID {orcid}")
		return

	for group in groups:
		summaries = group.get("work-summary") or []
		if not summaries:
			continue
		summary = summaries[0]
		put_code = summary.get("put-code")
		if not put_code:
			continue
		work = get_work(orcid, put_code)
		if not work:
			continue
		year = extract_publication_year(work)
		if year is None or int(year) < begin_year:
			continue
		
		
		# Skip entries that have matching doi database
		doi = extract_doi(work)
		if doi is not None:
			if any(doi.lower() == entry_doi for _, _, entry_doi in bib_entry_ids):
				continue
		
		title = safe_value(work, "title", "title", "value")
		if not title:
			continue
		title_id = make_title_id(title,str(year))
	
		# Skip entries that have matching title+year database
		matched = False
		for i, entry_title_id, _ in bib_entry_ids:
			if title_id == entry_title_id:
				if doi is not None:
					print(f"Adding DOI {doi} to existing entry {title_id}")
					entries[i]["doi"] = doi
				matched = True
				break
		if matched:
			continue
			
		# New entry
		new_entry = bibtex_entry(work)
		
		# Try to fill entry using BibTeX autocomplete
		completer = BibtexAutocomplete()
		completer.load_string(new_entry)
		completer.autocomplete()

		bibtex_str = completer.write_string()[0]
		print(bibtex_str)
		
		if not global_prefs.quiet:
			print('Is this btac entry correct and ready to be added?\nOnce an entry is added any future changes must be done manually.')
			YN = input('Y/N? ')
			if YN.upper() != 'Y':
				continue
		
		bib_database = bibtexparser.loads(bibtex_str, tbparser)	

	writer = BibTexWriter()
	writer.order_entries_by = None
	with open(outputfile, 'w',encoding='utf-8') as thebibfile:
		bibtex_str = bibtexparser.dumps(bib_database, writer)
		thebibfile.write(bibtex_str)

	#cleanup
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






