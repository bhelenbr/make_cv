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
from typing import Optional


# =========================
# API ENDPOINTS
# =========================

PATENT_URL = "https://search.patentsview.org/api/v1/patent"
PUBLICATION_URL = "https://search.patentsview.org/api/v1/publication"


# =========================
# IDENTIFIER HANDLING
# =========================

def normalize_application_number(app_no: str) -> str:
    """
    Convert '19/091,471' → '19091471'
    """
    return app_no.replace("/", "").replace(",", "").strip()


def classify_identifier(identifier: str) -> str:
    """
    Classify identifier as:
      - 'patent'
      - 'publication'
      - 'application'
    """
    identifier = identifier.strip()

    if re.match(r"^[A-Z]{2}\d{4}", identifier):
        return "publication"

    if "/" in identifier or "," in identifier:
        return "application"

    if identifier.isdigit() and len(identifier) >= 7:
        return "patent"

    raise ValueError(f"Unrecognized identifier format: {identifier}")


# =========================
# LOOKUP LOGIC
# =========================

def lookup_record(identifier: str, api_key: str) -> Optional[dict]:
    """
    Lookup a patent, publication, or application and return
    a normalized record with metadata for BibTeX conversion.
    """

    id_type = classify_identifier(identifier)

    headers = {
        "X-Api-Key": api_key,
        "Accept": "application/json"
    }

    # ---- Granted Patent ----
    if id_type == "patent":
        payload = {
            "q": {"patent_id": identifier},
            "f": [
                "patent_id",
                "patent_title",
                "patent_date",
                "inventors.inventor_name_first",
                "inventors.inventor_name_last",
                "assignees.assignee_organization"
            ]
        }
        url = PATENT_URL
        record_key = "patents"
        meta = {
            "id": "patent_id",
            "title": "patent_title",
            "date": "patent_date",
            "label": "U.S. Patent"
        }

    # ---- Publication or Application ----
    else:
        if id_type == "application":
            identifier = normalize_application_number(identifier)
            query = {"application_number": identifier}
        else:
            query = {"publication_number": identifier}

        payload = {
            "q": query,
            "f": [
                "publication_number",
                "publication_title",
                "publication_date",
                "application_number",
                "inventors.inventor_name_first",
                "inventors.inventor_name_last",
                "assignees.assignee_organization"
            ]
        }
        url = PUBLICATION_URL
        record_key = "publications"
        meta = {
            "id": "publication_number",
            "title": "publication_title",
            "date": "publication_date",
            "label": "U.S. Patent Application"
        }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    records = response.json().get(record_key, [])
    if not records:
        return None

    record = records[0]
    record["_meta"] = meta
    return record


# =========================
# BIBTEX CONVERSION
# =========================

def record_to_bibtex_misc(record: dict) -> str:
    """
    Convert a PatentsView record to BibTeX @misc
    """

    meta = record["_meta"]

    identifier = record.get(meta["id"], "unknown")

    title = (
        record.get(meta["title"], "")
        .replace("{", "")
        .replace("}", "")
    )

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
    date_str = record.get(meta["date"])
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year
        month = dt.strftime("%b").lower()

    bibtex = f"""@misc{{{identifier},
  title        = {{{title}}},
  author       = {{{authors}}},
  year         = {{{year}}},
  month        = {{{month}}},
  howpublished = {{{meta["label"]} {identifier}}},
"""

    if assignees:
        bibtex += f"  note         = {{Assignee: {', '.join(assignees)}}},\n"

    bibtex += "}\n"
    return bibtex


# =========================
# ONE-CALL PIPELINE
# =========================

def identifier_to_bibtex(identifier: str, api_key: str) -> Optional[str]:
    """
    Main public API:
      identifier → BibTeX @misc entry
    """
    record = lookup_record(identifier, api_key)
    if not record:
        return None
    return record_to_bibtex_misc(record)


# =========================
# EXAMPLE USAGE
# =========================
if __name__ == "__main__":

    API_KEY = "YOUR_API_KEY_HERE"

    identifiers = [
        "10987654",        # granted patent
        "US20210234567",   # publication
        "19/091,471",      # raw application number
        "19091471"         # normalized application number
    ]

    with open("patents.bib", "w", encoding="utf-8") as f:
        for ident in identifiers:
            bib = identifier_to_bibtex(ident, API_KEY)
            if bib:
                f.write(bib + "\n")
            else:
                print(f"No record found for {ident}")
