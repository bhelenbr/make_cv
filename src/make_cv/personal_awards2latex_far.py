#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# First argument is file to scatter, second argument is Faculty 
# scatter <file to scatter> <Faculty folder> 
# import modules
import pandas as pd
import os
import sys
from datetime import date
import argparse

from .stringprotect import str2latex

def personal_awards2latex_far(f,years,inputfile):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
	
	today = date.today()
	year = today.year
	begin_year = year - years

	df = df[(df['Year'] >= begin_year)]
	df.reset_index(inplace=True)
	nrows = df.shape[0] 

	if (nrows > 0):
		df = df.fillna('')
		df.sort_values(by=['Year','Type','Title'], inplace=True, ascending = [False,True,True])
		df.reset_index()

		#print(df)
		#print(df.columns)
	
		f.write("\\begin{tabularx}{\\linewidth}{llX}\nYear & Type  & Title \\\\\n\\hline\n")
		count = 0
		newline = ""
		while count < nrows:
			f.write(newline)
			f.write(str(df.loc[count,"Year"]) + " & " +df.loc[count,"Type"] + " & " +str2latex(df.loc[count,"Title"]))
			newline = "\\\\\n"
			count += 1
	
		f.write("\n\\end{tabularx}\n")
	
	return(nrows)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs personal awards data to a latex table for awards received in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = personal_awards2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)