#! /usr/bin/env python3

import pandas as pd
import os
import sys
import numpy as np
from datetime import date
from zipfile import BadZipFile
import argparse

def STRM2Year(strm):
	return(int((strm-4190)/10 +2019))

from .stringprotect import str2latex

def shortformteaching(f, years, inputfile):
	source = inputfile  # File to read
	try:
		df = pd.read_excel(source, sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return 0
	except BadZipFile:
		print("Error reading file: " + source)
		print("If you open this file with Excel and resave, the problem should go away")
		return 0

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]

	if 'course_title' not in df.columns:
		df['course_title'] = ""


	df = df[(df['question']==19) | (df['question'] == 20)]
	table = df.pivot_table(index=['combined_course_num','course_title'],columns=['question'],values=['Weighted Average','enrollment','count_evals','STRM'],aggfunc={'Weighted Average': 'sum','enrollment': 'mean','count_evals': 'sum','STRM' : ['min', 'max',pd.Series.nunique]},sort=True)
	df = table.reset_index()
	df.fillna(0,inplace=True)
	nrows = df.shape[0] 
			
	if (nrows > 0):	
		f.write("\\begin{itemize}\n")
		count = 0
		while count < nrows:
			f.write("\\item\n")
			f.write(str2latex(df.iloc[count]['course_title','','']) + ' ')  #+' ' +str2latex(df.iloc[count]['combined_course_num','','']) 
			if STRM2Year(df.iloc[count]['STRM','min',19]) == STRM2Year(df.iloc[count]['STRM','max',19]):
				f.write(str(STRM2Year(df.iloc[count]['STRM','min',19])))
			else:
				f.write(str(STRM2Year(df.iloc[count]['STRM','min',19])) + "-" +str(STRM2Year(df.iloc[count]['STRM','max',19])))
			
			f.write(" " +str(df.iloc[count]['STRM', 'nunique', 20]))
			if df.iloc[count]['STRM', 'nunique', 20] == 1:
				f.write(" semester")
			else:
				f.write(" semesters")
			f.write(" Av. Enrl. " +str(int(df.iloc[count]['enrollment', 'mean', 20])))
			f.write(", Q19 " +"{:3.2f}".format(df.iloc[count]['Weighted Average', 'sum', 19]/df.iloc[count]['count_evals', 'sum', 19]))
			#f.write(", Q20 " +"{:3.2f}".format(df.iloc[count]['Weighted Average', 'sum', 20]/df.iloc[count]['count_evals', 'sum', 20]) +"\n")
			count += 1
		f.write("\\end{itemize}\n")

	return(nrows)
	
	df = df['question'==19]
	
#	 df = df.drop_duplicates(subset=['combined_course_num', 'term'])
# 
#	 df['course_period'] = df['term'].apply(lambda x: x[-4:])
# 
#	 grouped = (
#		 df.groupby(['combined_course_num', 'course_title'])
#		 .agg(
#			 min_year=('course_period', 'min'),
#			 max_year=('course_period', 'max'),
#			 count=('term', 'size')
#		 )
#		 .reset_index()
#	 )
# 
#	 grouped['year_range'] = grouped.apply(
#	 lambda row: row['min_year'] if row['min_year'] == row['max_year'] else f"{row['min_year']}-{row['max_year']}",
#	 axis=1
#	 )
# 
#	 grouped['output'] = grouped.apply(
#	 lambda row: (
#		 f"{row['course_title']} {row['combined_course_num']} {row['year_range']} "
#		 f"({row['count']} semester)" if row['count'] == 1 else 
#		 f"{row['course_title']} {row['combined_course_num']} {row['year_range']} "
#		 f"({row['count']} semesters)"
#	 ),
#	 axis=1
#	 )
# 
# 
#	 if not grouped.empty:
#		 f.write("\\begin{itemize}\n")
#		 for _, row in grouped.iterrows():
#			 f.write(f"  \\item {str2latex(row['output'])}\n")
#		 f.write("\\end{itemize}\n")

	return len(grouped)




if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs teaching data to a latex table that shows classes taught in the last [YEARS] years')
	parser.add_argument('-y', '--years', default="-1", type=int, help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const', const="a", default="w")
	parser.add_argument('inputfile', help='the input excel file name')
	parser.add_argument('outputfile', help='the output latex table name')
	args = parser.parse_args()

	f = open(args.outputfile, args.append)  # File to write
	nrows = shortformteaching(f, args.years, args.inputfile)
	f.close()

	if nrows == 0:
		os.remove(args.outputfile)


