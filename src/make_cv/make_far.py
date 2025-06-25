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


from .create_config import create_config
from .create_config import verify_config
from .publons2excel import publons2excel
from .bib_add_citations import bib_add_citations
from .bib_get_entries import bib_get_entries
from .bib_add_student_markers import bib_add_student_markers
from .bib_add_keywords import bib_add_keywords
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
from .publons2latex_far import publons2latex_far
from .teaching2latex_far import teaching2latex_far
	

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
	
	if config.getboolean('Reviews'):
		print('Updating reviews table')
		freviews = open(table_dir +os.sep +'Reviews.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ReviewsFile'])
		nrows = publons2latex_far(freviews,years,filename)
		freviews.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Reviews.tex')
	
	# Undergraduate Research
	if config.getboolean('UndergradResearch'):
		print('Updating undergraduate research table')
		fur = open(table_dir +os.sep +'UndergraduateResearch.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['UndergradResearchFile'])
		nrows = UR2latex_far(fur,years,filename)	
		fur.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'UndergraduateResearch.tex')
	
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

	[configuration,args] = read_args(parser,argv)
	config = configuration['CV']
	process_default_args(config,args)
	
	stem = config['LaTexFile'][:-4]
	folder = "Tables_" +stem
	make_far_tables(config,folder)
	typeset(config,stem,['xelatex',config['LaTexFile']])

if __name__ == "__main__":
	main()

