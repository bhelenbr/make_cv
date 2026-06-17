#!/usr/bin/env python3
"""
USPTO Open Data Portal (ODP) Patent / Application -> BibTeX

Supports:
    - Patent numbers          (e.g. 10987654)
    - Publication numbers     (e.g. US20210234567A1)
    - Application numbers     (e.g. 19/091,471 or 19091471)

Requires:
    pip install requests
"""

import re
from datetime import datetime
from typing import Optional

import requests

from .bib_get_entries_orcid import make_title_id

SEARCH_URL = "https://api.uspto.gov/api/v1/patent/applications/search"
APPLICATION_URL = "https://api.uspto.gov/api/v1/patent/applications/{app}"


def _headers(api_key: str) -> dict:
    return {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def normalize_application_number(identifier: str) -> str:
    return re.sub(r"[^0-9]", "", identifier)


def normalize_publication_number(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", identifier).upper()


def search_applications(
    query: str,
    api_key: str,
    fields=None,
    limit: int = 25,
) -> dict:

    payload = {
        "q": query,
        "pagination": {
            "offset": 0,
            "limit": limit,
        },
    }

    if fields:
        payload["fields"] = fields

    try:
        response = requests.post(
            SEARCH_URL,
            json=payload,
            headers=_headers(api_key),
            timeout=30,
        )
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # e.g., 404 Client Error
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

    return response.json()


def get_application(application_number: str, api_key: str) -> dict:

    try:
        response = requests.get(
            APPLICATION_URL.format(app=application_number),
            headers=_headers(api_key),
            timeout=30,
        )

        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # e.g., 404 Client Error
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

    data = response.json()

    records = data.get("patentFileWrapperDataBag", [])
    if not records:
        print(f"No application record found for {application_number}")
        return None 

    return records[0]


def _extract_assignees(record: dict) -> list:

    assignees = []

    for assignment in record.get("assignmentBag", []):
        for assignee in assignment.get("assigneeBag", []):
            name = assignee.get("assigneeNameText")
            if name:
                assignees.append(name)

    return list(dict.fromkeys(assignees))


def _extract_authors(meta: dict) -> str:

    authors = []

    for inventor in meta.get("inventorBag", []):

        first = inventor.get("firstName", "")
        last = inventor.get("lastName", "")

        if last:
            authors.append(f"{last}, {first}")

    return " and ".join(authors)


def record_to_bibtex(record: dict) -> Optional[str]:

    if record is None:
        return None

    meta = record.get("applicationMetaData", {})

    title = (
        meta.get("inventionTitle", "")
        .replace("{", "")
        .replace("}", "")
    )

    if not title:
        return None

    authors = _extract_authors(meta)
    assignees = _extract_assignees(record)

    patent_number = meta.get("patentNumber")
    publication_number = meta.get("earliestPublicationNumber")
    application_number = record.get("applicationNumberText")

    date_str = (
        meta.get("grantDate")
        or meta.get("earliestPublicationDate")
        or meta.get("filingDate")
    )

    year = ""
    month = ""

    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            year = str(dt.year)
            month = str(dt.month)
        except Exception:
            pass

    idstring = make_title_id(title, year)

    if patent_number:
        howpublished = f"U.S. Patent {patent_number}"
        url = f"https://patents.google.com/patent/US{patent_number}"

    elif publication_number:
        pub = normalize_publication_number(publication_number)
        howpublished = f"U.S. Patent Application {publication_number}"
        url = f"https://patents.google.com/patent/{pub}"

    else:
        howpublished = (
            f"U.S. Patent Application {application_number}"
        )
        url = ""

    bibtex = f"""@misc{{{idstring},
  title        = {{{title}}},
  author       = {{{authors}}},
  year         = {{{year}}},
  month        = {{{month}}},
  keywords     = {{patent}},
  howpublished = {{{howpublished}}},"""

    if url:
        bibtex += f"\n  url          = {{{url}}},"

    if assignees:
        bibtex += (
            f"\n  note         = {{Assignee: {', '.join(assignees)}}},"
        )

    bibtex += "\n}\n"

    return bibtex


def lookup_application(
    identifier: str,
    api_key: str,
) -> Optional[str]:

    app_number = normalize_application_number(identifier)

    record = get_application(app_number, api_key)

    return record_to_bibtex(record)


def lookup_patent(
    identifier: str,
    api_key: str,
) -> Optional[str]:

    patent_number = re.sub(r"\D", "", identifier)

    response = search_applications(
        f"applicationMetaData.patentNumber:{patent_number}",
        api_key,
        fields=["applicationNumberText"],
        limit=1,
    )
    if response is None:
        return None

    records = response.get("patentFileWrapperDataBag", [])

    if not records:
        return None

    app_number = records[0]["applicationNumberText"]

    record = get_application(app_number, api_key)

    return record_to_bibtex(record)


def lookup_publication(
    identifier: str,
    api_key: str,
) -> Optional[str]:

    pub = normalize_publication_number(identifier)

    response = search_applications(
        f'applicationMetaData.earliestPublicationNumber:"{pub}"',
        api_key,
        fields=["applicationNumberText"],
        limit=1,
    )

    if response is None:
        return None

    records = response.get("patentFileWrapperDataBag", [])

    if not records:
        return None

    app_number = records[0]["applicationNumberText"]

    record = get_application(app_number, api_key)

    return record_to_bibtex(record)
