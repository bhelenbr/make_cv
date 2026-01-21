#!/usr/bin/env python3
import os
import re
import argparse
from datetime import date

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexautocomplete import BibtexAutocomplete

from pylatexenc.latex2text import LatexNodes2Text

from pybliometrics.scopus import AuthorRetrieval, AuthorSearch, AbstractRetrieval

from .stringprotect import str2latex
from . import global_prefs

from .bib_add_keywords import add_keyword
from .bib_get_entries_orcid import make_bibtex_id_list
from .bib_get_entries_orcid import make_title_id
from .bib_get_entries_orcid import getyear

# -------------------------------
# Scopus helpers
# -------------------------------

def scopus_author_id_from_name(name):
    res = AuthorSearch(name)
    if not res.authors:
        return None
    return res.authors[0].author_id

def scopus_metadata(ab):
    return {
        "title": ab.title,
        "year": ab.coverDate[:4] if ab.coverDate else None,
        "doi": ab.doi if ab.doi else None,
    }


def build_bibtex(ab):
    # Safe getters
    def _name(a):
        given = getattr(a, "given_name", None) or getattr(a, "givenName", "")
        surname = getattr(a, "surname", None) or getattr(a, "surname", "")
        return (given + " " + surname).strip()

    authors = " and ".join(_name(a) for a in (ab.authors or [])) if getattr(ab, "authors", None) else None
    year = ab.coverDate[:4]
    cite_key = make_title_id(ab.title, year)

    publication = getattr(ab, "publicationName", None)
    pages = getattr(ab, "pageRange", None) or getattr(ab, "pages", None)
    doi = getattr(ab, "doi", None)

    # Determine entry type: book chapter, book, conference (inproceedings), fallback article
    subtype = (getattr(ab, "subtype", "") or "").lower()
    print(subtype)
    if "ch" in subtype:
        entry_type = "incollection"
        primary_container = publication
    elif "bk" in subtype:
        entry_type = "book"
        primary_container = publication
    elif "cp" in subtype:
        entry_type = "inproceedings"
        primary_container = publication
    else:
        entry_type = "article"
        primary_container = publication

    bib = [f"@{entry_type}{{{cite_key},"]

    # Common fields
    if getattr(ab, "title", None):
        bib.append(f"  title   = {{{str2latex(getattr(ab, 'title'))}}},")
    if authors:
        bib.append(f"  author  = {{{authors}}},")
    if getattr(ab,"publisher", None):
        bib.append(f"  publisher   = {{{str2latex(getattr(ab, 'publisher'))}}},")
    if pages:
        bib.append(f"  pages   = {{{pages}}},")
    if year:
        bib.append(f"  year    = {{{year}}},")
    if doi:
        bib.append(f"  doi     = {{{doi}}},")

    if entry_type in ("incollection", "inproceedings"):
        if primary_container:
            bib.append(f"  booktitle = {{{str2latex(primary_container)}}},")

    elif entry_type == "article":
        if primary_container:
            bib.append(f"  journal = {{{str2latex(primary_container)}}},")

    # Trim trailing comma on last field and finish
    if len(bib) > 1:
        bib[-1] = bib[-1].rstrip(',')
    bib.append("}\n")
    return "\n".join(bib)


# -------------------------------
# Main routine
# -------------------------------

def bib_get_entries_scopus(bibfile, author_id, years, outputfile):

    begin_year = date.today().year - years if years > 0 else 0

    tbparser = BibTexParser(common_strings=True)
    tbparser.expect_multiple_parse = True

    with open(bibfile, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f, tbparser)

    entries = bib_db.entries
    existing_ids = make_bibtex_id_list(entries)

    author = AuthorRetrieval(author_id)
    eids = author.get_documents(refresh=10)
    for doc in eids:
        # Extract a usable identifier (EID/Scopus ID/DOI) from the returned document
        eid_val = getattr(doc, "eid")
        ab = AbstractRetrieval(eid_val, view="FULL")
        try:
            meta = scopus_metadata(ab)
        except Exception:
            continue

        if not meta["year"] or int(meta["year"]) < begin_year:
            continue

        title_id = make_title_id(meta["title"], meta["year"])

        # DOI duplicate check
        if meta["doi"] and any(meta["doi"].lower() == d for _, _, d in existing_ids):
            continue

        # Title/year duplicate check
        if any(title_id == t for _, t, _ in existing_ids):
            continue

        # Prefer native Scopus BibTeX for journal articles
        try:
            bib = ab.get_bibtex()
        except Exception:
            bib = None

        if not bib:
            bib = build_bibtex(ab)
            completer = BibtexAutocomplete()
            completer.load_string(bib)
            completer.autocomplete()
            bib = completer.write_string()[0]

        print(bib)

        if not global_prefs.quiet:
            yn = input("Add this entry? Y/N ").upper()
            if yn != "Y":
                continue

        bib_db = bibtexparser.loads(bib, tbparser)

    writer = BibTexWriter()
    writer.order_entries_by = None

    with open(outputfile, "w", encoding="utf-8") as f:
        f.write(bibtexparser.dumps(bib_db, writer))


# -------------------------------
# CLI
# -------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bibfile")
    parser.add_argument("-sid", "--scopus_id", required=True)
    parser.add_argument("-y", "--years", type=int, default=1)
    parser.add_argument("-o", "--output", default="scopus.bib")
    args = parser.parse_args()

    bib_get_entries_scopus(args.bibfile, args.scopus_id, args.years, args.output)
