#! /usr/bin/env python3

# Python code to output service data in nice latex table

# import modules
from datetime import date
import pandas as pd
import os
import sys
import argparse

from .stringprotect import str2latex


def service2latex_far(f,years,inputfile):
	source = inputfile # file to read
	try:
		source_data = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		source_data = source_data[source_data['Calendar Year'].apply(lambda x: int(x)) >= begin_year]

	source_data.sort_values(by=['Calendar Year', 'Term', 'Type', 'Description'], inplace=True, ascending = [False,True,True,True])
	df = source_data.reset_index()
	nrows = df.shape[0]

	if nrows > 0:
		f.write("\\begin{tabularx}{\\linewidth}{lllXl}\nYear & Term & Type & Description & Hours \\\\\n\\hline\n")
		count = 0
		newline=""
		while count < nrows:
			# make date string
			f.write(newline)
			f.write(str2latex(df.loc[count,"Calendar Year"]) + " & " +str2latex(df.loc[count,"Term"]) + " & " +str2latex(df.loc[count,"Type"]) + " & " +str2latex(df.loc[count,"Description"]) + " & " +str2latex(df.loc[count,"Hours/Semester"]))
			newline="\\\\\n"
			count += 1
		f.write("\n\\end{tabularx}\n")
		
	return(nrows)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs service data to a latex table that shows a list of service activities in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = service2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)