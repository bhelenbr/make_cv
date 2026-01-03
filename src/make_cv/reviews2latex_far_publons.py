#! /usr/bin/env python3
# This script outputs reviewing data to a latex table
# that shows a list of journals reviewed for and the number of papers reviewed for each
# journal in the last 5 years
# 
# To run "publons2latex.py <filename> <outputname.txt>"

# import modules
import pandas as pd
import os
import sys
from datetime import date
import argparse

from .stringprotect import str2latex

def publons2latex_far(f,years,inputfile):
	source = inputfile  # file to read
	try:
		reviews = pd.read_excel(source,header=0)
	except OSError:
		print("Could not open/read file: " + source)
		return

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		reviews = reviews[reviews['Start'].apply(lambda x: x.year) >= begin_year]
		
	reviews.reset_index(inplace=True)
	table = reviews.sort_values(by=['Start'], ascending=[False])
	#print(table)

	nrows = table.shape[0] 
	if (nrows > 0):
		f.write("\\begin{tabularx}{\linewidth}{Xll}\nJournal & Start Date & Rounds \\\\\n\\hline\n")

		count = 0
		newline=""
		while count < nrows:
			f.write(newline)
			f.write(str2latex(table.loc[count,"Journal"]) + " & " +str(table.loc[count,"Start"].strftime('%b %Y')) +" & " +str(table.loc[count,"Rounds"]))
			newline = "\\\\\n"
			count += 1
	f.write("\n\\end{tabularx}\n")
	
	return(nrows)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs reviewing data to a latex table that shows a list of journals reviewed for and the number of papers reviewed for each journal in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = publons2latex_far(args.outputfile, args.append) # file to write
	nrows = main(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)