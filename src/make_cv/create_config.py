#!/usr/bin/env python

import configparser

sections = {'PersonalAwards': 'true',
				'Journal': 'true',
				'Refereed': 'true',
				'Book': 'true',
				'Patent': 'true',
				'Conference': 'true',
				'Invited': 'true',
				'Service': 'true',
				'Reviews': 'true',
				'StudentAwards': 'true',
				'GradAdvisees': 'true',
				'UndergradResearch': 'true',
				'Teaching': 'true',
				'Grants': 'true',
				'Proposals': 'true'} 

defaults = {'data_dir': '..',
				'GoogleID': '',
				'ScraperID': '',
				'UseScraper': 'false',
				'UpdateCitations': 'false',
				'UpdateStudentMarkers': 'false',
				'GetNewScholarshipEntries': '0',
				'SearchForDOIs': 'false',
	   			'ORCID': '',
	   			'GetNewScholarshipEntriesusingOrcid':'0'}

files = {'ScholarshipFile': 'Scholarship/scholarship.bib',
			'PersonalAwardsFile': 'Awards/personal awards data.xlsx',
			'StudentAwardsFile': 'Awards/student awards data.xlsx',
			'ServiceFile': 'Service/service data.xlsx',
			'ReviewsFile': 'Service/reviews data.json',
			'CurrentGradAdviseesFile':'Scholarship/current student data.xlsx',
			'GradThesesFile': 'Scholarship/thesis data.xlsx',
			'UndergradResearchFile': 'Service/undergraduate research data.xlsx',
			'TeachingFile': 'Teaching/teaching evaluation data.xlsx',
			'ProposalsFile': 'Proposals & Grants/proposals & grants.xlsx',
			'GrantsFile': 'Proposals & Grants/proposals & grants.xlsx'} 
			
cv_keys = {'IncludeStudentMarkers': 'true',
			'IncludeCitationCounts': 'true',
	   		'ShortTeachingTable' : 'true', 
	   		'Timestamp': 'false'}
			
far_keys = {'Years': '3',
			'IncludeStudentMarkers': 'true',
			'IncludeCitationCounts': 'true'}
			
web_keys = {'Years': '-1',
			'IncludeStudentMarkers': 'true',
			'IncludeCitationCounts': 'true'}

def verify_config(config):
	for key in defaults:
		if not key in config['DEFAULT'].keys():
			print(key +' is missing from config file')
			return False
	
	for key in files:
		if not key in config['DEFAULT'].keys():
			print(key +' is missing from config file')
			return False
	
	for sec in ['CV','FAR','WEB']:	
		if not config.has_section(sec):
			print(sec +' is missing from config file') 
			return False
		else:
			for key in sections:
				if not key in config[sec].keys():
					print(key +' is missing from config file')
					return False
			
	for key in cv_keys:
		if not key in config['CV'].keys():
			print(key +' is missing from config file')
			return False
	
	for key in far_keys:
		if not key in config['FAR'].keys():
			print(key +' is missing from config file')
			return False
			
	for key in web_keys:
		if not key in config['WEB'].keys():
			print(key +' is missing from config file')
			return False
	
	return True

def create_config(filename, old_config=None):
	config = configparser.ConfigParser()
	config['DEFAULT'] = defaults | files	
	config['CV'] = cv_keys | sections
	config['FAR'] = far_keys | sections
	config['WEB'] = web_keys | sections

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
