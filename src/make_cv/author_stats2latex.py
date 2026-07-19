# Load bibfile
	
import json
import os
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bparser import BibTexParser

def author_stats2latex(f,bibfile):
    tbparser = BibTexParser(common_strings=True)
    tbparser.alt_dict['url'] = 'url'	# this prevents change 'url' to 'link'
    tbparser.expect_multiple_parse = True
    with open(bibfile, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, tbparser)

    author_stats_string = [c for c in bib_database.comments if c.startswith('author_stats')]
    author_stats = json.loads(author_stats_string[0].split('author_stats: ')[1]) if author_stats_string else {}

    if author_stats:
        f.write("\\par\nGoogle Stats -- ")
        f.write("Hindex: " + str(author_stats.get('hindex', '')) +", ")
        f.write("i10index: " + str(author_stats.get('i10index', '')) +", ")
        f.write("Cites: " + str(author_stats.get('citedby', '')) +", ")
        f.write("Hindex 5y: " + str(author_stats.get('hindex5y', ''))  +", ")
        f.write("i10index 5y: " + str(author_stats.get('i10index5y', ''))  +", ")
        f.write("Cites 5y: " + str(author_stats.get('citedby5y', ''))  +"\n")
        return True
    else:
        return False