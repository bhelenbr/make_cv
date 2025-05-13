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
from zipfile import BadZipFile

from .stringprotect import str2latex

def teaching2latex(f,years,inputfile):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)
	except BadZipFile:
		print("Error reading file: " + source)
		print("If you open this file with Excel and resave, the problem should go away")
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years	
		df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]
		
	if not('course_title' in df.columns):
		df['course_title'] = ""
		
	df = df[(df['question']==19) | (df['question'] == 20)]
	df.sort_values(by=['combined_course_num','STRM','course_section','course_title'],inplace=True)
	df.reset_index(inplace=True)
	
	table = df.pivot_table(index=['combined_course_num','STRM','term','course_section','course_title'],columns=['question'],values=['Weighted Average','enrollment','count_evals'],aggfunc={'sum'},sort=True)
	df = table.reset_index()
	df = df.fillna(0)
	#print(df)
	#print(df.columns)
	nrows = df.shape[0] 
	
	if (nrows > 0):	

		f.write("\\begin{tabularx}{\\linewidth}{Xlllll}\nCourse  & Term & Sec & Enrl & Q19 & Q20 \\endfirsthead\n")
		f.write("\\multicolumn{6}{l}{\\conthead{Teaching}} \\endhead \\hline\n")
		count = 0
		newline=""
		while count < nrows:
			f.write(newline)
			f.write(str2latex(df.iloc[count]['combined_course_num',    '', '']) +" " +str2latex(df.iloc[count]['course_title',    '', '']) + " & " +str2latex(df.iloc[count]['term',    '', '']) + " & " +str2latex(df.iloc[count]['course_section',    '', '']) +" & " +str2latex(df.iloc[count]['enrollment', 'sum', 20])+ " & " +"{:3.2f}".format(df.iloc[count]['Weighted Average', 'sum', 19]/df.iloc[count]['count_evals', 'sum', 19])+ " & " +"{:3.2f}".format(df.iloc[count]['Weighted Average', 'sum', 20]/df.iloc[count]['count_evals', 'sum', 20]))
			newline="\\\\\n"
			count += 1
		f.write("\n\\end{tabularx}\n")

	return(nrows)
	
#course	term	sec	enroll	Eval	% Resp	Eval	% Resp

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs teaching data to a latex table that shows classes taught in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="-1",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = teaching2latex(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)