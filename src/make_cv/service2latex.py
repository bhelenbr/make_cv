#! /usr/bin/env python3

# Python code to output service data in nice latex table

# import modules
import pandas as pd
import os
import sys
import argparse
import re
import io
from datetime import date

from .stringprotect import str2latex
from .stringprotect import years2range

def read_service_data(inputfile,years,ExcludeColumn=None):
	"""Read the Data sheet of a service-style excel file (Description, Type, Term, Calendar Year)
	and keep only the last [years] years.  Returns None if the file can't be read."""
	try:
		source_data = pd.read_excel(inputfile,sheet_name="Data")
		if ExcludeColumn is not None and ExcludeColumn in source_data.columns:
			source_data = source_data[source_data[ExcludeColumn] != True]
	except OSError:
		print("Could not open/read file: " + inputfile)
		return(None)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		source_data = source_data[source_data['Calendar Year'].apply(lambda x: int(x)) >= begin_year]

	source_data = source_data.copy()
	source_data['Type'] = source_data['Type'].str.strip()
	return(source_data)

def write_service_entries(f,source_data,name,max_rows=-1):
	"""Write \\entry* lines for one Type, most recent first.  Returns the number of rows written."""
	table = source_data[source_data.Type == name].pivot_table(columns=['Calendar Year'], values=['Term'], index=['Type', 'Description'], aggfunc={'Term': 'count'},observed=False)
	df = table.reset_index()
	df = df.fillna(0)
	nrows = df.shape[0]
	if nrows == 0:
		return(0)

	ncols = df.shape[1]
	maxyear = [0] * nrows
	for count in range(0,nrows):
		for year in range(2,ncols):
			if (df.iloc[count,year] > 0):
				maxyear[count] = year
	df["maxyear"] = maxyear
	df.sort_values(by=["maxyear","Description"],inplace=True,ascending=[False,True])

	if max_rows > 0 and nrows > max_rows:
		nrows = max_rows

	count = 0
	while count < nrows:
		# make date string from the actual years with entries
		years_list = [df.columns[year][1] for year in range(2,ncols) if df.iloc[count,year] > 0]
		date_string = years2range(years_list)
		f.write("\\entry*[" +date_string +"] " +str2latex(df.iloc[count,1]) +"\n")
		count += 1
	return(nrows)

def service2latex(f,years,inputfile,name,max_rows=-1,ExcludeColumn=None):
	"""Write all service activities as one rubric titled [name] with a subrubric for each Type."""
	source_data = read_service_data(inputfile,years,ExcludeColumn)
	if source_data is None or source_data.shape[0] == 0:
		return(0)

	f.write("\\begin{rubric}{" +name +"}\n")
	totalrows = 0
	for type_name in source_data.Type.unique():
		entries = io.StringIO()
		nrows = write_service_entries(entries,source_data,type_name,max_rows=max_rows)
		if nrows > 0:
			f.write("\\subrubric{" +type_name +"}\n")
			f.write(entries.getvalue())
		totalrows += nrows
	f.write("\\end{rubric}\n")
	return(totalrows)

def type2filename(type_name):
	"""File-name stem for a Type: letters and digits only (e.g. 'Committee Work' -> 'CommitteeWork')"""
	return(re.sub(r'[^A-Za-z0-9]', '', type_name))

def service2latex_separate(table_dir,stem,years,inputfile,max_rows=-1,ExcludeColumn=None):
	"""Write each Type to its own rubric file <table_dir>/<stem>_<Type>.tex, with the Type as the
	rubric title.  Type names are reduced to letters and digits for the file name.
	Returns the total number of rows written."""
	source_data = read_service_data(inputfile,years,ExcludeColumn)
	if source_data is None or source_data.shape[0] == 0:
		return(0)

	totalrows = 0
	for type_name in source_data.Type.unique():
		if not isinstance(type_name,str) or type2filename(type_name) == "":
			continue
		filename = os.path.join(table_dir,stem +"_" +type2filename(type_name) +".tex")
		with open(filename,'w') as f:
			f.write("\\begin{rubric}{" +type_name +"}\n")
			nrows = write_service_entries(f,source_data,type_name,max_rows=max_rows)
			f.write("\\end{rubric}\n")
		if nrows == 0:
			os.remove(filename)
		totalrows += nrows
	return(totalrows)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs service data to a latex table that shows a list of service activities in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="0",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = service2latex(f,args.years,args.inputfile,'Service')
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)
