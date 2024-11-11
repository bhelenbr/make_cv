#!/usr/bin/env python
# Script to create cv
# must be executed from Faculty/CV folder
# script folder must be in path

import os
import sys
import subprocess
import glob
import re
import pandas as pd
import platform
import shutil
import configparser
import argparse
import datetime
from datetime import date

from .create_config import create_config
from .create_config import verify_config

from .make_cv import make_cv_tables
from .make_cv import typeset
from .make_cv import add_default_args
from .make_cv import process_default_args
from .make_cv import read_args
	
from .stringprotect import abbreviate_name
from .stringprotect import split_names
from .stringprotect import last_first

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser

from pylatexenc.latex2text import LatexNodes2Text

def getyear(paperbibentry):
	if "year" in paperbibentry.keys(): 
		return(int(paperbibentry["year"]))
	if "date" in paperbibentry.keys():
		return(int(paperbibentry["date"][:4]))
	return(0)

def get_collaborator_list(config,years,outputfile):
	faculty_source = config['data_dir']
	
	bibfile = faculty_source +os.sep +config['ScholarshipFolder'] +os.sep +config['ScholarshipFile']
	with open(bibfile) as bibtex_file:
		bibtex_str = bibtex_file.read()
	tbparser = BibTexParser(common_strings=True)
	bib_database = bibtexparser.loads(bibtex_str, tbparser)
	
	cur_grad = faculty_source +os.sep +config['CurrentGradAdviseesFolder'] +os.sep +config['CurrentGradAdviseesFile']
	try:
		cur_grad_names = pd.read_excel(cur_grad,sheet_name="Data",parse_dates=['Start Date'])
		cur_grad_found = True
	except OSError:
		print("Could not open/read file: " + cur_grad)
		cur_grad_found = False
	
	grads = faculty_source +os.sep +config['GradThesesFolder'] +os.sep +config['GradThesesFile']
	try:
		grad_names = pd.read_excel(grads,sheet_name="Data",dtype={'Start Date':int,'Year':int})
		grad_found = True
	except OSError:
		print("Could not open/read file: " + grads)
		grad_found = False
	
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0
		
	f = open(outputfile,"w")
		

	# Combine graduate student lists
	# Rename Column for current students
	cur_grad_names.rename(columns={"Student Name": "Student"},inplace=True)
	cur_grad_names.rename(columns={"Current Program": "Degree"},inplace=True)
	cur_grad_names['Start Date'] = cur_grad_names['Start Date'].apply(lambda x : x.year)
	cur_grad_names['Year'] = year
	
	grad_list = pd.concat([cur_grad_names,grad_names],ignore_index=True,join="inner")
	grad_list = grad_list[grad_list["Degree"].apply(lambda x : "PhD" in x)]
	
	converter = LatexNodes2Text()
	print("PhD Advisees")
	f.write("PhD Advisees")
	for index,row in grad_list.iterrows():
		output_string = "T:\t" + converter.latex_to_text(last_first(row["Student"]))+'\t\t8/1/' +str(row["Year"])
		f.write(output_string +'\n')
		print(output_string)
	
	
	grad_list['Student'] = grad_list['Student'].apply(lambda x : abbreviate_name(x,first_initial_only=True))
	

	collab_list = {}
	year_list = {}
	for icpbe, paperbibentry in enumerate(bib_database.entries):
		
		year = getyear(paperbibentry)
		if not(year >= begin_year):
			continue
			
		if "author" in paperbibentry.keys():
			pubyear = getyear(paperbibentry)
			authstr = paperbibentry['author']
			authstr = re.sub("\\\\gs","",authstr)
			authstr = re.sub("\\\\us","",authstr)
			author_list = split_names(authstr)
			for author in author_list:
				abbrev = abbreviate_name(author,first_initial_only=True)
				if abbrev in grad_list.index:
					continue
				key=last_first(abbrev)
				if key in collab_list.keys():
					collab_list[key] = (last_first(author),max(year,collab_list[key][-1]))
				else:
					collab_list[key] = (last_first(author),year)
			
		
	sortedkeys=sorted(collab_list.keys())	
	
	print("Collaborators")
	f.write("Collaborators\n")
	for key in sortedkeys:
		val = collab_list[key]
		output_string = "A:\t" +converter.latex_to_text(val[0]) +'\t\t8/1/' +str(val[1])
		f.write(output_string +'\n')
		print(output_string)
	
	f.close()

def main(argv = None):
	parser = argparse.ArgumentParser(description='This script creates an NSF Advisee & Collaborator List')
	add_default_args(parser)
	parser.add_argument('-y','--years', help='number of years to include in list (default is 4)',type=int, default = 4)
	parser.add_argument('-o', '--output',default="collaborators.txt",help='the name of the output file')
	
	[configuration,args] = read_args(parser,argv)
	
	config = configuration['FAR']
	process_default_args(config,args)

	get_collaborator_list(config,args.years,args.output)

if __name__ == "__main__":
	main()

