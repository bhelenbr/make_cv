#!/usr/bin/env python
# Script to create cv
# must be executed from Faculty/CV folder
# script folder must be in path

import os
import sys
import subprocess
import glob
import pandas as pd
import platform
import shutil
import configparser
import argparse
import warnings
from pathlib import Path

from .bib2latex_far import bib2latex_far

from .make_cv import make_cv_tables
from .make_cv import typeset
from .make_cv import add_default_args
from .make_cv import process_default_args
from .make_cv import read_args

from .UR2latex_far import UR2latex_far
from .personal_awards2latex_far import personal_awards2latex_far
from .student_awards2latex_far import student_awards2latex_far
from .service2latex_far import service2latex_far
from .reviews2latex_far_publons import reviews2latex_far_publons
from .reviews2latex_far_orcid import reviews2latex_far_orcid
from .teaching2latex_far import teaching2latex_far
from .advising2latex_far import advising2latex_far	

from . import global_prefs

pubfiles = ['Journal','Refereed','Book','Conference','Patent','Invited']

def make_far_tables(config,table_dir):
	# default to writing entire history
	years = config.getint('years')
	
	make_cv_tables(config,table_dir)
	
	# override faculty source to be relative to CV folder
	faculty_source = config['data_dir']

	# Personal Awards
	if config.getboolean('PersonalAwards'):
		print('Updating personal awards table')
		fpawards = open(table_dir +os.sep +'PersonalAwards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['PersonalAwardsFile'])
		nrows = personal_awards2latex_far(fpawards,years,filename)
		fpawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'PersonalAwards.tex')
	
	# Student Awards
	if config.getboolean('StudentAwards'):
		print('Updating student awards table')
		fsawards = open(table_dir +os.sep +'StudentAwards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['StudentAwardsFile'])
		nrows = student_awards2latex_far(fsawards,years,filename)	
		fsawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'StudentAwards.tex')
	
	# Service Activities
	if config.getboolean('Service'):
		print('Updating service table')
		fservice = open(table_dir +os.sep +'Service.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ServiceFile'])
		nrows = service2latex_far(fservice,years,filename)	
		fservice.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Service.tex')
			
	# Undergraduate Advising Counts
	filename = faculty_source +os.sep +"Service" +os.sep + "advisee counts.xlsx"
	if Path(filename).is_file():
		print('Updating advisee counts')
		df = pd.read_excel(filename,skiprows=0)
		nadvisees = df["Count Distinct Name"].iloc[-1]
		fadv = open(table_dir +os.sep +'AdviseeCounts.tex', 'w') # file to write
		fadv.write("Current undergraduate advisees: " +str(nadvisees) +" \\par\n")
		fadv.close()

	#Undergraduate Advising Evaluations
	filename = faculty_source +os.sep +"Service" +os.sep + "advising evaluation data.xlsx"
	if Path(filename).is_file():
		print('Updating advisee evals')
		f = open(table_dir +os.sep +'AdvisingEvals.tex', 'w') # file to write
		advising2latex_far(f,years,filename,private=False)
		f.close()
		
	# Prospective Visit Counts
	filename = faculty_source +os.sep +"Service" +os.sep + "prospective visit data.xlsx"
	if Path(filename).is_file():
		print('Updating prospective visit counts')
		df = pd.read_excel(filename,skiprows=0)
		nvisits = df["Visits"].iloc[-1]
		ndeposits = df["Deposits"].iloc[-1]
		nyear = df["Year"].iloc[-1]
		f = open(table_dir +os.sep +'ProspectiveVisits.tex', 'w') # file to write
		f.write(f"Prospective visits in {nyear}: {nvisits} with {ndeposits} deposits \\par\n")
		f.close()
	
	#Reviewing
	if config.getboolean('Reviews'):
		print('Updating reviews table')
		freviews = open(table_dir +os.sep +'Reviews.tex', 'w', encoding="utf-8") # file to write
		file_path = Path(config['ReviewsFile'])
		if file_path.exists():
			filename = os.path.join(faculty_source,config['ReviewsFile'])
			nrows = reviews2latex_far_publons(freviews,years,filename)
		else:
			nrows = reviews2latex_far_orcid(freviews,config["orcid"],years)
		freviews.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Reviews.tex')
	
	# Undergraduate Research
	if config.getboolean('UndergradResearch'):
		print('Updating undergraduate research table')
		fur = open(table_dir +os.sep +'UndergradResearch.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['UndergradResearchFile'])
		nrows = UR2latex_far(fur,years,filename)	
		fur.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'UndergradResearch.tex')
	
	# Teaching
	if config.getboolean('Teaching'):
		print('Updating teaching table')
		fteaching = open(table_dir +os.sep +'Teaching.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['TeachingFile'])
		nrows = teaching2latex_far(fteaching,years,filename)	
		fteaching.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Teaching.tex')

def main(argv = None):
	warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
	parser = argparse.ArgumentParser(description='This script creates a far using python and LaTeX plus provided data')
	add_default_args(parser)
	parser.add_argument('-p','--pandoc', help='Create a .docx far using pandoc', action='store_true')

	[configuration,args] = read_args(parser,argv)
	config = configuration['CV']
	process_default_args(config,args)
	global_prefs.usePandoc = args.pandoc
	
	stem = config['LaTexFile'][:-4]
	folder = "Tables_" +stem
	make_far_tables(config,folder)
	
	if global_prefs.usePandoc:
		docxfile = config['LaTexFile'][0:-4] +".docx"
		subprocess.run(['pandoc','--citeproc','--csl=no-bib-full.csl','--toc',config['LaTexFile'],'-o',docxfile],check=True)
	else:
		typeset(config,stem,['xelatex',config['LaTexFile']])

if __name__ == "__main__":
	main()

