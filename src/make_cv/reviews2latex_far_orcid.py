#!/usr/bin/env python3

import requests
from collections import defaultdict

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
    summary = group["peer-review-summary"][0]
    review = summary.get("peer-review", {})

    subject = review.get("subject", {})
    journal = subject.get("journal-title", {}).get("value")

    convening_org = review.get("convening-organization", {})
    organization = convening_org.get("name")

    year = (
        review.get("review-completion-date", {})
        .get("year", {})
        .get("value")
    )

    # Prefer journal title; fall back to organization
    venue = journal or organization

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
            if start_year and (year is None or year < start_year):
                continue

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


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
    ORCID_ID = "0000-0002-1825-0097"  # ← replace
    START_YEAR = 2020               # ← CV cutoff (or None)

    records = collect_and_group_reviews(
        ORCID_ID,
        start_year=START_YEAR
    )

    latex = reviews_to_latex_longtable(
        records,
        start_year=START_YEAR
    )

    with open("peer_review_activity.tex", "w", encoding="utf-8") as f:
        f.write(latex)

    print("Wrote peer_review_activity.tex")
