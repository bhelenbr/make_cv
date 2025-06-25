#! /usr/bin/env python3
# Script to create cv
# must be executed from Faculty/CV folder
# script folder must be in path
import os
import sys
import subprocess
import glob
import shutil
import configparser
import argparse
import warnings

from .make_far import make_far_tables
from .make_cv import make_cv_tables
from .make_cv import add_default_args
from .make_cv import process_default_args
from .make_cv import read_args
from .make_cv import sections
from .make_cv import typeset

from .create_config import create_config
from .create_config import verify_config

def main(argv = None):
	warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
	parser = argparse.ArgumentParser(description='This script creates a cv using python and LaTeX plus provided data')
	add_default_args(parser)
	
	[configuration,args] = read_args(parser,argv)
	
	config = configuration['CV']
	process_default_args(config,args)
	
	stem = config['LaTexFile'][:-4]
	folder = "Tables_" +stem
	make_far_tables(config,folder)
	typeset(config,stem,["mk4ht", "htlatex",config['LaTexFile'],"xhtml,3,next,charset=utf-8,pmathml","-cunihtf -utf8 -cvalidate"])		
	
	# extra cleanup
	for file in ["web.4ct","web.4tc","web.dvi","web.idv","web.tmp","web.xref","web.bdf.bbl","web.bdf.blg","web.lg"]:
		try:
			os.remove(file)
		except OSError as err:
			print("")

if __name__ == "__main__":
	main()
