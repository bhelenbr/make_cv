#! /usr/bin/env python3

# Python code to create latex form of Undergraduate Research Data

# import modules
import datetime
import pandas as pd
import os
import sys
from datetime import date

from .stringprotect import str2latex
from .stringprotect import abbreviate_name_list

def UR2latex(f,years,inputfile,max_rows=-1):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return 0

	df.fillna('',inplace=True)	
	if (years > 0):
		today = date.today()
		year = today.year
		begin_year = year - years

		df = df[(df['Calendar Year'] >= begin_year)]
		df.sort_values(by=['Calendar Year','Term'], inplace=True, ascending = [False,True])
		df.reset_index(inplace=True)
	
	nrows = df.shape[0]
	if (nrows > 0):
		#table = pd.pivot_table(df, values=['Calendar Year','Term'], index=['Students', 'Title', 'Program Type'], aggfunc={'Calendar Year': ('min','max'), 'Term': 'count'},observed=True)
		table = pd.pivot_table(df, values=['Calendar Year','Term'], index=['Students', 'Title', 'Program Type'], aggfunc={'Calendar Year': ('min'), 'Term': 'count'},observed=True)
		df = table.reset_index()
		#print(df.columns)
		nrows = df.shape[0]
		
		if max_rows > 0 and nrows > max_rows:
			nrows = max_rows
		
		#df.sort_values(by=[('Calendar Year',   'max')], inplace=True, ascending = [False])
		df.sort_values(by=['Calendar Year'], inplace=True, ascending = [False])
		df = df.reset_index()
		#print(df)
		
		f.write("\\begin{tabularx}{\\linewidth}{>{\\rownum}rXll}\n & Name: Title  & Program & Date(Semesters) \\tablehead\n")
		f.write("\\tablecontinue{Undergraduate Research}\n")
		count = 0
		newline=""
		while count < nrows:
			f.write(newline)
			f.write(" & " +abbreviate_name_list(df.loc[count,"Students"])+": " +str2latex(df.loc[count,"Title"]) + " & " +str2latex(df.loc[count,"Program Type"]) + " & " +str2latex(df.loc[count,"Calendar Year"]) +"("+str2latex(df.loc[count,"Term"]) +")")
			newline="\\\\\n"
			count += 1
	
		f.write("\n\\end{tabularx}\n")
	
	return(nrows)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs undergraduate research data to a latex table')
	parser.add_argument('-y', '--years',default="0",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = UR2latex(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)