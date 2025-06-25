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
import inspect
from pathlib import Path
import datetime
import warnings

from .create_config import create_config
from .create_config import verify_config
from .publons2excel import publons2excel
from .bib_add_citations import bib_add_citations
from .bib_get_entries import bib_get_entries
from .bib_get_entries_orcid import bib_get_entries_orcid
from .bib_add_student_markers import bib_add_student_markers
from .bib_add_keywords import bib_add_keywords
from .grants2latex_far import grants2latex_far
from .props2latex_far import props2latex_far
from .UR2latex import UR2latex
from .bib2latex_far import bib2latex_far
from .thesis2latex_far import thesis2latex_far
from .personal_awards2latex import personal_awards2latex
from .student_awards2latex import student_awards2latex
from .service2latex import service2latex
from .publons2latex import publons2latex
from .teaching2latex import teaching2latex
from .shortformteaching import shortformteaching
	
	
pub_categories = ['journal','conference','patent','book','invited','refereed']
other_sections = ['PersonalAwards','StudentAwards','Service','Reviews','GradAdvisees','UndergradResearch','Teaching','Grants','Proposals'] 
sections = pub_categories +other_sections
datafiles = ['Scholarship','PersonalAwards','StudentAwards','Service','Reviews','CurrentGradAdvisees','GradTheses','UndergradResearch','Teaching','Grants','Proposals']

def getSectionVals(config,section):
	include = config.getboolean(section)
	years = config.getint(section +'Years')
	max_pubs = config.getint(section +'Count')
	defaultyears = config.getint('Years')
	if years < 0:
		years = defaultyears
	return([include,years,max_pubs])
	
def make_cv_tables(config,table_dir):
	# override faculty source to be relative to CV folder
	faculty_source = config['data_dir']
	
	if not os.path.exists(table_dir):
		os.makedirs(table_dir)
	
# 	# Scholarly Works
	print('Updating scholarship tables')
	filename = os.path.join(faculty_source,config['ScholarshipFile'])
	if os.path.isfile(filename):
		for name in pub_categories:
			[include,years,max_pubs] = getSectionVals(config,name)
			if include:
				# allow possibility of overriding category name 
				category = name
				if name +"Key" in config.keys():
					category = config[name +"Key"]
				with open(table_dir +os.sep +name +".tex", 'w') as fpubs:
					nrecords = bib2latex_far(fpubs,filename,[category],years=years,max_pubs=max_pubs)
				if not(nrecords > 0):
					os.remove(table_dir+os.sep +name +".tex")
	
	# Personal Awards
	[include,years,max_rows] = getSectionVals(config,'PersonalAwards')
	if include:
		print('Updating personal awards table')
		fpawards = open(table_dir +os.sep +'PersonalAwards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['PersonalAwardsFile'])
		nrows = personal_awards2latex(fpawards,years,filename,max_rows=max_rows)
		fpawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'PersonalAwards.tex')
	
	# Student Awards
	[include,years,max_rows] = getSectionVals(config,'StudentAwards')
	if include:
		print('Updating student awards table')
		fsawards = open(table_dir +os.sep +'StudentAwards.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['StudentAwardsFile'])
		nrows = student_awards2latex(fsawards,years,filename,max_rows=max_rows)	
		fsawards.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'StudentAwards.tex')
	
	# Service Activities
	[include,years,max_rows] = getSectionVals(config,'Service')
	if include:
		print('Updating service table')
		fservice = open(table_dir +os.sep +'Service.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ServiceFile'])
		nrows = service2latex(fservice,years,filename,'Service',max_rows=max_rows)	
		fservice.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Service.tex')
		
	[include,years,max_rows] = getSectionVals(config,'ProfDevelopment')	
	if include:
		print('Updating professional development table')
		fprof_development = open(table_dir +os.sep +'ProfDevelopment.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ProfDevelopmentFile'])
		nrows = service2latex(fprof_development,years,filename,'Professional Development',max_rows=max_rows)	
		fprof_development.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'ProfDevelopment.tex')
	
	[include,years,max_rows] = getSectionVals(config,'Reviews')	
	if include:
		print('Updating reviews table')
		freviews = open(table_dir +os.sep +'Reviews.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ReviewsFile'])
		nrows = publons2latex(freviews,years,filename,max_rows=max_rows)
		freviews.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Reviews.tex')
	
	# Thesis Publications & Graduate Advisees
	[include,years,max_rows] = getSectionVals(config,'GradAdvisees')	
	if include:
		print('Updating graduate advisees table')
		fthesis = open(table_dir +os.sep +'GradAdvisees.tex', 'w') # file to write
		filename1 = os.path.join(faculty_source,config['CurrentGradAdviseesFile'])
		filename2 = os.path.join(faculty_source,config['GradThesesFile'])
		nrows = thesis2latex_far(fthesis,years,filename1,filename2,max_rows=max_rows)
		fthesis.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'GradAdvisees.tex')
	
	# Undergraduate Research
	[include,years,max_rows] = getSectionVals(config,'UndergradResearch')	
	if include:
		print('Updating undergraduate research table')
		fur = open(table_dir +os.sep +'UndergradResearch.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['UndergradResearchFile'])
		nrows = UR2latex(fur,years,filename,max_rows=max_rows)	
		fur.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'UndergradResearch.tex')
	
	# Teaching
	if config.getboolean('Teaching'):
		print('Updating teaching table')
		fteaching = open(table_dir +os.sep +'Teaching.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['TeachingFile'])
		if config.getboolean('ShortTeachingTable'):
			nrows = shortformteaching(fteaching,years,filename)
		else:
			nrows = teaching2latex(fteaching,years,filename)	
		fteaching.close()
		if not(nrows):
			os.remove(table_dir+os.sep +'Teaching.tex')
	
	[include,years,max_rows] = getSectionVals(config,'Grants')	
	if include:
		print('Updating grants table')
		fgrants = open(table_dir +os.sep +'Grants.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['GrantsFile'])
		nrows = grants2latex_far(fgrants,years,filename,max_rows=max_rows)
		fgrants.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'Grants.tex')
	
	# Proposals
	[include,years,max_rows] = getSectionVals(config,'Proposals')	
	if include:
		print('Updating proposals table')
		fprops = open(table_dir +os.sep +'Proposals.tex', 'w') # file to write
		filename = os.path.join(faculty_source,config['ProposalsFile'])
		nrows = props2latex_far(fprops,years,filename,max_rows=max_rows)	
		fprops.close()
		if not(nrows):
			os.remove(table_dir +os.sep +'Proposals.tex')
	

def add_default_args(parser):
	parser.add_argument('-b','--begin', help='create default directory structure & files named <>',)
	parser.add_argument('-d','--data_dir', help='the name of root directory containing the data folders')
	parser.add_argument('-f','--configfile', default='make_cv.cfg', help='the configuration file, default is make_cv.cfg')
	parser.add_argument('-F','--file', help='override data file location in config file.  Format is NAME=<file name> where NAME can be: Scholarship, PersonalAwards, StudentAwards, Service, Reviews, CurrentGradAdvisees, GradTheses, UndergradResearch, Teaching, Proposals, Grants', action='append')
	parser.add_argument('-S','--ScraperID', help='ScraperID (not necessary, but avoids Google blocking requests)')
	parser.add_argument('-s','--UseScraper', help='Use scraper to avoid blocking by Google',  choices=['true','false'])
	parser.add_argument('-G','--GoogleID', help='GoogleID (used for finding new publications()')
	parser.add_argument('-g','--GetNewScholarshipEntries', help='search for and add new entries from the last N (default 1) years to the .bib file', nargs='?', const='1')
	parser.add_argument('-I','--SearchForDOIs', help='search for and add missing DOIs to the .bib file',  choices=['true','false'])
	parser.add_argument('-c','--UpdateCitations', help='update citation counts',  choices=['true','false'])
	parser.add_argument('-C','--IncludeCitationCounts', help='put citation counts in cv', choices=['true','false'])
	parser.add_argument('-m','--UpdateStudentMarkers', help='update the student author markers', choices=['true','false'])
	parser.add_argument('-M','--IncludeStudentMarkers', help='put student author markers in cv', choices=['true','false'])
	parser.add_argument('-e','--exclude', help='exclude section from cv', choices=sections,action='append')
	parser.add_argument('-T','--Timestamp', help='Include last update timestamp at the bottom of cv', nargs='?', const='true')
	parser.add_argument('-orc','--GetNewScholarshipEntriesusingOrcid', help='search for and add new entries from the last N (default 1) years to the .bib file', nargs='?', const='1')
	parser.add_argument('-orcid','--ORCID', help='ORCID (used for finding new publications()')
	parser.add_argument('-y','--years', help='number of years of data to include in tables',type=int)
	parser.add_argument('-n','--NoCleanUp', help='Don''t delete autogenerated LaTex files after typset', nargs='?', const='true')

def read_args(parser,argv):
	if argv is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(argv)
		
		
	if args.begin is not None:
		# Set up file structure and exit
		if os.path.exists(args.begin):
			print("This directory already exists.  Please provide a different directory name")
			exit()
		else:
			dst = Path(args.begin)
			#dst = path.parent.absolute()
			myDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
			shutil.copytree(myDir +os.sep +"files",dst)
			print('Directory created.  Now type "cd ' +args.begin +'/make_cv/CV" to change to that folder and type "make_cv" to create sample')
			exit()

	configuration = configparser.ConfigParser()
	configuration.read(args.configfile)
	
	ok = verify_config(configuration)
	if (not ok):
		print("Incomplete or Unreadable configuration file " +args.configfile +".\n") 
		YN = input('Would you like to update configuration file named make_cv.cfg [Y/N]?')
		if YN == 'Y' or YN =='y':
			newconfig = create_config('make_cv.cfg',configuration)
			return(newconfig,args)
		elif YN =='N' or YN =='n':
			print("Couldn't proceed due to Incomplete or Unreadable configuration file")
			return
		else:
			return
		
	return([configuration,args])

def process_default_args(config,args):
	# override config with command line arguments
	if args.data_dir is not None: config['data_dir'] = args.data_dir
	if args.GoogleID is not None: config['GoogleID'] = args.GoogleID
	if args.ScraperID is not None: config['ScraperID'] = args.ScraperID
	if args.UseScraper is not None: config['UseScraper'] = args.UseScraper
	if args.UpdateCitations is not None: config['UpdateCitations'] = args.UpdateCitations
	if args.UpdateStudentMarkers is not None: config['UpdateStudentMarkers'] = args.UpdateStudentMarkers
	if args.GetNewScholarshipEntries is not None: config['GetNewScholarshipEntries'] = args.GetNewScholarshipEntries
	if args.SearchForDOIs is not None: config['SearchForDOIs'] = args.SearchForDOIs
	if args.IncludeStudentMarkers is not None: config['IncludeStudentMarkers'] = args.IncludeStudentMarkers
	if args.IncludeCitationCounts is not None: config['IncludeCitationCounts'] = args.IncludeCitationCounts
	if args.Timestamp is not None: config['Timestamp'] = args.Timestamp
	if args.GetNewScholarshipEntriesusingOrcid is not None: config['GetNewScholarshipEntriesusingOrcid'] = args.GetNewScholarshipEntriesusingOrcid
	if args.ORCID is not None: config['ORCID'] = args.ORCID
	if args.years is not None: config['Years'] = args.years
	
	if args.NoCleanUp is not None: 
		config['NoCleanUp'] = args.NoCleanUp
	else:
		config['NoCleanUp'] = 'false'
	
	if args.exclude is not None:
		for section in args.exclude:
			config[section] = 'false'
	
	if args.file is not None:
		for file in args.file:
			strings = file.split('=')
			if len(strings) == 2 and strings[0] in datafiles:
				config[strings[0]+'File'] = strings[1]
			else:
				print('Unable to parse filename ' + file)
				exit()
	
	
		
# 	argdict = vars(args)
# 	for file in files:
# 		if argdict[file+'File'] is not None: config[file+'File'] = argdict[file+'File']
# 		if argdict[file+'Folder'] is not None: config[file+'Folder'] = argdict[file+'Folder']
		
	# do the preprocessing stuff first
	faculty_source = config['data_dir']
	
	# convert a reviewin history json file from Web of Science
	reviewfile = config['ReviewsFile']
	name_extension_tuple = os.path.splitext(reviewfile)
	if name_extension_tuple[1] == '.json':
		xls = os.path.join(faculty_source,name_extension_tuple[0] +'.xlsx')
		json = os.path.join(faculty_source,reviewfile)
		if os.path.exists(json):
			print('Converting json reviewing file')
			publons2excel(json,xls)
		config['ReviewsFile'] = name_extension_tuple[0] +'.xlsx'
		
	if config['UseScraper'] == 'false':
		scraperID = None
	else:
		scraperID = config['ScraperID']
		
	if config['GetnewScholarshipEntries'] == 'false':
		config['GetnewScholarshipEntries'] = '0'
	elif config['GetnewScholarshipEntries'] == 'true':
		config['GetnewScholarshipEntries'] = '1'
	
	if config.getint('GetNewScholarshipEntries') != 0:
		print("Trying to find new .bib entries from Google Scholar")
		if config['GoogleID'] == "":
			print("Can't find new scholarship entries without providing Google ID")
			exit()
		filename = os.path.join(faculty_source,config['ScholarshipFile'])
		backupfile = os.path.join(faculty_source,'backup1.bib')
		shutil.copyfile(filename,backupfile)
		nyears = int(config['GetNewScholarshipEntries'])
		bib_get_entries(backupfile,config['GoogleID'],nyears,filename,scraperID)
		os.remove(backupfile)
	
	if config.getint('GetNewScholarshipEntriesusingOrcid') != 0:
		print("Trying to find new .bib entries from ORCID")
		if config['ORCID'] == "":
			print("Can't find new scholarship entries without providing ORCID")
			exit()
		filename = os.path.join(faculty_source,config['ScholarshipFile'])
		backupfile = os.path.join(faculty_source,'backup1.bib')
		shutil.copyfile(filename,backupfile)
		nyears = int(config['GetNewScholarshipEntries'])
		bib_get_entries_orcid(backupfile,config['ORCID'],nyears,filename)
		os.remove(backupfile)
		
	# add/update citations counts in .bib file	
	if config.getboolean('UpdateCitations'):
		print("Updating citation counts using Google Scholar")
		if config['GoogleID'] == "":
			print("Can't update without providing Google ID")
			exit()
		filename = os.path.join(faculty_source,config['ScholarshipFile'])
		backupfile = os.path.join(faculty_source,'backup2.bib')
		shutil.copyfile(filename,backupfile)
		bib_add_citations(backupfile,config['GoogleID'],filename,scraperID)
		os.remove(backupfile)
		
	# add/update citations counts in .bib file	
	if config.getboolean('UpdateStudentMarkers'):
		print("Updating student markers in .bib file")
		filename = os.path.join(faculty_source,config['ScholarshipFile'])
		backupfile = os.path.join(faculty_source,'backup3.bib')
		shutil.copyfile(filename,backupfile)
		cur_grads = os.path.join(faculty_source,config['CurrentGradAdviseesFile'])
		gradfile = os.path.join(faculty_source,config['GradThesesFile'])
		ugradfile = os.path.join(faculty_source,config['UndergradResearchFile'])
		bib_add_student_markers(100,ugradfile,gradfile,cur_grads,backupfile,filename)
		os.remove(backupfile)
		
	if config.getboolean('SearchForDOIs'):
		filename = os.path.join(faculty_source,config['ScholarshipFile'])
		backupfile = os.path.join(faculty_source,'backup4.bib')
		shutil.copyfile(filename,backupfile)
		subprocess.run(["btac", "-i","-v","-c","doi","-m",filename])
		# I think btac deletes the comments from a .bib file so I need to add them back in?

	# Check for missing keywords in .bib file
	filename = os.path.join(faculty_source,config['ScholarshipFile'])
	if os.path.isfile(filename):
		print('Checking for .bib entries that are missing type specifiers')
		backupfile = os.path.join(faculty_source,'backup.bib')
		shutil.copyfile(filename,backupfile)
		bib_add_keywords(backupfile,filename)
	try:
		os.remove(backupfile)
	except:
		pass


def add_timestamp_to_cv():
	# Get current timestamp
	current_time = datetime.datetime.now().strftime("%B %d, %Y")
	# Create timestamp in LaTeX format
	timestamp_tex = f"""
		% Add timestamp to bottom of CV
		\\vspace*{{\\fill}}
		\\begin{{center}}
		\\small
		Last updated: {current_time}
		\\end{{center}}
		"""
	
	# Write timestamp to a separate file
	with open('timestamp.tex', 'w') as f:
		f.write(timestamp_tex)
		
def typeset(config,filename,command):
	# Create exclusion file
	with open('exclusions.tex', 'w') as exclusions:
		exclusions.write('\\makeatletter\n\\def\\input@path{{Tables_' +filename +'/}{' +config['bio_dir'] +'/}} % Add folder to file search path\n\\makeatother\n')
		for section in sections:
			if not config.getboolean(section): exclusions.write('\\setboolean{' +section +'}{false}\n')
		if not config.getboolean('IncludeCitationCounts'): exclusions.write('\\DeclareFieldFormat{citations}{}\n')
		if not config.getboolean('IncludeStudentMarkers'):
			exclusions.write('\\renewcommand{\\us}{}\n')
			exclusions.write('\\renewcommand{\\gs}{}\n')
		exclusions.write('\n')

	
	if "Timestamp" in config.keys() and config.getboolean("Timestamp"):
		# Create timestamp
		add_timestamp_to_cv()
	else:
		with open('timestamp.tex', 'w') as f:
			f.write('')

	with open('biblatex-dm.cfg', 'w') as configLatex:
		configLatex.write('\\DeclareDatamodelFields[type=field, datatype=integer, nullok=true]{citations}\n')
		configLatex.write('\\DeclareDatamodelEntryfields{citations}\n')
	
	bcffile = filename +".bcf"
	pdffile = filename +".pdf"
	#subprocess.run([command, "cv.tex"],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT) 
	print("\ntypesetting pass 1\n")
	subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT) 
	
	print("\ncreating bibliography\n")
	subprocess.run(["biber", bcffile]) 
	print("\ntypesetting pass 2\n")
	subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
	print("Trying to delete " +filename +".pdf file.  If this gets stuck, delete " +filename +".pdf yourself and the compilation should continue")
	print("If it doesn't, hit ctrl-c, delete " +filename +".pdf and try again")
	while True:
		try:
			if os.path.exists(pdffile):
				os.remove(pdffile)
			break
		except OSError as err:
			continue
	print("\ntypesetting pass 3\n")
	subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT) 
	print("\ntypesetting pass 4\n")
	ps = subprocess.run(command)
	
	# cleanup
	if "NoCleanUp" in config.keys() and not(config.getboolean("NoCleanUp")):
		for file in [filename +".aux",filename +".bbl",filename +".bcf",filename +".blg",filename +".log",filename +".out",filename +".run.xml","biblatex-dm.cfg","exclusions.tex",filename +".toc","timestamp.tex"]:
			try:
				os.remove(file)
			except OSError as err:
				pass


def main(argv = None):
	warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
	parser = argparse.ArgumentParser(description='This script creates a cv using python and LaTeX plus provided data')
	add_default_args(parser)
	
	[configuration,args] = read_args(parser,argv)
	
	config = configuration['CV']
	process_default_args(config,args)
	
	stem = config['LaTexFile'][:-4]
	folder = "Tables_" +stem
	make_cv_tables(config,folder)
	typeset(config,stem,['xelatex','-interaction=batchmode',config['LaTexFile']])

if __name__ == "__main__":
	SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.dirname(SCRIPT_DIR))
	main()
