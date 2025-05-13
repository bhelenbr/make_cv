#! /usr/bin/env python3

# Python code to create latex form of Undergraduate Research Data - for the three most recent 3 years
# First argument is excel file to read (including path), and second argument is what you want to name output file, as .tex

# import modules
from datetime import date
import pandas as pd
import os
import sys
import argparse

from .stringprotect import str2latex
from .stringprotect import abbreviate_name_list

def UR2latex_far(f,years,inputfile):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return

	df.fillna('',inplace=True)
	#df['Calendar Year'] = pd.to_datetime(df['Calendar Year'],format = "%Y",exact=True)
	
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		df = df[(df['Calendar Year'] >= begin_year)]
		
	df.sort_values(by=['Calendar Year','Term'], inplace=True, ascending = [False,True])
	df.reset_index(inplace=True)
	
	nrows = df.shape[0]
	
	if (nrows > 0):	
		f.write("\\begin{tabularx}{\\linewidth}{Xll}\nName: Title  & Program & Term \\\\\n\\hline\n")
		count = 0
		newline=""
		while count < nrows:
			f.write(newline)
			f.write(abbreviate_name_list(df.loc[count,"Students"])+": " +str2latex(df.loc[count,"Title"]) + " & " +df.loc[count,"Program Type"] + " & " +df.loc[count,"Term"] +" " +str(df.loc[count,"Calendar Year"])+"\\\\\n")
			newline="\\\\\n"
			count += 1
		f.write("\n\\end{tabularx}\n")
		
	return(nrows)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs undergraduate research data to a latex table that shows the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = UR2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)