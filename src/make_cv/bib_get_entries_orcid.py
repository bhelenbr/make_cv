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
from bibtexautocomplete import BibtexAutocomplete

from . import global_prefs

# -------------------------------
# Configuration
# -------------------------------

ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF_API = "https://api.crossref.org/works"

HEADERS_ORCID = {"Accept": "application/json"}
HEADERS_CROSSREF = {
	"User-Agent": "ORCID-BibTeX-Exporter/1.0 (mailto:bhelenbr@clarkson.edu)"
}

BIBTEX_TYPE_MAP = {
	"journal-article": "article",
	"conference-paper": "inproceedings",
	"book": "book",
	"book-chapter": "incollection",
	"report": "techreport"
}

CROSSREF_CACHE = {}

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
	if not text:
		return "unknown"
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
	r = requests.get(url, headers=HEADERS_ORCID)
	r.raise_for_status()
	return r.json().get("group", [])


def get_work(orcid, put_code):
	url = f"{ORCID_API}/{orcid}/work/{put_code}"
	r = requests.get(url, headers=HEADERS_ORCID)
	r.raise_for_status()
	return r.json()


def extract_doi(work):
	for ext in work.get("external-ids", {}).get("external-id", []):
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
# Crossref access
# -------------------------------

def crossref_lookup(doi):
	if doi in CROSSREF_CACHE:
		return CROSSREF_CACHE[doi]

	try:
		url = f"{CROSSREF_API}/{doi}"
		r = requests.get(url, headers=HEADERS_CROSSREF, timeout=10)
		r.raise_for_status()
		msg = r.json()["message"]
		CROSSREF_CACHE[doi] = msg
		return msg
	except Exception:
		CROSSREF_CACHE[doi] = None
		return None


def crossref_authors(msg):
	authors = []
	for a in msg.get("author", []):
		family = a.get("family")
		given = a.get("given")
		if family and given:
			authors.append(f"{family}, {given}")
		elif family:
			authors.append(family)
	return " and ".join(authors) if authors else None


def crossref_year(msg):
	for key in ("published-print", "published-online", "issued"):
		parts = msg.get(key, {}).get("date-parts")
		if parts and parts[0]:
			return str(parts[0][0])
	return None


def crossref_title(msg):
	titles = msg.get("title")
	return titles[0] if titles else None


def crossref_journal(msg):
	container = msg.get("container-title")
	return container[0] if container else None

# -------------------------------
# Metadata merge
# -------------------------------

def merge_metadata(work):
	doi = extract_doi(work)
	cr = crossref_lookup(doi) if doi else None

	if cr:
		return {
			"title": crossref_title(cr),
			"author": crossref_authors(cr),
			"year": crossref_year(cr),
			"journal": crossref_journal(cr),
			"volume": cr.get("volume"),
			"number": cr.get("issue"),
			"pages": cr.get("page"),
			"doi": doi
		}

	# ORCID structured fallback
	return {
		"title": safe_value(work, "title", "title", "value"),
		"author": extract_authors(work),
		"year": safe_value(work, "publication-date", "year", "value"),
		"journal": safe_value(work, "journal-title", "value"),
		"volume": None,
		"number": None,
		"pages": None,
		"doi": doi
	}


# -------------------------------
# BibTeX writer
# -------------------------------

def bibtex_entry(work):


	# 2️⃣ Crossref → ORCID fallback
	meta = merge_metadata(work)
	work_type = work.get("type", "").lower()
	bib_type = BIBTEX_TYPE_MAP.get(work_type, "misc")

	key_parts = [
		normalize_key(meta["author"].split(" and ")[0] if meta["author"] else None),
		meta["year"] or "nodate",
		normalize_key(meta["title"])
	]
	cite_key = "_".join(filter(None, key_parts))
	
	# 1️⃣ ORCID BibTeX takes precedence
	orcid_bib = extract_orcid_bibtex(work)
	if orcid_bib:
		orcid_bib = re.sub(r'{[^,]+', "{" +cite_key, orcid_bib, count=1)
		return normalize_bibtex(orcid_bib)
		

	fields = {
		"title": meta["title"],
		"author": meta["author"],
		"journal": meta["journal"],
		"year": meta["year"],
		"volume": meta["volume"],
		"number": meta["number"],
		"pages": meta["pages"],
		"doi": meta["doi"]
	}

	bib = [f"@{bib_type}{{{cite_key},"]

	for field, value in fields.items():
		if value:
			bib.append(f"  {field} = {{{value}}},")

	if bib[-1].endswith(","):
		bib[-1] = bib[-1][:-1]

	bib.append("}\n")
	return "\n".join(bib)


# --------


def make_bibtex_id_list(file_path):
	with open(file_path, 'r') as file:
		content = file.read()
	
	# Split the content into individual entries
	entries = re.split(r'\n@', content)
	parsed_entries = []

	for entry in entries:
		year_match = re.search(r'year\s*=\s*{(\d+)}', entry)
		title_match = re.search(r'(?:,|\n)\s*title\s*=\s*{(.+?)},', entry)
		if year_match and title_match:
			# Get rid of protect strings
			title_string = title_match.group(1)
			title_string = re.sub('{', "", title_string)
			title_string = re.sub('}', "", title_string)
			title_id = ''.join(word.lower() for word in title_string.split() if (word.isalpha()  and word.isascii()))
			title_id += year_match.group(1)
		else:
			continue
			
		# Extract doi
		doi_match = re.search(r'doi\s*=\s*{(.+?)}', entry)
		if doi_match:
			doi = doi_match.group(1).lower()
		else:
			doi = None
		
		parsed_entries.append((title_id,doi))
	
	return parsed_entries

def bib_get_entries_orcid(bibfile, orcid, years, outputfile):

	# Set starting year for search
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0
		
	# get list of publication identifiers in existing file
	bib_entries = make_bibtex_id_list(bibfile)
	
# 	for bibid in bib_entries:
# 		print(bibid)
	
	# Get all works from orcid
	groups = get_all_works(orcid)
	
	for group in groups:
		summary = group["work-summary"][0]
		put_code = summary["put-code"]
		work = get_work(orcid, put_code)
		year = extract_publication_year(work)
		if year is None or int(year) < begin_year:
			continue
		
		
		# Skip entries that have matching doi database
		doi = extract_doi(work)
		if doi is not None:
			if any(doi.lower() == entry_doi for _, entry_doi in bib_entries):
				continue
		
		title = safe_value(work, "title", "title", "value")
		if (title is None):
			continue
		title_id = ''.join(word.lower() for word in title.split() if (word.isalpha()  and word.isascii()))
		title_id += year
		if any(title_id == entry_title_id for entry_title_id, _ in bib_entries):
			if doi is not None:
				print(f'possibly missing doi {title_id}: {doi}')
			continue
			
		# New entry
		print(title_id)
		new_entry = bibtex_entry(work)
		
		# Try to fill entry using BibTeX autocomplete
		completer = BibtexAutocomplete()
		completer.load_string(new_entry)
		completer.autocomplete()
		print(completer.write_string()[0])
		
		if not global_prefs.quiet:
			print('Is this btac entry correct and ready to be added?\nOnce an entry is added any future changes must be done manually.')
			YN = input('Y/N? ')
			if YN.upper() != 'Y':
				continue
			
		with open(outputfile, 'a') as dest_file:  # Use 'a' to append
			dest_file.write(completer.write_string()[0])
	
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






