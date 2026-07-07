#!/usr/bin/env python

import configparser
import os

from . import global_prefs

sections = {name: 'true' for name in global_prefs.pub_categories + global_prefs.other_sections}
sections['References'] = 'false'

defaults = {'data_dir': '../..',
				'bio_dir': '../PersonalData',
				'UseWebScraper': 'false',
				'UpdateCitations': 'false',
				'UpdateStudentMarkers': 'false',
				'GetNewGoogleEntries': '0',
				'SearchForDOIs': 'false',
				'GetNewOrcidEntries':'0',
				'GetNewScopusEntries':'0',
				'SplitAdviseesAndTheses': 'false',
				'UsePandoc': 'false'}

cv_keys = {'Years': '-1',
			'LaTexFile':'cv.tex',
			'IncludeStudentMarkers': 'true',
			'IncludeCitationCounts': 'true',
			'ShortTeachingTable' : 'true', 
			'HideTeachingEvals' : 'false',
			'Timestamp': 'false',
			'ExcludeColumn': 'None'
			}

def load_personal_data(configuration):
	"""Read personal_data.txt from the given bio_dir and return dict of values.
	Keys returned (lowercase): googleid, webscraperid, scopusid, orcid
	If file does not exist, returns empty values.
	"""
	bio_dir = configuration['DEFAULT'].get('bio_dir')

	pdata = {'googleid': '', 'webscraperid': '', 'scopusid': '', 'orcid': ''}
	if bio_dir is None:
		return pdata
	pfile = os.path.join(bio_dir, 'personal_data.txt')
	if (not os.path.isfile(pfile)):
		with open(pfile, 'w', encoding='utf-8') as f:
			f.write('# Personal data (IDs) for make_cv\n')
			f.write('# Fill in the values without quotes. Example:\n')
			f.write('# googleid = ABCDEFGHIJ\n')
			for k in ['googleid', 'webscraperid', 'scopusid', 'orcid']:
				if k in configuration['DEFAULT'].keys():
					f.write(f'{k} = {configuration["DEFAULT"][k]}\n')
				else:
					f.write(f'{k} = \n')
		return(configuration)
	else:
		with open(pfile, 'r', encoding='utf-8') as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith('#'):
					continue
				if '=' in line:
					key, val = line.split('=', 1)
				elif ':' in line:
					key, val = line.split(':', 1)
				else:
					continue
				key = key.strip().lower()
				val = val.strip()
				if key in pdata:
					pdata[key] = val
		for k, v in pdata.items():
			configuration['DEFAULT'][k] = v
		return configuration
	
	return(None)

def verify_config(config):
	for key in defaults:
		if not key in config['DEFAULT'].keys():
			print(key +' is missing from config file')
			return False
	
	for key in global_prefs.files.keys():
		if not key in config['DEFAULT'].keys():
			print(key +' is missing from config file')
			return False
	
	for sec in ['CV']:	
		if not config.has_section(sec):
			print(sec +' is missing from config file') 
			return False
		else:
			for key in sections:
				if not key in config[sec].keys():
					print(key +' is missing from config file')
					return False
				if not key +"Years" in config[sec].keys():
					print(key +'Years is missing from config file')
					return False
				if not key +"Count" in config[sec].keys():
					print(key +'Count is missing from config file')
					return False
				
			
	for key in cv_keys:
		if not key in config['CV'].keys():
			print(key +' is missing from config file')
			return False
	
	return True

def create_config(filename, old_config=None):
	config = configparser.ConfigParser()
	config['DEFAULT'] = defaults | global_prefs.files	
	sectionYears = {str(key) + 'Years': "-1" for key in sections}
	sectionCounts = {str(key) + 'Count': "-1" for key in sections}
	config['CV'] = cv_keys | sections | sectionYears | sectionCounts

	if not old_config == None:
		if old_config.has_section('CV'):
			for key in old_config['CV']:
					if key in config['DEFAULT']:
						config['DEFAULT'][key] = old_config['CV'][key]
						
		for section in config.sections():
			if old_config.has_section(section):
				for key in old_config[section]:
					if key in config[section] and not key in config['DEFAULT']:
						config[section][key] = old_config[section][key]
	
	with open(filename, 'w') as configfile:
		config.write(configfile)

	return config
  
if __name__ == "__main__":
	create_config('cv.cfg')
