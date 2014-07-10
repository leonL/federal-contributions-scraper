from __future__ import unicode_literals

import csv
import os

import requests

import query
import search


def scrape_contribs(party, start_year, end_year=None, contribs_dir=None, get_address=True):
    session = requests.Session()
    contribs = []

    for year in range(start_year, end_year + 1):
        csvpath = (os.path.join(contribs_dir, '{}.{}.csv'.format(party, year))
                   if contribs_dir is not None else None)

        print 'Getting federal party contributions for {} in {}'.format(party, year)
        queryid = query.build_query(session, party, True, year)
        contribs.extend(search.search_contribs(session, queryid, True, year, get_address, csvpath))

        print 'Getting local riding association contributions for {} in {}'.format(party, year)
        queryid = query.build_query(session, party, False, year)
        contribs.extend(search.search_contribs(session, queryid, False, year, get_address, csvpath))

    return contribs


def save_to_csv(contribs, contribs_dir, party, year):
    csvpath = os.path.join(contribs_dir, '{}.{}.csv'.format(party, year))
    print 'Saving {} contributions to {}...'.format(len(contribs), csvpath)

    with open(csvpath, 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        for contrib in contribs:
            writer.writerow(contrib)
