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
import csv
import warnings

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
		return int(paperbibentry["year"])
	if "date" in paperbibentry.keys():
		return int(paperbibentry["date"][:4])
	return 0

def get_collaborator_list(config, output_format):
	years = config.getint('years')

	faculty_source = config['data_dir']
	
	bibfile = os.path.join(faculty_source, config['ScholarshipFile'])
	with open(bibfile,encoding='utf-8') as bibtex_file:
		bibtex_str = bibtex_file.read()
	tbparser = BibTexParser(common_strings=True)
	bib_database = bibtexparser.loads(bibtex_str, tbparser)
	
	cur_grad = os.path.join(faculty_source, config['CurrentGradAdviseesFile'])
	try:
		cur_grad_names = pd.read_excel(cur_grad, sheet_name="Data", parse_dates=['Start Date'])
	except OSError:
		print("Could not open/read file: " + cur_grad)
		return
	
	grads = os.path.join(faculty_source, config['GradThesesFile'])
	try:
		grad_names = pd.read_excel(grads, sheet_name="Data", dtype={'Start Date': int, 'Year': int})
	except OSError:
		print("Could not open/read file: " + grads)
		return
		
	grantfile = os.path.join(faculty_source, config['GrantsFile'])
	try:
		grants = pd.read_excel(grantfile,sheet_name="Data")
		grants.fillna(value={'Principal Investigators':'','Funded?':'No'},inplace=True)
		grants = grants[grants['Funded?'].str.match('Y')]
		grants.reset_index(inplace=True,drop=True)
	except OSError:
		print("Could not open/read file: " + grantfile)
		return
		
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
	else:
		begin_year = 0


	# Prepare data for output
	advisees_list = []
	collab_list = {}

	# Combine graduate student lists
	cur_grad_names.rename(columns={"Student Name": "Student"}, inplace=True)
	cur_grad_names.rename(columns={"Current Program": "Degree"}, inplace=True)
	cur_grad_names['Start Date'] = cur_grad_names['Start Date'].apply(lambda x: x.year)
	cur_grad_names['Year'] = year
	
	grad_list = pd.concat([cur_grad_names,grad_names], ignore_index=True, join="inner")	
	
	cnames= grad_list.columns
	grad_list = grad_list[grad_list["Degree"].apply(lambda x: "PhD" in x)]
	# Check if the filtered DataFrame is empty
	if grad_list.empty:
		# Reassign the column names from the original DataFrame
		grad_list = pd.DataFrame(columns=cnames)
	
	converter = LatexNodes2Text()
	for index, row in grad_list.iterrows():
		student_name = converter.latex_to_text(last_first(row["Student"]))
		advisees_list.append([student_name, '8/1/' + str(row["Year"])])
	
	grad_list['Student'] = grad_list['Student'].apply(lambda x: abbreviate_name(x, first_initial_only=True))
	for icpbe, paperbibentry in enumerate(bib_database.entries):
		year = getyear(paperbibentry)
		if not (year >= begin_year):
			continue
		
		if "author" in paperbibentry.keys():
			authstr = paperbibentry['author']
			authstr = re.sub("\\\\gs", "", authstr)
			authstr = re.sub("\\\\us", "", authstr)
			author_list = split_names(authstr)
			for author in author_list:
				abbrev = abbreviate_name(author, first_initial_only=True)
				if abbrev in grad_list['Student'].values:
					continue
				key = last_first(abbrev)
				if key in collab_list.keys():
					collab_list[key] = (last_first(author), max(year, collab_list[key][-1]))
				else:
					collab_list[key] = (last_first(author), year)
					
	# add grant collaborators
	grants = grants[grants['End Date'].apply(lambda x: x.year) >= begin_year]
	for index, row in grants.iterrows():
		year = row['End Date'].year
		
		names_no_PI = re.sub(r"\([a-zA-Z-]*\)","",row['Principal Investigators'])
		for author in split_names(names_no_PI):
			abbrev = abbreviate_name(author, first_initial_only=True)
			if abbrev in grad_list.index:
				continue
			key = last_first(abbrev)
			if key in collab_list.keys():
				collab_list[key] = (last_first(author), max(year, collab_list[key][-1]))
			else:
				collab_list[key] = (last_first(author), year)

	
	sortedkeys = sorted(collab_list.keys())
	
	collaborators = []
	for key in sortedkeys:
		val = collab_list[key]
		collaborator_name = converter.latex_to_text(val[0])
		collaborators.append([collaborator_name, '8/1/' + str(val[1])])

	# Output to CSV or Excel
	if output_format == 'csv':
		with open("collaborators.csv", mode="w", newline='', encoding='utf-8') as csvfile:
			csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
			csv_writer.writerow(["PhD Advisees"])
			csv_writer.writerow(["Name", "Date"])
			csv_writer.writerows(advisees_list)

			csv_writer.writerow([])
			csv_writer.writerow(["Collaborators"])
			csv_writer.writerow(["Name", "Date"])
			csv_writer.writerows(collaborators)
			print("collaborators.csv created")

	elif output_format == 'xlsx':
		with pd.ExcelWriter("collaborators.xlsx", engine='openpyxl') as writer:
			pd.DataFrame(advisees_list, columns=["Name", "Date"]).to_excel(writer, sheet_name='PhD Advisees', index=False)
			pd.DataFrame(collaborators, columns=["Name", "Date"]).to_excel(writer, sheet_name='Collaborators', index=False)
			print("collaborators.xlsx created")

def main(argv=None):
	warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
	parser = argparse.ArgumentParser(description='This script creates an NSF Advisee & Collaborator List')
	add_default_args(parser)
	parser.add_argument('-fmt', '--format', choices=['csv', 'xlsx'], default='xlsx', help='output format (csv or xlsx)')
	
	[configuration, args] = read_args(parser, argv)
	
	config = configuration['CV']
	process_default_args(config, args)

	get_collaborator_list(config, args.format)

if __name__ == "__main__":
	main()
