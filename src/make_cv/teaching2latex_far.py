#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# First argument is file to scatter, second argument is Faculty 
# scatter <file to scatter> <Faculty folder> 

# import modules
import pandas as pd
import os
import sys
import numpy as np
from datetime import date
import argparse

from .stringprotect import str2latex


def teaching2latex_far(f,years,inputfile,private=False):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years	
		df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]
	
	df = df[(df['question']==19) | (df['question'] == 20)]
	
	table = df.pivot_table(index=['STRM','term','combined_course_num','course_section'],columns=['question'],aggfunc={'enrollment': 'sum','Weighted Average': 'sum', 'count_evals': 'sum'})	
	#table = df.pivot_table(index=['STRM','term','course_num','course_section','enrollment'],columns=['question'],values=['Calculated Mean','Particip'],aggfunc={'Calculated Mean': np.mean, 'Particip':'sum'})
	
	df = table.reset_index()
	df = df.fillna(0)
	df.sort_values(by=['STRM','combined_course_num','course_section'], inplace=True,ascending = [False,True,True])
	df = df.reset_index()
	#print(df.columns)
	nrows = df.shape[0] 
	if (nrows > 0):	
		newline=""
		if (private):
			f.write("\\begin{tabularx}{\\linewidth}{lXll}\nTerm  & Course & Sections & Enrollment \\\\\n\\hline\n")
			count = 0
			while count < nrows:
				f.write(newline)
				f.write(str2latex(df.loc[count,('term','')]) + " & " +str2latex(df.loc[count,('combined_course_num','')]) + " & " +str2latex(df.loc[count,('course_section','')]) +" & " +str2latex(df.loc[count,('enrollment',1)]))
				count += 1
		else:
			f.write("\\begin{tabularx}{\\linewidth}{lXllll}\nTerm  & Course & Sections & Enrollment & Q19 & Q20 \\\\\n\\hline\n")
			count = 0
			while count < nrows:
				f.write(newline)
				f.write(str2latex(df.loc[count,('term','')]) + " & " +str2latex(df.loc[count,('combined_course_num','')]) + " & " +str2latex(df.loc[count,('course_section','')]) +" & " +str2latex(df.loc[count,('enrollment',19)])+ " & " +"{:3.2f}".format(df.loc[count,('Weighted Average',19)]/df.loc[count,('count_evals',19)]) + " & " +"{:3.2f}".format(df.loc[count,('Weighted Average',20)]/df.loc[count,('count_evals',20)]))
				newline="\\\\\n"
				count += 1
		f.write("\n\\end{tabularx}\n")
		
	return(nrows)

#course	term	sec	enroll	Eval	% Resp	Eval	% Resp

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs teaching data to a latex table that shows classes taught in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('-p', '--private',default=False,type=bool,help="Hide teaching evaluation numbers")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = teaching2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)