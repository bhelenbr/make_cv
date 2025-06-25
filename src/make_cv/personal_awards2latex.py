#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# First argument is file to scatter, second argument is Faculty 
# scatter <file to scatter> <Faculty folder> 
# import modules
import pandas as pd
import os
import sys
from datetime import date

from .stringprotect import str2latex

names = ["Department","School","University","Professional","Community"]

def personal_awards2latex(f,years,inputfile,max_rows=-1):
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
		source_data = source_data[(source_data['Year'] >= begin_year)]
		if source_data.shape[0] == 0:
			return(0)
	
	#table = source_data.pivot_table(columns=['Year'], values=['Year'], index=['Type', 'Title'], aggfunc={'Year': 'count'},observed=False)
	
	f.write("\\begin{rubric}{Personal Awards}\n")
	total = 0
	for name in names:
		table = source_data[source_data.Type == name].pivot_table(columns=['Year'], values=['Year'], index=['Type', 'Title'], aggfunc={'Year': 'count'},observed=False)
		df = table.reset_index()
		df = df.fillna(0)
		#print(df)
		#print(df.columns)
		nrows = df.shape[0]
		ncols = df.shape[1]
		
		if max_rows > 0 and nrows > max_rows:
			nrows = max_rows
			
		total += nrows
		if nrows > 0: 
			f.write("\\subrubric{" +name +"}\n")
			count = 0
			while count < nrows:
				# make date string
				date_string = ""
				separ = ""
				prev_found = False
				found = False
				for year in range(2,ncols-1):
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
				if (df.iloc[count,ncols-1] > 0):
					if (found==False):
						date_string = date_string +separ +str(df.columns[ncols-1][1])
					else:
						date_string = date_string +"-" +str(df.columns[ncols-1][1])	
				f.write("\\entry*[" +date_string +"]" +str2latex(df.iloc[count,1])+ "\n")
				count += 1
	f.write("\\end{rubric}\n")
	return(total)
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs personal awards data to a latex table for awards received in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output, default is all')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = personal_awards2latex(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)