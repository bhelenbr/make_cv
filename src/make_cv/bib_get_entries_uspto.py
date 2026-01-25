#!/usr/bin/env python3

"""
Unified USPTO Patent / Application → BibTeX (@misc) pipeline

Accepts:
  - Granted patent numbers        (e.g. 10987654)
  - Publication numbers           (e.g. US20210234567)
  - Application numbers (raw)     (e.g. 19/091,471)
  - Application numbers (numeric) (e.g. 19091471)

Outputs:
  - BibTeX @misc entries suitable for .bib files

Requires:
  - USPTO PatentsView API key
  - Obtain a free API key at https://patentsview.org/apis/api-key-request
  - pip install requests
"""

import requests
import re
from datetime import datetime
from urllib.parse import quote
from typing import Optional

from .bib_get_entries_orcid import make_title_id

# =========================
# API ENDPOINTS
# =========================

PATENT_URL = "https://search.patentsview.org/api/v1/patent"
PUBLICATION_URL = "https://search.patentsview.org/api/v1/publication"

def _resolve_field(record: dict, dotted_key: str):
    """Resolve a possibly dotted key from a PatentsView record.

    Examples:
      'patent_id' -> record['patent_id']
      'granted_pregrant_crosswalk.application_number' ->
         record['granted_pregrant_crosswalk'][0]['application_number']
    Returns None if not found.
    """
    # direct
    if dotted_key in record:
        return record.get(dotted_key)

    # dotted resolution
    if "." not in dotted_key:
        return record.get(dotted_key)

    parts = dotted_key.split(".")
    cur = record
    for part in parts:
        if cur is None:
            return None
        if isinstance(cur, list):
            cur = cur[0] if cur else None
        if isinstance(cur, dict) and part in cur:
            cur = cur.get(part)
        else:
            return None
    return cur

def lookup_patent(identifier: str, api_key: str) -> Optional[str]:
    """Lookup a granted patent record from the PatentsView API and
    return a BibTeX string (or None).
    """
    num_id = identifier.replace(",","").strip()
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    payload = {
        "q": {"patent_id": num_id},
        "f": [
            "patent_id",
            "patent_title",
            "patent_date",
            "inventors.inventor_name_first",
            "inventors.inventor_name_last",
            "assignees.assignee_organization",
        ],
    }

    response = requests.post(PATENT_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    records = response.json().get("patents", [])
    if not records:
        return None
    record = records[0]

    title = record.get("patent_title", "").replace("{", "").replace("}", "")
    inventors = record.get("inventors", [])
    authors = " and ".join(
        f"{i.get('inventor_name_last')}, {i.get('inventor_name_first')}"
        for i in inventors
        if i.get("inventor_name_last")
    )
    assignees = [
        a.get("assignee_organization")
        for a in record.get("assignees", [])
        if a.get("assignee_organization")
    ]
    year = ""
    month = ""
    date_str = record.get("patent_date") 
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year
        month = str(dt.month)
        idstring = make_title_id(title, str(year))
        # build Google Patents URL (prefix with US if numeric)
        gp_id = num_id if re.match(r'^[A-Za-z]', num_id) else f"US{num_id}"
        url = f"https://patents.google.com/patent/{gp_id}"
        bibtex = f"""@misc{{{idstring},
        title        = {{{title}}},
        author       = {{{authors}}},
        year         = {{{year}}},
        month        = {{{month}}},
        keywords      = {{patent}},
        howpublished = {{U.S. Patent {identifier.rstrip(',')}}},
        url          = {{{url}}},
    """
    if assignees:
        bibtex += f"  note         = {{Assignee: {', '.join(assignees)}}},\n"
    bibtex += "}\n"
    return bibtex


def lookup_application(identifier: str, api_key: str) -> Optional[str]:
    """Lookup an application (or related publication) from PatentsView and
    return a BibTeX string (or None).

    This will normalize application numbers like '19/091,471' → '19091471'.
    """
    num_id = identifier.replace(",","").replace("/","").strip()
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}

    query = {"granted_pregrant_crosswalk.application_number": num_id}
    payload = {
        "q": query,
        "f": [
            "granted_pregrant_crosswalk.application_number",
            "document_number",
            "publication_title",
            "publication_date",
            "inventors.inventor_name_first",
            "inventors.inventor_name_last",
            "assignees.assignee_organization",
            "granted_pregrant_crosswalk.current_document_number_flag",
            "granted_pregrant_crosswalk.current_patent_id_flag",
            "granted_pregrant_crosswalk.patent_id",
        ],
    }

    response = requests.post(PUBLICATION_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    records = response.json().get("publications", [])
    if not records:
        return None
    
    # Prefer the record marked as the current document number, if present.
    record = records[0]
    for temp in records:
        flag = _resolve_field(record, "granted_pregrant_crosswalk.current_document_number_flag")
        if flag:
            record = temp
            break

    title = record.get("publication_title", "").replace("{", "").replace("}", "")
    inventors = record.get("inventors", [])
    authors = " and ".join(
        f"{i.get('inventor_name_last')}, {i.get('inventor_name_first')}"
        for i in inventors
        if i.get("inventor_name_last")
    )
    assignees = [
        a.get("assignee_organization")
        for a in record.get("assignees", [])
        if a.get("assignee_organization")
    ]
    year = ""
    month = ""
    date_str = record.get("publication_date")
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year
        month = str(dt.month)
    idstring = make_title_id(title, str(year))
    # Try to extract a direct publication/document id for a per-publication URL
    pub_id = record.get("document_number")
    gp_id = f"US{pub_id}"
    url = f"https://patents.google.com/patent/{gp_id}"
    bibtex = f"""@misc{{{idstring},
title        = {{{title}}},
author       = {{{authors}}},
year         = {{{year}}},
month        = {{{month}}},
keywords      = {{patent}},
howpublished = {{U.S. Patent Application {identifier.rstrip(',')}}},
url          = {{{url}}},
"""
    if assignees:
        bibtex += f"  note         = {{Assignee: {', '.join(assignees)}}},\n"
    bibtex += "}\n"
    return bibtex


def lookup_publication(identifier: str, api_key: str) -> Optional[str]:
    """Lookup a publication/document record from PatentsView and
    return a BibTeX string (or None).
    """
    num_id = identifier.replace(",","").strip()
    num_id = re.sub(r'^[A-Za-z]{2}', '', num_id)

    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    query = {"document_number": num_id}
    payload = {
        "q": query,
        "f": [
            "document_number",
            "publication_title",
            "publication_date",
            "inventors.inventor_name_first",
            "inventors.inventor_name_last",
            "assignees.assignee_organization",
        ],
    }

    response = requests.post(PUBLICATION_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    records = response.json().get("publications", [])
    if not records:
        return None
    record = records[0]

    # Direct field access (no _meta)
    title = record.get("publication_title", "").replace("{", "").replace("}", "")
    inventors = record.get("inventors", [])
    authors = " and ".join(
        f"{i.get('inventor_name_last')}, {i.get('inventor_name_first')}"
        for i in inventors
        if i.get("inventor_name_last")
    )
    assignees = [
        a.get("assignee_organization")
        for a in record.get("assignees", [])
        if a.get("assignee_organization")
    ]
    year = ""
    month = ""
    date_str = record.get("publication_date") 
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year
        month = str(dt.month)
        idstring = make_title_id(title, str(year))
        # Prefer document_number from the API record for a direct link
        pub_id = record.get("document_number")
        gp_id = f"US{pub_id}"
        url = f"https://patents.google.com/patent/{gp_id}"
        bibtex = f"""@misc{{{idstring},
    title        = {{{title}}},
    author       = {{{authors}}},
    year         = {{{year}}},
    month        = {{{month}}},
    keywords      = {{patent}},
    howpublished = {{U.S. Patent Application {identifier.rstrip(',')}}},
    url          = {{{url}}},
"""
    if assignees:
        bibtex += f"  note         = {{Assignee: {', '.join(assignees)}}},\n"
    bibtex += "}\n"
    return bibtex

