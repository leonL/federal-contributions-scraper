from __future__ import unicode_literals

import csv
import os

import requests

from query import build_query
from search import search_contribs


def scrape_contribs(party, start_year, end_year=None, contribs_dir=None, get_address=True,
                    federal=True, riding=True):
    session = requests.Session()
    contribs = []

    for year in range(start_year, end_year + 1):
        csvpath = (os.path.join(contribs_dir, '{}.{}.csv'.format(party, year))
                   if contribs_dir is not None else None)

        # run each search if they are explicitly enabled, or both if neither are
        if federal or not riding:
            print 'Getting federal party contributions for {} in {}'.format(party, year)
            queryid = build_query(session, party, True, year)
            contribs.extend(search_contribs(session, queryid, True, year, get_address, csvpath))

        if riding or not federal:
            print 'Getting local riding association contributions for {} in {}'.format(party, year)
            queryid = build_query(session, party, False, year)
            contribs.extend(search_contribs(session, queryid, False, year, get_address, csvpath))

    return contribs


def save_to_csv(contribs, contribs_dir, party, year):
    csvpath = os.path.join(contribs_dir, '{}.{}.csv'.format(party, year))
    print 'Saving {} contributions to {}...'.format(len(contribs), csvpath)

    with open(csvpath, 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        for contrib in contribs:
            writer.writerow(contrib)
