#! /usr/bin/env python3
# this is the updated version of the publons script
# This script converts .json review list from publons into an .txt file, and then from text file to excel
# The script then merges the excel data between publons and non publons files into one
# To run "publons.py <filename> > <outputname>"

import json
import sys
import os
import pandas as pd
import shutil
from datetime import datetime
import argparse

def publons2excel(inputfile,outputfile):
	json_dir = os.path.dirname(inputfile)

	try:
		with open(inputfile) as f:
			data=json.load(f)
			f.close()
	except FileNotFoundError:
		print("json file not found " +inputfile)
		exit()

	journal = []
	startdate = []
	rounds = []

	for review in data['records']['review']['reviews']['review_list']:
		datestring = review['review_rounds']['start_date']
		datestring = datestring[:4] + "1 " + datestring[4:]
		datetime_object = datetime.strptime(datestring, '%b %d %Y').date()
		journal.append(review['journal'])
		startdate.append(datetime_object)
		rounds.append(review['review_rounds']['number_of_rounds'])

	df1 = pd.DataFrame({'Journal':journal,'Start':startdate,'Rounds':rounds})
	file_path3 = "reviews_nonpublons.xlsx"

	# append excel file 1 to 2 - creates new data file
	# with open(file_path3, encoding="latin-1") as f3:
	try:
		df2 = pd.read_excel(json_dir +os.sep +file_path3)
		df_total = pd.concat([df1, df2])
	except FileNotFoundError as e:
		df_total = df1

	excelfile = df_total.to_excel(outputfile, index=False)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script converts a .json reviewing file into the reviews data.xlsx file and appends the non-publons data')
	parser.add_argument('inputfile',help='the input json file name') 
	parser.add_argument('outputfile',default="reviews data.xlsx",help='the output file name')          
	args = parser.parse_args()
	publons2excel(args.inputfile,args.outputfile)



