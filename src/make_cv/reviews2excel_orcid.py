#!/usr/bin/env python3

import requests
import argparse

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
	try:
		r = requests.get(url, headers=HEADERS, timeout=10)
		r.raise_for_status()
		return r.json().get("group", [])
	except requests.RequestException as exc:
		print(f"Failed to fetch ORCID peer reviews for {orcid}: {exc}")
		return []


def get_group_name(group_id, cache={}):
	"""Journal name for a review group ID like 'issn:0017-9310', looked up in Crossref, or None."""
	if group_id in cache:
		return cache[group_id]
	name = None
	if group_id.lower().startswith("issn:"):
		issn = group_id.split(":", 1)[1].strip()
		try:
			r = requests.get(f"https://api.crossref.org/journals/{issn}", timeout=10)
			r.raise_for_status()
			name = r.json().get("message", {}).get("title")
		except Exception:
			pass
	cache[group_id] = name
	return name


# ------------------------------------------------------------
# Extract every review in a journal group
# ------------------------------------------------------------

def extract_reviews(group):
	"""One dict per review in a journal group."""
	reviews = []
	for review in group.get("peer-review-group", []):
		summaries = review.get("peer-review-summary") or []
		if not summaries:
			continue
		summary = summaries[0]    # several summaries = same review from different sources

		group_id = summary.get("review-group-id")
		venue = (get_group_name(group_id) if group_id else None) \
			or (summary.get("convening-organization") or {}).get("name") \
			or group_id

		cdate = summary.get("completion-date") or {}
		def part(k, default):
			v = (cdate.get(k) or {}).get("value")
			return int(v) if v else default
		year = part("year", None)
		if venue is None or year is None:
			continue
		reviews.append({"venue": venue, "date": date(year, part("month", 1), part("day", 1))})
	return reviews


# ------------------------------------------------------------
# Collect and write the Excel file
# ------------------------------------------------------------

def reviews2excel_orcid(orcid,outputfile):
	journal, startdate, rounds = [], [], []
	for group in get_peer_reviews(orcid):
		for r in extract_reviews(group):
			journal.append(r["venue"])
			startdate.append(r["date"])
			rounds.append(1)
	
	df1 = pd.DataFrame({'Journal':journal,'Start':startdate,'Rounds':rounds})
	file_path3 = "reviews_nonpublons.xlsx"

	# append excel file 1 to 2 - creates new data file
	# with open(file_path3, encoding="latin-1") as f3:
	output_dir = os.path.dirname(outputfile)
	try:
		df2 = pd.read_excel(output_dir +os.sep +file_path3,sheet_name='Data')
		df_total = pd.concat([df1, df2])
	except FileNotFoundError as e:
		df_total = df1

	excelfile = df_total.to_excel(outputfile, index=False,sheet_name='Data')


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs reviewing data from orcid to an excel file and appends the non-orcid data')
	parser.add_argument('orcid',help='the orcid for the reviewing data')		   
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	args = parser.parse_args()
	reviews2excel_orcid(args.orcid,args.outputfile)
