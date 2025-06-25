#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# writes latex files for creating bibliography
# Usually run from CV/Tables folder like this
# pubs2latex_far.py ../../Scholarship/scholarship.bib

import os, sys
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser
from datetime import date
import argparse
import numpy as np

def getyear(paperbibentry):
	if "year" in paperbibentry.keys(): 
		return(int(paperbibentry["year"]))
	if "date" in paperbibentry.keys():
		return(int(paperbibentry["date"][:4]))
	return(0)

def bib2latex_far(f,inputfile,keywords,years=-1,max_pubs=-1):

	nrecord = 0
	if max_pubs < 0:
		max_pubs = sys.maxsize
		
	# homogenize_fields: Sanitize BibTeX field names, for example change `url` to `link` etc.
	tbparser = BibTexParser(common_strings=True)
	tbparser.homogenize_fields = False  # no dice
	tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'

	try:
		with open(inputfile,encoding='utf-8') as bibtex_file:
			bib_database = bibtexparser.load(bibtex_file, tbparser)
		bib_database.entries = sorted(bib_database.entries, key=lambda k: getyear(k), reverse=True)	
	except OSError:
		print("Could not open/read file: " +inputfile)
		return(nrecord)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0

	f.write("\\begin{enumerate}\n")

	for icpbe, paperbibentry in enumerate(bib_database.entries):
		year = getyear(paperbibentry)
		if not(year >= begin_year):
			continue
	
		if "keywords" in paperbibentry.keys():
			kword = str(paperbibentry["keywords"])
			for count,etype in enumerate(keywords):
				etype = etype.strip()
				if kword.find(etype) > -1:
					f.write("\\item\n\\fullcite{"+paperbibentry["ID"]+"}\n")
					nrecord += 1
					break
		
		if (nrecord == max_pubs):
			break
	
	f.write("\\end{enumerate}\n")
	return(nrecord)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs bibliographic latex citations to a latex table for (journals,refereed conferences,conferences,patents,books,invited talks) received in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="0",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('-e', '--ending',default="_far",type=str,help='ending to append to filenames')
	parser.add_argument('inputfile',help='the input bibliography file name')
	parser.add_argument('outputpath',help='the input bibliography file name')         
	args = parser.parse_args()
	
	f = [open(args.outputpath +os.sep +etype+args.ending+".tex", args.append) for count,etype in  enumerate(categories)]	
	necord = bib2latex_far(f,args.years,args.inputfile)
	
	for count,etype in enumerate(categories):
		f[count].close()
		if (necord[count] == 0):	
			os.remove(args.outputpath +os.sep +etype+args.ending+".tex")