#!/usr/bin/env python3

import requests
from collections import defaultdict
from datetime import date


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
	print(f"source {source}")
	organization = summary.get("convening-organization", {}).get("name")
	
	year = (
		summary.get("completion-date", {})
		.get("year", {})
		.get("value")
	)
	print(f"year {year}")

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

def collect_and_group_reviews(orcid, start_year=None):
	grouped = defaultdict(lambda: {"count": 0, "years": set()})

	for group in get_peer_reviews(orcid):
		try:
			r = extract_review(group)

			if not r["venue"]:
				continue

			year = r["year"]
			print(year)
			print(start_year)
			if start_year and (year is None or int(year) < int(start_year)):
				continue
			print("I am here")
			grouped[r["venue"]]["count"] += 1
			if year:
				grouped[r["venue"]]["years"].add(year)

		except Exception:
			continue

	records = []
	for venue, data in grouped.items():
		records.append({
			"venue": venue,
			"count": data["count"],
			"latest_year": max(data["years"]) if data["years"] else None
		})

	records.sort(
		key=lambda x: (x["latest_year"] or 0, x["venue"]),
		reverse=True
	)

	return records


# ------------------------------------------------------------
# LaTeX helpers
# ------------------------------------------------------------

def latex_escape(text):
	if not text:
		return ""
	replacements = {
		"&": r"\&",
		"%": r"\%",
		"_": r"\_",
		"#": r"\#",
		"{": r"\{",
		"}": r"\}",
	}
	for k, v in replacements.items():
		text = text.replace(k, v)
	return text


def reviews_to_latex_longtable(records, start_year=None):
	subtitle = (
		f"\\textit{{Reviewing activity since {start_year}}}\n\n"
		if start_year else ""
	)

	header = r"""
\begin{longtable}{p{0.65\linewidth}rr}
\hline
Journal / Venue & Reviews & Most Recent \\
\hline
\endhead
""".strip()

	rows = []
	for r in records:
		rows.append(
			f"{latex_escape(r['venue'])} & "
			f"{r['count']} & "
			f"{r['latest_year'] or ''} \\\\"
		)

	footer = r"""
\hline
\end{longtable}
""".strip()

	return "\n".join([subtitle, header] + rows + [footer])


def reviews2latex_far_orcid(f,orcid,years):
	if years > 0:
		today = date.today()
		year = today.year
		begin_year = str(year - years)
	else:
		begin_year = str(0)
		
	records = collect_and_group_reviews(orcid,start_year=begin_year)
	latex = reviews_to_latex_longtable(records,start_year=begin_year)
	f.write(latex)
	
	print(records)
	print(len(records))
	return(len(records))

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='This script outputs reviewing data to a latex table that shows a list of journals reviewed for and the number of papers reviewed for each journal in the last [YEARS] years')
	parser.add_argument('-y', '--years',default="3",type=int,help='the number of years to output')
	parser.add_argument('orcid',help='the orcid for the reviewing data')		   
	parser.add_argument('outputfile',help='the output latex table name')
	args = parser.parse_args()
	
	f = open(args.outpufile, 'w') # file to write
	nrows = reviews2latex_far_orcid(f, args.orcid, args.years) # file to write
	f.close()
	
	if (nrows == 0):
		os.remove(args.outputfile)
