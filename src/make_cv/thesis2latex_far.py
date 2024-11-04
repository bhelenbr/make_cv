#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders - for the 3 most recent years
# First argument is file to scatter, second argument is Faculty
# scatter <file to scatter> <Faculty folder>

# import modules
import datetime as dt
import pandas as pd
import os
import sys
import argparse

from .stringprotect import str2latex
from .stringprotect import abbreviate_name

def thesis2latex_far(f,years,studentfile,thesisfile):
	try:
		source = pd.read_excel(studentfile,sheet_name="Data",parse_dates=['Start Date'])
		student_found = True
	except OSError:
		print("Could not open/read file: " + studentfile)
		student_found = False
		
	try:
		source2 = pd.read_excel(thesisfile,sheet_name="Data",dtype={'Start Date':int,'Year':int})
		thesis_found = True
	except OSError:
		print("Could not open/read file: " + thesisfile)
		thesis_found = False
	
	today = dt.date.today()
	year = today.year
	begin_year = year - years

	if (student_found):
		source = source.fillna({'Start Date':today})
		source.sort_values(by=['Start Date','Current Program','Student Name'], inplace=True, ascending = [False,True,True])
		df = source.reset_index()
		nrows = df.shape[0]
	else:
		nrows = 0
	
	if (thesis_found):
		source2 = source2.fillna(0)
		if years > 0:
			source2 = source2[source2['Year'].apply(lambda x: int(x)) >= begin_year]
		source2.sort_values(by=['Year','Degree','Student'], inplace=True, ascending = [False,True,True])
		df2= source2.reset_index()
		nrows2 = df2.shape[0]
	else:
		nrows2 = 0
	
	
	if (nrows+nrows2 > 0):
		f.write("\\begin{tabularx}{\\linewidth}{>{\\rownum}rXll}\n & Name: Title  & Date & Degree \\\\\n\\hline\n")
		
		if nrows > 0:
			count = 0
			while count < nrows:
				f.write(" & " +abbreviate_name(df.loc[count,"Student Name"])+": in progress"  + " &  & " +str2latex(df.loc[count,"Current Program"][(df.loc[count,"Current Program"].find("-")+1):]) +"\\\\\n")
				count += 1
		
		if nrows2 > 0:
			count = 0
			while count < nrows2:
				f.write(" & " +abbreviate_name(df2.loc[count,"Student"])+": " +str2latex(df2.loc[count,"Title"]) + " & " +'{0:d}'.format(int(df2.loc[count,"Year"])) + " & " +str2latex(df2.loc[count,"Degree"]) +"\\\\\n")
				count += 1
	
		f.write("\\end{tabularx}\n")
		
	return(nrows+nrows2)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs thesis data to a latex table for the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('studentfile',help='the student excel file name')          
	parser.add_argument('thesisfile',help='the thesis excel file name') 
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = thesis2latex_far(f,args.years,args.studentfile,args.thesisfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)