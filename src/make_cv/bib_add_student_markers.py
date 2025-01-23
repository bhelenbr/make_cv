#! /usr/bin/env python3
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
import pandas as pd
import datetime

from .stringprotect import abbreviate_name
from .stringprotect import split_names
from .stringprotect import first_last

def getyear(paperbibentry):
	if "year" in paperbibentry.keys(): 
		return(int(paperbibentry["year"]))
	if "date" in paperbibentry.keys():
		return(int(paperbibentry["date"][:4]))
	return(0)

def bib_add_student_markers(years,ugrads,grads,cur_grad,bibfile,outputfile):
	try:
		cur_grad_names = pd.read_excel(cur_grad,sheet_name="Data",parse_dates=['Start Date'])
	except OSError:
		print("Could not open/read file: " + cur_grad)
		cur_grad_names = pd.DataFrame([],columns=('Student Name','Start Date','Term'))
		
	try:
		grad_names = pd.read_excel(grads,sheet_name="Data",dtype={'Start Date':int,'Year':int})
	except OSError:
		print("Could not open/read file: " + grads)
		grad_names = pd.DataFrame([],columns=('Student','Start Date'))
	
	try:
		ugrad_names = pd.read_excel(ugrads,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + ugrads)
		ugrad_names	= pd.DataFrame([],columns=('Student','Calendar Year','Term'))
		
	
	# Split lists of undergraduate students into individual entries
	row_list = []
	for row in range(ugrad_names.shape[0]):
		row_data = ugrad_names.iloc[row]
		list_of_names = split_names(row_data['Students'])
		for name in list_of_names:
			name_string = abbreviate_name(name,first_initial_only=True)
			this_dict = {'Student':name_string,'Calendar Year':row_data['Calendar Year'],'Term':row_data['Term']}
			row_list.append(this_dict)
	ugrad_list = pd.DataFrame(row_list,columns=('Student','Calendar Year','Term'))
	
	# Find start date of undergraduates
	ugrad_list = ugrad_list.pivot_table(values=['Calendar Year'], index=['Student'], aggfunc={'Calendar Year': 'max'},fill_value=0,observed=False)	
	
	
	# Combine graduate student lists
	# Rename Column for current students
	cur_grad_names.rename(columns={"Student Name": "Student"},inplace=True)
	cur_grad_names['Start Date'] = cur_grad_names['Start Date'].apply(lambda x : x.year)
	grad_list = pd.concat([cur_grad_names,grad_names],ignore_index=True,join="inner")
	grad_list['Student'] = grad_list['Student'].apply(lambda x : abbreviate_name(x,first_initial_only=True))
	grad_list.rename(columns={'Start Date':'Calendar Year'},inplace=True)
	grad_list = grad_list.pivot_table(values=['Calendar Year'], index=['Student'], aggfunc={'Calendar Year': 'max'},fill_value=0,observed=False)

	# homogenize_fields: Sanitize BibTeX field names, for example change `url` to `link` etc.
	tbparser = BibTexParser(common_strings=True)
	tbparser.homogenize_fields = False  # no dice
	tbparser.alt_dict['url'] = 'url'    # this finally prevents change 'url' to 'link'
	
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bib_database = bibtexparser.load(bibtex_file, tbparser)
	
	# new_db = BibDatabase()
	
	bibdblen = len(bib_database.entries)
	for icpbe, paperbibentry in enumerate(bib_database.entries):
		if "author" in paperbibentry.keys():
			pubyear = getyear(paperbibentry)
			authstr = paperbibentry['author']
			author_list = split_names(authstr)
			spacer=""
			newauths = ""
			for author in author_list:
				abbrev = abbreviate_name(author,first_initial_only=True)
				newauths = newauths +spacer +first_last(author)

				if abbrev in grad_list.index:
					if grad_list.loc[abbrev,'Calendar Year']+years > pubyear:
						newauths = newauths +'\\gs'
				if abbrev in ugrad_list.index:
					if ugrad_list.loc[abbrev,'Calendar Year']+years > pubyear:
						newauths = newauths +'\\us'
				spacer = " and "
			paperbibentry['author'] = newauths
		
	writer = BibTexWriter()
	writer.order_entries_by = None
	with open(outputfile, 'w', encoding='utf-8') as thebibfile:
		bibtex_str = bibtexparser.dumps(bib_database,writer)
		thebibfile.write(bibtex_str)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script adds markers to student authors in a bib file')
	parser.add_argument('-y', '--years',default="200",type=int,help='the number of years after student project to include, default is all years')
	parser.add_argument('-o', '--output',default="scholarship1.bib",help='the name of the output file')
	parser.add_argument('ugradfile',help='the undergraduate research file name')          
	parser.add_argument('gradfile',help='the thesis excel file name') 
	parser.add_argument('cur_grads',help='the current graduate student file')
	parser.add_argument('bibfile',help='the .bib file to add the markers to')
	args = parser.parse_args()
	
	bib_add_student_markers(args.years,args.ugradfile,args.gradfile,args.cur_grads,args.bibfile,args.output)

		
		
