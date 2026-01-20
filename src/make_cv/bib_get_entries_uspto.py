import requests
from datetime import datetime

BASE_URL = "https://search.patentsview.org/api/v1/patent"


def search_patents_by_title(title_query, api_key, limit=25):
    query = {
        "_text_any": {
            "patent_title": title_query
        }
    }

    fields = [
        "patent_id",
        "patent_title",
        "patent_date",
        "inventors.inventor_name_first",
        "inventors.inventor_name_last",
        "assignees.assignee_organization"
    ]

    payload = {
        "q": query,
        "f": fields,
        "o": {"per_page": limit}
    }

    headers = {
        "X-Api-Key": api_key,
        "Accept": "application/json"
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("patents", [])


def patent_to_bibtex_misc(patent):
    """
    Convert a PatentsView patent record to a BibTeX @misc entry.
    """

    patent_id = patent.get("patent_id", "unknown_patent")

    title = patent.get("patent_title", "").replace("{", "").replace("}", "")

    inventors = patent.get("inventors", [])
    authors = " and ".join(
        f"{i.get('inventor_name_last','')}, {i.get('inventor_name_first','')}"
        for i in inventors
        if i.get("inventor_name_last")
    )

    assignees = patent.get("assignees", [])
    assignee_names = [
        a.get("assignee_organization")
        for a in assignees
        if a.get("assignee_organization")
    ]

    patent_date = patent.get("patent_date")
    year = ""
    month = ""
    if patent_date:
        dt = datetime.strptime(patent_date, "%Y-%m-%d")
        year = dt.year
        month = dt.strftime("%b").lower()

    bibtex = f"""@misc{{{patent_id},
  title        = {{{title}}},
  author       = {{{authors}}},
  year         = {{{year}}},
  month        = {{{month}}},
  howpublished = {{U.S. Patent {patent_id}}},
"""

    if assignee_names:
        bibtex += f"  note         = {{Assignee: {', '.join(assignee_names)}}},\n"

    bibtex += "}\n"

    return bibtex


def search_title_to_bibtex(title_query, api_key, limit=10):
    patents = search_patents_by_title(title_query, api_key, limit)
    return [patent_to_bibtex_misc(p) for p in patents]
