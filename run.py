# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import argparse
import os
import re

from scraper import scraper
from mapper import mapper


if __name__ == '__main__':
    # default values
    parties = ['Bloc Québécois',
               'Conservative Party',
               'Green Party',
               'Liberal Party',
               'New Democratic Party',
               ]
    start_year = 2011
    end_year = 2013
    contribs_dir = './contribs'
    results_dir = './results'

    # create directories
    if not os.path.exists(contribs_dir):
        os.makedirs(contribs_dir)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--analyze-only', action='store_true',
                        help="Don't run the scraper, just analyze existing CSV data.")
    parser.add_argument('-p', '--party', '--parties',
                        help="Specify a comma-separated list of party names (or parts thereof).")
    parser.add_argument('-y', '--year', '--years',
                        help="Specify a year or range of years, e.g. 2012 or 2011-2013")
    parser.add_argument('-f', '--federal', action='store_true',
                        help="Search federal party contributions only.")
    parser.add_argument('-r', '--riding', action='store_true',
                        help="Search riding association contributions only.")
    args = parser.parse_args()

    # override party list
    if args.party is not None:
        parties = [party for pstr in args.party.split(',') for party in parties
                   if pstr.strip().lower() in party.lower()]

    # override years
    if args.year is not None:
        m = re.match('(\d{4})(?:-(\d{4}))?', args.year)
        if m is not None:
            start_year = int(m.group(1))
            end_year = int(m.group(2)) if m.group(2) is not None else start_year

    # scrape data from elections website
    if not args.analyze_only:
        for party in parties:
            scraper.scrape_contribs(party, start_year, end_year, contribs_dir,
                                    federal=args.federal, riding=args.riding)

    # analyze data and export for map
    mapper.analyze_contribs(contribs_dir, results_dir)
