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

from .create_config import create_config
from .create_config import verify_config
from .publons2excel import publons2excel
from .bib_add_citations import bib_add_citations
from .bib_get_entries import bib_get_entries
from .bib_add_student_markers import bib_add_student_markers
from .bib_add_keywords import bib_add_keywords

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
	

sections = {'Journal','Refereed','Book','Conference','Patent','Invited','PersonalAwards','StudentAwards','Service','Reviews','GradAdvisees','UndergradResearch','Teaching','Grants','Proposals'} 
files = {'Scholarship','PersonalAwards','StudentAwards','Service','Reviews','CurrentGradAdvisees','GradTheses','UndergradResearch','Teaching','Proposals','Grants'} 


def make_far_tables(config,table_dir):
	# default to writing entire history
	years = config.getint('years')
	
	make_cv_tables(config,table_dir,years)
	
	# override faculty source to be relative to CV folder
	faculty_source = config['data_dir']

	# Personal Awards
	if config.getboolean('PersonalAwards'):
		print('Updating personal awards table')
		fpawards = open(table_dir +os.sep +'personal_awards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['PersonalAwardsFile'])
		nrows = personal_awards2latex_far(fpawards,years,filename)
		fpawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'personal_awards.tex')
	
	# Student Awards
	if config.getboolean('StudentAwards'):
		print('Updating student awards table')
		fsawards = open(table_dir +os.sep +'student_awards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['StudentAwardsFile'])
		nrows = student_awards2latex_far(fsawards,years,filename)	
		fsawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'student_awards.tex')
	
	# Service Activities
	if config.getboolean('Service'):
		print('Updating service table')
		fservice = open(table_dir +os.sep +'service.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ServiceFile'])
		nrows = service2latex_far(fservice,years,filename)	
		fservice.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'service.tex')
	
	if config.getboolean('Reviews'):
		print('Updating reviews table')
		freviews = open(table_dir +os.sep +'reviews.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ReviewsFile'])
		nrows = publons2latex_far(freviews,years,filename)
		freviews.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'reviews.tex')
	
	# Undergraduate Research
	if config.getboolean('UndergradResearch'):
		print('Updating undergraduate research table')
		fur = open(table_dir +os.sep +'undergraduate_research.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['UndergradResearchFile'])
		nrows = UR2latex_far(fur,years,filename)	
		fur.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'undergraduate_research.tex')
	
	# Teaching
	if config.getboolean('Teaching'):
		print('Updating teaching table')
		fteaching = open(table_dir +os.sep +'teaching.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['TeachingFile'])
		nrows = teaching2latex_far(fteaching,years,filename)	
		fteaching.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'teaching.tex')

def main(argv = None):
	parser = argparse.ArgumentParser(description='This script creates a far using python and LaTeX plus provided data')
	add_default_args(parser)
	parser.add_argument('-y','--years', help='number of years to include in far',type=int)

	[configuration,args] = read_args(parser,argv)
	
	config = configuration['FAR']
	
	process_default_args(config,args)
	if args.years is not None: config['Years'] = args.years

	make_far_tables(config,'Tables_far')
	typeset(config,'far',['xelatex','far.tex'])

if __name__ == "__main__":
	main()

