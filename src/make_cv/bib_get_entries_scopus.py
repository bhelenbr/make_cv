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


def scopus_bibtex_from_eid(eid):
    try:
        ab = AbstractRetrieval(eid, view="FULL")
        bib = ab.bibtex
        return bib if bib and bib.startswith("@") else None
    except Exception:
        return None


def scopus_metadata(eid):
    ab = AbstractRetrieval(eid, view="STANDARD")
    return {
        "title": ab.title,
        "authors": " and ".join(a.given_name + " " + a.surname for a in ab.authors),
        "year": ab.coverDate[:4] if ab.coverDate else None,
        "journal": ab.publicationName,
        "doi": ab.doi
    }


def build_bibtex(meta):
    cite_key = make_title_id(meta["title"], meta["year"])
    bib = [
        f"@article{{{cite_key},",
        f"  title   = {{{str2latex(meta['title'])}}},",
        f"  author  = {{{meta['authors']}}},",
        f"  journal = {{{str2latex(meta['journal'])}}},",
        f"  year    = {{{meta['year']}}},"
    ]
    if meta.get("doi"):
        bib.append(f"  doi     = {{{meta['doi']}}},")
    bib[-1] = bib[-1].rstrip(",")
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
    eids = author.get_documents()

    for eid in eids:
        try:
            meta = scopus_metadata(eid)
        except Exception:
            continue

        print(meta)

        if not meta["year"] or int(meta["year"]) < begin_year:
            continue

        title_id = make_title_id(meta["title"], meta["year"])
        doi = meta.get("doi")

        # DOI duplicate check
        if doi and any(doi.lower() == d for _, _, d in existing_ids):
            continue

        # Title/year duplicate check
        if any(title_id == t for _, t, _ in existing_ids):
            continue

        # Prefer native Scopus BibTeX
        bib = scopus_bibtex_from_eid(eid)
        if not bib:
            bib = build_bibtex(meta)

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
