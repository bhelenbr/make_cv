#!/usr/bin/env python

import configparser

sections = {'Journal','Refereed','Book','Conference','Patent','Invited','PersonalAwards','StudentAwards','Service','Reviews','GradAdvisees','UndergradResearch','Teaching','Grants','Proposals'} 

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
			
web_keys = {'IncludeStudentMarkers': 'true',
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
    config['DEFAULT'] = defaults        
    for key, value in files.items():
        config['DEFAULT'][key] = value
        
    config['CV'] = cv_keys
    for section in sections:
        config['CV'][section] = 'true'    
        
    config['FAR'] = far_keys
    for section in sections:
        config['FAR'][section] = 'true'     
        
    config['WEB'] = web_keys
    for section in sections:
        config['WEB'][section] = 'false' 
    
    config['WEB']['Journal'] = 'true'

    for section in old_config.sections():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in old_config.items(section):
            config[section][key] = value
    for key, value in old_config['DEFAULT'].items():
        config['DEFAULT'][key] = value 
    
    
    
    with open(filename, 'w') as configfile:
        config.write(configfile)
    
    return config
  
if __name__ == "__main__":
	create_config('cv.cfg')
