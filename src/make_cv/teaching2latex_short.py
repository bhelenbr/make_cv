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

# Last 4 digits of term should be year
def term2year(term):
	return(int(term[-4:]))

from .stringprotect import str2latex

def teaching2latex_short(f, years, inputfile, private=False):
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
		df = df[df['term'].apply(lambda x: term2year(x)) >= begin_year]

	if 'component' not in df.columns:
		df['component'] = "LEC"
	else:
		df['component'] = df['component'].fillna("LEC")

	if 'course_title' not in df.columns:
		df['course_title'] = ""
	else:
		df['course_title'] = df['course_title'].fillna("")

	if 'STRM' not in df.columns:
		df['STRM'] = df.index

	# components: CLN -clinical DIS-discussion FLD-fieldwork IND-independent study LAB-lab LEC-lecture PHY-physical education PRA-practacum PRO-project RSC-research SEM-seminar THE-thesis TUT-tutorial						
	df = df[~df['component'].isin(['DIS','IND','PRO','RSC','TUT','THE'])]	
	df['weighted_19'] = df['count_19'] * df['mean_19']
	df['weighted_20'] = df['count_20'] * df['mean_20']
	df['ncomponents'] = df.groupby(['combined_course_num','STRM'])['component'].transform('nunique')


	df['STRM_combined_num_sec'] = df['STRM'].astype(str) + df['combined_num_sec'].astype(str)
	table = df.groupby(['combined_course_num','component']).agg({'course_title':['first'],'STRM':['min', 'max','nunique'],'ncomponents':['first'],'enrollment':['sum'],'count_19':['sum'],'weighted_19':['sum'],'count_20':['sum'],'weighted_20':['sum']})	
	df = table.reset_index()

	df.sort_values(by=[('combined_course_num',''),('course_title','first')], inplace=True,ascending = [True,True])
	df = table.reset_index()
	mask = df[('ncomponents','first')] > 1
	df[('title_string','')] = df[('combined_course_num','')] + np.where(mask, " ("+df[('component','')] + ")", "") + "-" + df[('course_title','first')]

	nrows = df.shape[0] 
	if (nrows > 0):	
		f.write("\\begin{itemize}\n")
		count = 0
		while count < nrows:
			f.write("\\item\n")
			f.write(str2latex(df.iloc[count]['title_string','']) + ', ')
			if STRM2Year(df.iloc[count]['STRM','min']) == STRM2Year(df.iloc[count]['STRM','max']):
				f.write(str(STRM2Year(df.iloc[count]['STRM','min'])))
			else:
				f.write(str(STRM2Year(df.iloc[count]['STRM','min'])) + "-" +str(STRM2Year(df.iloc[count]['STRM','max'])))
			
			f.write(", " +str(df.iloc[count]['STRM', 'nunique']))
			if df.iloc[count]['STRM', 'nunique'] == 1:
				f.write(" semester,")
			else:
				f.write(" semesters,")
			#f.write(" \={Enrl}: " +"{:d}".format(int(df.iloc[count]['enrollment', 'sum']/df.iloc[count]['STRM', 'nunique'])))
			f.write(" {:d}".format(int(df.iloc[count]['enrollment', 'sum']/df.iloc[count]['STRM', 'nunique'])))

		
			if not private:
				if df.iloc[count]['count_19', 'sum'] > 0:
					f.write(", {:3.2f}".format(df.iloc[count]['weighted_19', 'sum']/df.iloc[count]['count_19', 'sum']))
					f.write(", {:3.2f}".format(df.iloc[count]['weighted_20', 'sum']/df.iloc[count]['count_20', 'sum']))
			f.write("\n")
			count += 1
		f.write("\\end{itemize}\n")

	return(nrows)
	
#	df = df['question'==19]
#	
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
#
#	return len(grouped)




if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs teaching data to a latex table that shows classes taught in the last [YEARS] years')
	parser.add_argument('-y', '--years', default="-1", type=int, help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const', const="a", default="w")
	parser.add_argument('inputfile', help='the input excel file name')
	parser.add_argument('outputfile', help='the output latex table name')
	args = parser.parse_args()

	f = open(args.outputfile, args.append)  # File to write
	nrows = teaching2latex_short(f, args.years, args.inputfile)
	f.close()

	if nrows == 0:
		os.remove(args.outputfile)


