#!/usr/bin/env python3

import requests
from collections import defaultdict
from datetime import date
from datetime import datetime
import pandas as pd
import os


ORCID_API = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}


# ------------------------------------------------------------
# ORCID API access
# ------------------------------------------------------------

def get_peer_reviews(orcid):
	url = f"{ORCID_API}/{orcid}/peer-reviews"
	r = requests.get(url, headers=HEADERS)
	r.raise_for_status()
	return r.json().get("group", [])


# ------------------------------------------------------------
# Extract a single review defensively
# ------------------------------------------------------------

def extract_review(group):
	subgroup = group.get("peer-review-group",{})
	summary = subgroup[0].get("peer-review-summary", {})[0]
	
	source = summary.get("source", {}).get("source-name", {}).get("value")
	organization = summary.get("convening-organization", {}).get("name")
	
	year = (
		summary.get("completion-date", {})
		.get("year", {})
		.get("value")
	)

	# Prefer journal title; fall back to organization
	venue = source or organization

	if year:
		year = int(year)

	return {
		"venue": venue,
		"year": year
	}


# ------------------------------------------------------------
# Collect, filter, group, and sort (CV-grade)
# ------------------------------------------------------------


def reviews2excel_orcid(orcid,outputfile):

	journal = []
	startdate = []
	rounds = []
	
	for group in get_peer_reviews(orcid):
		try:
			r = extract_review(group)			
			venue = r["venue"]
			year = r["year"]
			
			# orcid doesn't tell month or day 
			datestring = "01 01 " + str(year)
			datetime_object = datetime.strptime(datestring, '%d %m %Y').date()
			
			journal.append(venue)
			startdate.append(datetime_object)
			rounds.append("1")
		except Exception:
			continue
	
	df1 = pd.DataFrame({'Journal':journal,'Start':startdate,'Rounds':rounds})
	file_path3 = "reviews_nonpublons.xlsx"

	# append excel file 1 to 2 - creates new data file
	# with open(file_path3, encoding="latin-1") as f3:
	output_dir = os.path.dirname(outputfile)
	try:
		df2 = pd.read_excel(output_dir +os.sep +file_path3)
		df_total = pd.concat([df1, df2])
	except FileNotFoundError as e:
		df_total = df1

	excelfile = df_total.to_excel(outputfile, index=False)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs reviewing data from orcid to an excel file and appends the non-orcid data')
	parser.add_argument('orcid',help='the orcid for the reviewing data')		   
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	args = parser.parse_args()
	reviews2excel_orcid(args.inputfile,args.outputfile)
