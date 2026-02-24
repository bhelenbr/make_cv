#!/usr/bin/env python3
import os
import re
import argparse
from datetime import date
import requests
import xml.etree.ElementTree as ET

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexautocomplete import BibtexAutocomplete

from pylatexenc.latex2text import LatexNodes2Text

from .stringprotect import str2latex
from . import global_prefs

from .bib_add_keywords import add_keyword
from .bib_get_entries_orcid import make_bibtex_id_list
from .bib_get_entries_orcid import make_title_id
from .bib_get_entries_orcid import getyear


# -------------------------------
# PubMed helpers
# -------------------------------

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def pubmed_author_search(author_name):
    params = {
        "db": "pubmed",
        "term": f"{author_name}[Author]",
        "retmax": 500,
        "retmode": "json",
    }
    r = requests.get(BASE + "esearch.fcgi", params=params)
    r.raise_for_status()
    return r.json()["esearchresult"]["idlist"]


def pubmed_fetch_record(pmid):
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }
    r = requests.get(BASE + "efetch.fcgi", params=params)
    r.raise_for_status()
    return ET.fromstring(r.text)


def pubmed_metadata(article_xml):
    article = article_xml.find(".//Article")
    if article is None:
        return None

    title_elem = article.find("ArticleTitle")
    journal_elem = article.find(".//Journal/Title")
    year_elem = article.find(".//PubDate/Year")

    if year_elem is None:
        medline = article.find(".//PubDate/MedlineDate")
        year = medline.text[:4] if medline is not None else None
    else:
        year = year_elem.text

    doi = None
    for aid in article_xml.findall(".//ArticleId"):
        if aid.attrib.get("IdType") == "doi":
            doi = aid.text
            break

    return {
        "title": title_elem.text if title_elem is not None else None,
        "year": year,
        "doi": doi,
        "journal": journal_elem.text if journal_elem is not None else None,
    }


def build_bibtex(article_xml):
    article = article_xml.find(".//Article")

    title = article.find("ArticleTitle")
    journal = article.find(".//Journal/Title")
    volume = article.find(".//JournalIssue/Volume")
    issue = article.find(".//JournalIssue/Issue")
    pages = article.find(".//Pagination/MedlinePgn")
    year_elem = article.find(".//PubDate/Year")

    if year_elem is None:
        medline = article.find(".//PubDate/MedlineDate")
        year = medline.text[:4] if medline is not None else None
    else:
        year = year_elem.text

    authors = []
    for author in article.findall(".//Author"):
        last = author.find("LastName")
        initials = author.find("Initials")
        if last is not None and initials is not None:
            authors.append(f"{initials.text} {last.text}")

    author_str = " and ".join(authors)

    cite_key = make_title_id(title.text if title is not None else "unknown", year)

    bib = [f"@article{{{cite_key},"]

    if title is not None:
        bib.append(f"  title   = {{{str2latex(title.text)}}},")
    if author_str:
        bib.append(f"  author  = {{{author_str}}},")
    if journal is not None:
        bib.append(f"  journal = {{{str2latex(journal.text)}}},")
    if volume is not None:
        bib.append(f"  volume  = {{{volume.text}}},")
    if issue is not None:
        bib.append(f"  number  = {{{issue.text}}},")
    if pages is not None:
        bib.append(f"  pages   = {{{pages.text}}},")
    if year:
        bib.append(f"  year    = {{{year}}},")

    doi = None
    for aid in article_xml.findall(".//ArticleId"):
        if aid.attrib.get("IdType") == "doi":
            doi = aid.text
            break
    if doi:
        bib.append(f"  doi     = {{{doi}}},")

    if len(bib) > 1:
        bib[-1] = bib[-1].rstrip(",")

    bib.append("}\n")
    return "\n".join(bib)


# -------------------------------
# Main routine
# -------------------------------

def bib_get_entries_pubmed(bibfile, author_name, years, outputfile):

    begin_year = date.today().year - years if years > 0 else 0

    tbparser = BibTexParser(common_strings=True)
    tbparser.expect_multiple_parse = True

    with open(bibfile, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f, tbparser)

    entries = bib_db.entries
    existing_ids = make_bibtex_id_list(entries)

    pmids = pubmed_author_search(author_name)

    for pmid in pmids:
        try:
            xml_root = pubmed_fetch_record(pmid)
            meta = pubmed_metadata(xml_root)
        except Exception:
            continue

        if not meta or not meta["year"] or int(meta["year"]) < begin_year:
            continue

        title_id = make_title_id(meta["title"], meta["year"])

        # DOI duplicate check
        if meta["doi"] and any(meta["doi"].lower() == d for _, _, d in existing_ids):
            continue

        # Title/year duplicate check
        if any(title_id == t for _, t, _ in existing_ids):
            continue

        bib = build_bibtex(xml_root)

        completer = BibtexAutocomplete()
        completer.load_string(bib)
        completer.autocomplete()
        bib = completer.write_string()[0]
        bib = str2latex(bib)

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
    parser.add_argument("-a", "--author", required=True)
    parser.add_argument("-y", "--years", type=int, default=1)
    parser.add_argument("-o", "--output", default="pubmed.bib")
    args = parser.parse_args()

    bib_get_entries_pubmed(args.bibfile, args.author, args.years, args.output)