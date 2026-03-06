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

from make_cv import global_prefs

from .stringprotect import str2latex

def STRM2Year(strm):
	return(int((strm-4190)/10 +2019))

# Last 4 digits of term should be year
def term2year(term):
	return(int(term[-4:]))

def teaching2latex_far(f,years,inputfile,private=False,sortbycourse=False,shortform=False):
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
		df = df[df['term'].apply(lambda x: term2year(x) >= begin_year)]
	
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

	table = df.groupby(['combined_course_num','STRM','term']).agg({'course_title':['first'],'combined_num_sec':['count'],'enrollment':['sum'],'count_19':['sum'],'weighted_19':['sum'],'count_20':['sum'],'weighted_20':['sum']})
	df = table.reset_index()
	if sortbycourse:
		df.sort_values(by=[('combined_course_num',''),('course_title','first'),('STRM','')], inplace=True,ascending = [True,True,False])
		df[('title_string','')] = df[('course_title','first')]

		headers = ["Course","Term"]
		keys = [('title_string',''),('term','')]
	else:
		df.sort_values(by=[('STRM',''),('combined_course_num',''),('course_title','first')], inplace=True,ascending = [False,True,True])
		df[('title_string','')] = df[('combined_course_num','')] + " " + df[('course_title','first')]
		headers = ["Term","Course"]
		keys = [('term',''),('title_string','')]			
	
	df.reset_index(inplace=True)	
	

	nrows = df.shape[0] 
	if (nrows > 0):	
		newline=""
		if not global_prefs.usePandoc:
			ending = "\\endfirsthead\n"
		else:
			ending = "\\\\\n\\hline\n"

		if (private):
			f.write("\\begin{tabularx}{\\linewidth}{lXll}\n")
			f.write(f"{headers[0]}  & {headers[1]} & Secs & Enroll. {ending}")
			if not global_prefs.usePandoc: 
				f.write("\\multicolumn{4}{l}{\\conthead{Teaching}} \\endhead \\hline\n")
		else:
			f.write("\\begin{tabularx}{\\linewidth}{lXlllll}\n")
			f.write(f"{headers[0]} & {headers[1]} & Secs & Enroll. & \\%Resp. & Q19 & Q20 {ending}")
			if not global_prefs.usePandoc: 
				f.write("\\multicolumn{7}{l}{\\conthead{Teaching}} \\endhead \\hline\n")
		
		count = 0
		while count < nrows:
			f.write(newline)
			f.write(str2latex(df.loc[count,keys[0]]) + " & " +str2latex(df.loc[count,keys[1]]) + " & " +"{:d}".format(df.loc[count,('combined_num_sec','count')]) +" & " +"{:d}".format(df.loc[count,('enrollment','sum')]))
			if not private:
				f.write(" & " +"{:3.0f}".format(df.loc[count,('count_19','sum')]*100.0/df.loc[count,('enrollment','sum')]) + "\\% & " +"{:3.2f}".format(df.loc[count,('weighted_19','sum')]/df.loc[count,('count_19','sum')]) + " & " +"{:3.2f}".format(df.loc[count,('weighted_20','sum')]/df.loc[count,('count_20','sum')]))
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