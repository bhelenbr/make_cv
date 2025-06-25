#! /usr/bin/env python3

# Python code to output service data in nice latex table

# import modules
import pandas as pd
import os
import sys
import argparse
from datetime import date

from .stringprotect import str2latex

def service2latex(f,years,inputfile,name,max_rows=-1):
	source = inputfile # file to read
	try:
		source_data = pd.read_excel(source,sheet_name="Data")
	except OSError:
		print("Could not open/read file: " + source)
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years
		source_data = source_data[source_data['Calendar Year'].apply(lambda x: int(x)) >= begin_year]
		
	if source_data.shape[0] == 0:
		return(0)
	
	
	
	f.write("\\begin{rubric}{" +name +"}\n")
	source_data['Type'] = source_data['Type'].str.strip()
	names = source_data.Type.unique()
	totalrows = 0
	for name in names:
		table = source_data[source_data.Type == name].pivot_table(columns=['Calendar Year'], values=['Term'], index=['Type', 'Description'], aggfunc={'Term': 'count'},observed=False)
		df = table.reset_index()
		df = df.fillna(0)
		#print(df)
		#print(df.columns)
		nrows = df.shape[0]
		if nrows == 0:
			continue
		
		ncols = df.shape[1]
		maxyear = [0] * nrows
		for count in range(0,nrows):
			for year in range(2,ncols):
				if (df.iloc[count,year] > 0):
					maxyear[count] = year
		df["maxyear"] = maxyear
		df.sort_values(by=["maxyear","Description"],inplace=True,ascending=[False,True])
		df.reset_index()
		# print(df)
		
		if max_rows > 0 and nrows > max_rows:
			nrows = max_rows
			
		totalrows += nrows

		f.write("\\subrubric{" +name +"}\n")
		count = 0
		while count < nrows:
			# make date string
			date_string = ""
			separ = ""
			prev_found = False
			found = False
			for year in range(2,ncols):
				if (df.iloc[count,year] > 0):
					if (found==False):
						date_string = date_string +separ +str(df.columns[year][1])
						separ = ","
					prev_found = found
					found = True
				else:
					if ((prev_found == True) and (found == True)):
						date_string = date_string +"-" +str(df.columns[year-1][1])
					prev_found = found
					found = False
			if ((prev_found == True) and (found == True)):
				date_string = date_string +"-" +str(df.columns[ncols-1][1])
			f.write("\\entry*[" +date_string +"] " +str2latex(df.iloc[count,1]) +"\n")
			count += 1
	f.write("\\end{rubric}\n")
	return(totalrows)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs service data to a latex table that shows a list of service activities in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="0",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = service2latex(f,args.years,args.inputfile,'Service')
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)
