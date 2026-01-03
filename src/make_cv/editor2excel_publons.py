#!/usr/bin/env python3

# This script converts .json editor lists from publons into an .csv file
# To run "publons_editor.py <filename> > <outputname.csv>"

import json
import sys

with open(sys.argv[1]) as f:
	data=json.load(f)
	
# 	    "records": {
#         "editor": {
#             "list": [
#                 {
#                     "decision_date": null,
#                     "journal": "Journal of Intelligent Material Systems and Structures",
#                     "title": "Best Pattern for Locating Piezoelectric Patches on Plate for Maximum Critical Buckling Loads, Using PSO Algorithm"
#                 },

for review in data['records']['editor']['list']: 
    print(review['journal'] +'\t' +review['title'] +'\t' +str(review['decision_date']))
