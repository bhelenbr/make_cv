#! /usr/bin/env python3

# Python code to scatter Undergraduate research data to faculty folders
# First argument is file to scatter, second argument is Faculty 
# scatter <file to scatter> <Faculty folder> 
# import modules
import pandas as pd
import os
import sys
import datetime as dt
import argparse

from .stringprotect import str2latex


def props2latex_far(f,years,inputfile,max_rows=-1):
	source = inputfile # file to read
	try:
		props = pd.read_excel(source,sheet_name="Data",header=0,dtype={'Sponsor':str,'Long Descr':str,'Allocated Amt':float,'Total Cost':float})

	except OSError:
		print("Could not open/read file: " + source)
		return(0)
	
	
	props.fillna(value={"Sponsor": "", "Title": "", "Allocated Amt": 0, "Total Cost": 0, "Funded?": "N", "Begin Date": dt.datetime(1900,1,1),"End Date": dt.datetime(1900,1,1)},inplace=True)
	if years > 0:
		today = dt.date.today()
		year = today.year
		begin_year = year - years
		props = props[props['Begin Date'].apply(lambda x: x.year) >= begin_year]
	
	props.sort_values(by=['Begin Date'], inplace=True,ascending = [False])
	props = props.reset_index()
	nrows = props.shape[0] 

	if max_rows > 0 and nrows > max_rows:
		nrows = max_rows
	
	if (nrows > 0):	
		f.write("\\begin{tabularx}{\\linewidth}{>{\\rownum}rXllll}\n& Sponsor: Title & Alloc/Total & Dates  \\tablehead\n")
		f.write("\\tablecontinue{Proposals}\n")
		newline = ""
		count = 0
		while count < nrows:
			f.write(newline)
			f.write(" & " +str2latex(props.loc[count,"Sponsor"].upper())+": " +str2latex(props.loc[count,"Title"]) + " & " + "\\${:,.0f}k".format(props.loc[count,"Allocated Amt"]/1000) + "/" +"\\${:,.0f}k".format(props.loc[count,"Total Cost"]/1000))
			f.write(" & " +props.loc[count,"Begin Date"].strftime("%m/%Y") +"-" +props.loc[count,"End Date"].strftime("%m/%Y"))
			newline = "\\\\\n"
			count += 1
		f.write("\n\\end{tabularx}\n")
	
	return(nrows)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs proposals data to a latex table that shows a list of proposals received in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = props2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if nrows == 0:
		os.remove(args.outputfile)