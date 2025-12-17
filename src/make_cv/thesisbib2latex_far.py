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
import datetime as dt
import argparse
import numpy as np
import pandas as pd

from .bib2latex_far import getyear
from .stringprotect import split_names
from .stringprotect import abbreviate_name
from .stringprotect import str2latex

def read_thesis_bib(thesisfile):
	import pandas as pd
	import bibtexparser
	from bibtexparser.bparser import BibTexParser

	# Create dataframe
	df = pd.DataFrame(columns=[
		"Student",
		"Start Date",
		"Year",
		"Degree",
		"Advisor",
		"Title",
		"Comments"
	])
	
	# Try common encodings
	for enc in ("utf-8", "cp1252", "latin-1"):
		try:
			with open(thesisfile, encoding=enc) as bibtex_file:
				tbparser = BibTexParser()
				bib_database = bibtexparser.load(bibtex_file, tbparser)
			break
		except UnicodeDecodeError:
			continue
		except OSError:
			print(f"Could not open/read file: {thesisfile}")
			return df
	else:
		print(f"Could not decode file: {thesisfile}")
		return df

	bib_database.entries = sorted(
		bib_database.entries,
		key=lambda k: getyear(k),
		reverse=True
	)

	for paperbibentry in bib_database.entries:
		row = {}

		if "author" in paperbibentry:
			names = split_names(paperbibentry["author"])
			row["Student"] = abbreviate_name(names[0])
			row["Advisor"] = abbreviate_name(names[1]) if len(names) > 1 else ""
		else:
			print("Missing Author in " + paperbibentry.get("ID", "UNKNOWN"))
			continue

		row["Start Date"] = "0"
		row["Year"] = str(getyear(paperbibentry))

		entrytype = paperbibentry.get("ENTRYTYPE", "").lower()
		if "type" in paperbibentry:
			row["Degree"] = paperbibentry["type"]
		elif entrytype == "phdthesis":
			row["Degree"] = "Ph.D."
		elif entrytype == "mastersthesis":
			row["Degree"] = "M.S."
		else:
			row["Degree"] = "unknown"

		if "title" in paperbibentry:
			row["Title"] = paperbibentry["title"]
		else:
			print("Missing Title in " + paperbibentry.get("ID", "UNKNOWN"))
			continue

		row["Comments"] = paperbibentry.get("school", "")

		# Correct append
		df.loc[len(df)] = row

	return df

	

def thesisbib2latex_far(f,years,studentfile,thesisfile,max_rows=-1):
	try:
		source = pd.read_excel(studentfile,sheet_name="Data",parse_dates=['Start Date'])
		student_found = True
	except OSError:
		print("Could not open/read file: " + studentfile)
		student_found = False
	
	today = dt.date.today()
	year = today.year
	begin_year = year - years
	
	source2 = read_thesis_bib(thesisfile)
	
	thesis_found = False
	if len(source2) > 0:
		thesis_found = True
	
	if (student_found):
		source = source.fillna({'Start Date':today})
		source.sort_values(by=['Start Date','Current Program','Student Name'], inplace=True, ascending = [False,True,True])
		df = source.reset_index()
		nrows = df.shape[0]
	else:
		nrows = 0
	
	if (thesis_found):
		source2 = source2.fillna(0)
		if years > 0:
			source2 = source2[source2['Year'].apply(lambda x: int(x)) >= begin_year]
		source2.sort_values(by=['Year','Degree','Student'], inplace=True, ascending = [False,True,True])
		df2= source2.reset_index()
		nrows2 = df2.shape[0]
	else:
		nrows2 = 0
	
	if (nrows+nrows2 > 0):
		f.write("\\begin{tabularx}{\\linewidth}{>{\\rownum}rXll}\n & Name: Title  & Date & Degree \\tablehead\n")
		f.write("\\tablecontinue{Graduate Advisees}\n")
		newline=""
		if nrows > 0:
			count = 0
			while count < nrows:
				f.write(newline)
				f.write(" & " +abbreviate_name(df.loc[count,"Student Name"])+": in progress"  + " &  & " +str2latex(df.loc[count,"Current Program"][(df.loc[count,"Current Program"].find("-")+1):]))
				newline="\\\\\n"
				count += 1
		
		if max_rows > 0 and nrows2 > max_rows:
			nrows2 = max_rows
			
		if nrows2 > 0:
			count = 0
			while count < nrows2:
				f.write(newline)
				f.write(" & " +abbreviate_name(df2.loc[count,"Student"])+": " +str2latex(df2.loc[count,"Title"]) + " & " +'{0:d}'.format(int(df2.loc[count,"Year"])) + " & " +str2latex(df2.loc[count,"Degree"]))
				newline="\\\\\n"
				count += 1
	
		f.write("\n\\end{tabularx}\n")
		
	return(nrows+nrows2)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs thesis data to a latex table for the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('studentfile',help='the student excel file name')		  
	parser.add_argument('thesisfile',help='the thesis bib file name') 
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = thesisbib2latex_far(f,args.years,args.studentfile,args.thesisfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)