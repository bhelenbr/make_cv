#! /usr/bin/env python3

import re

def str2latex(text):
	text = str(text)
	if text=="nan":
		return("")
	else:
		# Count number of $ signs if even assume latex string
		if text.count('$') == 0 or text.count('$') % 2 == 1:
			replacements = {"&":"\\&","$":"\\$","_":"\\_","#":"\\#"}
			for i, j in replacements.items():
				text = text.replace(i, j)
		return text
		
# This function should convert any name formatting in a document or file to that of the standardized format, which is:
# First initial. Middle initial. Last Name - Example > B.T. Helenbrook
# Input is to be taken as a string
# This will convert the following formats
# B. T. Helenbrook, N. Bagheri-Sadeghi (maintains this)
# Appleton, Jay (only one name allowed)
# Jay Appleton, Mike Ambrosia (multiple names separated by commas)

# if there is only one comma it could be a single name last, first
# or it could be two names in a list
# if is the former the first string before the comma will have no spaces or periods
# if it is the latter the first string before the comma will either have a space or a period

# if there are multiple commas it is definitely a comma separated list
# it may or may not have the word "and" in it

# it may also be an " and " separated list in this case it will have no commas
# and the word " and " in it

def split_names(name_list):
	# get rid of ", and" and replace with just ","
	name_list = re.sub('^(.*), *?and (.*)$','\\1, \\2',name_list)
	ncommas = name_list.count(',')
	nands = name_list.count(' and ')
	if name_list.count(';') > 0:
		list_of_names = name_list.split(";")
	elif nands > 0:
		list_of_names = name_list.split(" and ")
	elif ncommas > 1: # Multiple commas
		list_of_names = name_list.split(",")
	elif ncommas == 1:
		list_of_names = name_list.split(",")
		if (list_of_names[0].strip().find(" ") == -1) & (list_of_names[0].strip().find(".") == -1):
			# this is a single word so it is a lastname
			# and this is just a single name in Helenbrook, Brian format
			list_of_names.clear()
			list_of_names.append(name_list)
	else:
		# Single name with no commas
		list_of_names = []
		list_of_names.append(name_list)
	for count,name in enumerate(list_of_names):
		list_of_names[count] = name.strip()
	return(list_of_names)
	
	
# This function puts a single name in standard form:
# John S. Smith
def first_last(initial_name):
	initial_name = initial_name.strip()
	
	# Deal with Jr. and Sr. last name endings
	initial_name = re.sub('^(.*)?[ ]* Jr\\.?(.*)$','\\1_Jr\\2',initial_name)
	initial_name = re.sub('^(.*)?[ ]* Sr\\.?(.*)$','\\1_Jr\\2',initial_name)
	
	if initial_name.find(',') != -1: # If any commas are detected
		#print("In Part 1: Commas Included")
		last_first = initial_name.split(',')
		#print(mod_name)
		last_name = last_first[0].strip()
		first_name = last_first[1].strip()# This is now whatever remains besides last name
	else:
		first_last = initial_name.split()
		last_name = first_last[-1]
		nlast= len(last_name)
		first_name = initial_name[0:len(initial_name)-nlast].strip()

	name = first_name +" " +last_name
	
	# Undo Jr. and Sr. Change
	name = name.replace('_Jr',' Jr.')
	name = name.replace('_Sr',' Sr.')
	return(name)
	
# Smith, John S. 
def last_first(initial_name):
	initial_name = initial_name.strip()
	
	# Deal with Jr. and Sr. last name endings
	initial_name = re.sub('^(.*)?[ ]* Jr\\.?(.*)$','\\1_Jr\\2',initial_name)
	initial_name = re.sub('^(.*)?[ ]* Sr\\.?(.*)$','\\1_Jr\\2',initial_name)
	
	if initial_name.find(',') != -1: # If any commas are detected
		#print("In Part 1: Commas Included")
		last_first = initial_name.split(',')
		#print(mod_name)
		last_name = last_first[0].strip()
		first_name = last_first[1].strip()# This is now whatever remains besides last name
	else:
		first_last = initial_name.split()
		last_name = first_last[-1]
		nlast= len(last_name)
		first_name = initial_name[0:len(initial_name)-nlast].strip()

	name = last_name +", " +first_name
	
	# Undo Jr. and Sr. Change
	name = name.replace('_Jr',' Jr.')
	name = name.replace('_Sr',' Sr.')
	return(name)
	
# This function puts a single name in standard abbreviated form:
# J. S. Smith
def abbreviate_name(initial_name,first_initial_only=False):
	initial_name = initial_name.strip()
	
	# Deal with Jr. and Sr. last name endings
	initial_name = re.sub('^(.*)?[ ]* Jr\\.?(.*)$','\\1_Jr\\2',initial_name)
	initial_name = re.sub('^(.*)?[ ]* Sr\\.?(.*)$','\\1_Jr\\2',initial_name)
	
	if initial_name.find(',') != -1: # If any commas are detected
		#print("In Part 1: Commas Included")
		last_first = initial_name.split(',')
		#print(mod_name)
		last_name = last_first[0].strip()
		first_name = last_first[1].strip()# This is now whatever remains besides last name
	else:
		first_last = initial_name.split()
		last_name = first_last[-1]
		nlast= len(last_name)
		first_name = initial_name[0:len(initial_name)-nlast].strip()
	
	# Splitting characters in String
	first_names = re.split('\\.| ', first_name)
	first_abbrev = ""
	for name in first_names:
		if (len(name) > 0):
			first_abbrev = first_abbrev +name[0] +". "
			if first_initial_only:
				break
	
	abbreviated_name = first_abbrev +last_name
	
	# Undo Jr. and Sr. Change
	abbreviated_name = abbreviated_name.replace('_Jr',' Jr.')
	abbreviated_name = abbreviated_name.replace('_Sr',' Sr.')
	return(abbreviated_name)
	

def abbreviate_name_list(name_list):
	list_of_names = split_names(name_list)
	name_string = abbreviate_name(list_of_names.pop(0))
	for count,name in enumerate(list_of_names):
		name_string += ", " +abbreviate_name(name)
	return(name_string)

if __name__ == "__main__":
	name = "B.T. Helenbrook"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Helenbrook, B. T."
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Brian Todd Helenbrook"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Helenbrook, Brian Todd"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	names = "B.T. Helenbrook; N. Bagheri; K. Visser"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B.T. Helenbrook, N. Bagheri, K. Visser"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B.T. Helenbrook, N. Bagheri, and K. Visser"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B.T. Helenbrook, N. Bagheri,and K. Visser"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B.T. Helenbrook, N. Bagheri"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B.T. Helenbrook and N. Bagheri"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "Helenbrook, B. T. and Bagheri, N."
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "Helenbrook, B. T. and Bagheri, N. and Visser, K. D."
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	names = "B. T. Helenbrook and N. Bagheri and K. D. Visser"
	print('test split of name list ' +names)
	print(split_names(names))
	print(abbreviate_name_list(names))
	
	name = "Ken Adade Jr."
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Ken Adade Jr"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Ken AdadeJr"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))

	name = "Adade Jr., Ken"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))
	
	name = "Adade Jr, Ken"
	print('test abbreviation of single name ' +name)
	print(abbreviate_name(name))







	