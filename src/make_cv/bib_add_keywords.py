#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# use this like this:
# export
# label_bib_entries.py <bib_file_to_label>

import os, sys
import re

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser
import argparse

def guess_type(paperbibentry):
	entrytype = str(paperbibentry["ENTRYTYPE"])
	if entrytype  == "misc":
		if "note" in paperbibentry.keys():
			if (paperbibentry["note"].find("Patent") > -1):
				return("patent")
		else:
			return("invited")
	elif entrytype  ==  "article":
		if "journal" in paperbibentry.keys():
			if (paperbibentry["journal"].find("arXiv") > -1):
				return("arXiv")
			else:
				return("journal")
		else:
			return("ignore")
	elif (entrytype  == "inproceedings"):
		if "booktitle" in paperbibentry.keys():
			if (paperbibentry["booktitle"].find("IEEE") > -1) or (paperbibentry["booktitle"].find("ASME") > -1) or (paperbibentry["booktitle"].find("AIAA") > -1):
				return("refereed")
			else:
				return("conference")
		else:
			return("conference")
	elif (entrytype == "conference"):
		return("conference")
	elif entrytype  == "techreport":
		return("techreport")
	elif entrytype  == "book":
		return("book")
	else:
		return('ignore')
		
keyword_list =['journal','refereed','conference', 'book', 'patent', 'invited','arXiv','techreport','ignore']

def input_keyword(keyword):
	while True:
		print('Guessing type is ' +keyword +'.  If so hit return, otherwise enter:')
		for (n,key) in enumerate(keyword_list):
			print(str(n) +' for ' +key)
		response = input()
		if response.isdigit():
			intr = int(response)
			if intr >= 0 and intr < len(keyword_list):
				keyword = keyword_list[intr]
				break
		elif response == '':
			break
	return(keyword)

def add_keyword(paperbibentry):
	if not ("keywords" in paperbibentry.keys()):
		print(paperbibentry)
		keyword = guess_type(paperbibentry)
		keyword = input_keyword(keyword)
		paperbibentry["keywords"] = keyword
	else:
		# make sure there is a keyword in list of classification keywords
		klist = re.split(';|,', paperbibentry["keywords"])
		keyfound = False
		for key in klist:
			if key.strip() in keyword_list:
				keyfound = True
				break
		if not keyfound:
			print(paperbibentry)
			keyword = guess_type(paperbibentry)
			input_keyword(keyword)
			response = input('Should I erase current keywords [Y/N] default is [Y]')
			if (response == 'N'):
				paperbibentry["keywords"] += '; ' +keyword
			else:
				paperbibentry["keywords"] = keyword


def bib_add_keywords(bibfile,outputfile):
	# homogenize_fields: Sanitize BibTeX field names, for example change `url` to `link` etc.
	tbparser = BibTexParser(common_strings=True)
	tbparser.homogenize_fields = False  # no dice
	tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'
	
	with open(bibfile) as bibtex_file:
		bibtex_str = bibtex_file.read()
	bib_database = bibtexparser.loads(bibtex_str, tbparser)
	
	new_db = BibDatabase()
	bibdblen = len(bib_database.entries)
	for paperbibentry in bib_database.entries:
		if "year" in paperbibentry.keys() or "date" in paperbibentry.keys():
			add_keyword(paperbibentry)
			new_db.entries.append(paperbibentry)
	
	new_db.entries = sorted(new_db.entries, key=lambda k: int(k["year"]), reverse=True)	
	
	writer = BibTexWriter()
	# writer.contents = ['comments', 'entries']
	# writer.indent = '  '
	# writer.order_entries_by = ('year','ENTRYTYPE', 'author')
	writer.order_entries_by = None
	
	with open(outputfile, 'w') as thebibfile:
		bibtex_str = bibtexparser.dumps(new_db,writer)
		thebibfile.write(bibtex_str)
		
	# file = open("scholarship1.bib",'a')
	# file.write("@Comment{jabref-meta: databaseType:bibtex;}\n\n")
	# file.write("\n@Comment{jabref-meta: grouping:\n")
	# file.write("0 AllEntriesGroup:;\n")
	# file.write("1 AutomaticKeywordGroup:\\;0\\;keywords\\;,\\;>\\;1\\;0x8a8a8aff\\;\\;\\;;\n}")
	# file.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script guesses the type of each entry and adds the type as a keyword')
	parser.add_argument('-o', '--output',default="scholarship1.bib",help='the name of the output file')
	parser.add_argument('bibfile',help='the .bib file to add the markers to')
	args = parser.parse_args()
	bib_add_keywords(args.bibfile,args.output)