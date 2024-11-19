#! /usr/bin/env python3

import pandas as pd
import os
import sys
import numpy as np
from datetime import date
from zipfile import BadZipFile
import argparse

from .stringprotect import str2latex

def shortformteaching(f, years, inputfile):
    source = inputfile  # File to read
    try:
        df = pd.read_excel(source, sheet_name="Data")
    except OSError:
        print("Could not open/read file: " + source)
        return 0
    except BadZipFile:
        print("Error reading file: " + source)
        print("If you open this file with Excel and resave, the problem should go away")
        return 0

    if years > 0:
        today = date.today()
        year = today.year
        begin_year = year - years
        df = df[df['term'].apply(lambda x: int(x[-4:])) >= begin_year]

    if 'course_title' not in df.columns:
        df['course_title'] = ""

    df = df.drop_duplicates(subset=['combined_course_num', 'term'])

    df['course_period'] = df['term'].apply(lambda x: x[-4:])

    grouped = (
        df.groupby(['combined_course_num', 'course_title'])
        .agg(
            min_year=('course_period', 'min'),
            max_year=('course_period', 'max'),
            count=('term', 'size')
        )
        .reset_index()
    )

    grouped['year_range'] = grouped.apply(
    lambda row: row['min_year'] if row['min_year'] == row['max_year'] else f"{row['min_year']}-{row['max_year']}",
    axis=1
    )

    grouped['output'] = grouped.apply(
    lambda row: (
        f"{row['course_title']} {row['combined_course_num']} {row['year_range']} "
        f"({row['count']} semester)" if row['count'] == 1 else 
        f"{row['course_title']} {row['combined_course_num']} {row['year_range']} "
        f"({row['count']} semesters)"
    ),
    axis=1
    )


    if not grouped.empty:
        f.write("\\begin{itemize}\n")
        for _, row in grouped.iterrows():
            f.write(f"  \\item {str2latex(row['output'])}\n")
        f.write("\\end{itemize}\n")

    return len(grouped)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script outputs teaching data to a latex table that shows classes taught in the last [YEARS] years')
    parser.add_argument('-y', '--years', default="-1", type=int, help='the number of years to output, default is all')
    parser.add_argument('-a', '--append', action='store_const', const="a", default="w")
    parser.add_argument('inputfile', help='the input excel file name')
    parser.add_argument('outputfile', help='the output latex table name')
    args = parser.parse_args()

    f = open(args.outputfile, args.append)  # File to write
    nrows = shortformteaching(f, args.years, args.inputfile)
    f.close()

    if nrows == 0:
        os.remove(args.outputfile)


