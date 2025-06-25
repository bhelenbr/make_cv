#!/usr/bin/env python3

# import modules
import pandas as pd
import os
import sys
from datetime import date
import datetime as dt
import argparse

from .stringprotect import str2latex


def grants2latex_far(f,years,inputfile,max_rows=-1):
	try:
		props = pd.read_excel(inputfile,sheet_name="Data",header=0)
	except OSError:
		print("Could not open/read file: " + inputfile)
		return(0)
		

	props.fillna(value={"Sponsor": "", "Title": "", "Allocated Amt": 0, "Total Cost": 0, "Funded?": "N", "Begin Date": dt.datetime(1900,1,1),"End Date": dt.datetime(1900,1,1)},inplace=True)
	grants = props[props['Funded?'].str.match('Y')]
	grants.reset_index(inplace=True,drop=True)

	if (not(grants.shape[0] > 0)):
		return(0)

	if years > 0:
		today = date.today()
		year = today.year
		begin_year = year - years	
		grants = grants[grants['Begin Date'].apply(lambda x: x.year) >= begin_year]
		
	grants = grants.sort_values(by=['Begin Date'],ascending = [False])
	grants.reset_index(inplace=True,drop=True)
	nrows = grants.shape[0]
	
	if max_rows > 0 and nrows > max_rows:
		nrows = max_rows

	if (nrows > 0):
		total = grants["Total Cost"].sum()
		allocated = grants["Allocated Amt"].sum()
		
		f.write("Personal Allocation: " +"\\${:,.0f}k".format(allocated/1000) +"  Total: " +"\\${:,.0f}k\n".format(total/1000))
	
		f.write("\\begin{tabularx}{\\linewidth}{>{\\rownum}rXllll}\n& Sponsor: Title & Alloc/Total & Dates  \\tablehead\n")
		f.write("\\tablecontinue{Grants}\n")
		count = 0
		newline=""
		while count < nrows:
			f.write(newline)
			f.write("& " +str2latex(grants.loc[count,"Sponsor"].upper())+": " +str2latex(grants.loc[count,"Title"]) + " & " + "\\${:,.0f}k".format(grants.loc[count,"Allocated Amt"]/1000) + "/" +"\\${:,.0f}k".format(grants.loc[count,"Total Cost"]/1000))
			f.write(" & " +grants.loc[count,"Begin Date"].strftime("%m/%Y") +"-" +grants.loc[count,"End Date"].strftime("%m/%Y"))
			newline="\\\\\n"
			count += 1
		f.write("\n\\end{tabularx}\n")
	
	return(nrows)
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs grants data to a latex table that shows a list of grants received in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('-a', '--append', action='store_const',const="a",default="w")
	parser.add_argument('inputfile',help='the input excel file name')           
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outputfile, args.append) # file to write
	nrows = grants2latex_far(f,args.years,args.inputfile)
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)