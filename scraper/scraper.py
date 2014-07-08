from __future__ import unicode_literals

import csv
import os

import requests

import query
import search


def scrape_contribs(party, year, contribs_dir=None, get_address=True):
    session = requests.Session()

    csvpath = os.path.join(contribs_dir, party + '.csv') if contribs_dir is not None else None

    print 'Getting federal party contributions for', party
    queryid = query.build_query(session, party, True, year)
    contribs = search.search_contribs(session, queryid, True, year, get_address, csvpath)

    print 'Getting local riding association contributions for', party
    queryid = query.build_query(session, party, False, year)
    contribs.extend(search.search_contribs(session, queryid, False, year, get_address, csvpath))

    return contribs


def save_to_csv(contribs, contribs_dir, party):
    csvpath = os.path.join(contribs_dir, party + '.csv')
    print 'Saving {} contributions to {}...'.format(len(contribs), csvpath)

    with open(csvpath, 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        for contrib in contribs:
            writer.writerow(contrib)
