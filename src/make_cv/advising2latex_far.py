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

def advising2latex_far(f,years,inputfile,private=False):
	source = inputfile # file to read
	try:
		df = pd.read_excel(source)
	except OSError:
		print("Could not open/read file: " + source)
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		df = df[df['Term'].apply(lambda x: int(x/10)-400+2000) >= begin_year]
	
	df = df[df['Career']=="UGRD"]
	df = df.drop(columns=["ID","LN,FN","Career","DeptID","Descriptio","School","Long Descr"])
	df['Weighted'] = df["Question 1"] +2*df["Question 2"] +3*df["Question 3"] +4*df["Question 4"] +5*df["Question 5"] 
	df['EvalCount'] =   df["Question 1"] +df["Question 2"] +df["Question 3"] +df["Question 4"] +df["Question 5"]
	q5 = df[(df['Number']==5)]
	evals = q5['EvalCount'].sum()
	weight = q5['Weighted'].sum()
	f.write("Advising Evaluations: Question 5 - Is in his/her office during office hours: " +"{:3.2f}".format(weight/evals)+" (\\# of Evals: " +str(evals) +" ) \\par\n")	
	
	q11 = df[(df['Number']==11)]
	evals = q11['EvalCount'].sum()
	weight = q11['Weighted'].sum()
	f.write("Advising Evaluations: Question 11 - In general, I am pleased with my advisor: " +"{:3.2f}".format(weight/evals) +" (\\# of Evals: " +str(evals) +" ) \\par\n\n")
	return(1)	
	

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
	nrows = advising2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)