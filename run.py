# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv
import json
import os

import requests

import analyze
import query
import scraper


def scrape_contribs(party, year, get_address=True, save_csv=True):
    session = requests.Session()

    csvpath = './contribs/{}.csv'.format(party) if save_csv else None

    print 'Getting federal party contributions for', party
    queryid = query.start_query(session, party, True, year)
    contribs = scraper.scrape(session, queryid, True, year, get_address, csvpath)

    print 'Getting local riding association contributions for', party
    queryid = query.start_query(session, party, False, year)
    contribs.extend(scraper.scrape(session, queryid, False, year, get_address, csvpath))

    return contribs


def save_to_csv(contribs, filename):
    if not os.path.exists('./contribs'):
        os.makedirs('./contribs')

    print 'Saving {} contributions to ./contribs/{}.csv...'.format(len(contribs), filename)
    with open('./contribs/{}.csv'.format(filename), 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')

        for contrib in contribs:
            writer.writerow(contrib)


def read_from_csv(filename):
    print 'Reading ./contribs/{}.csv...'.format(filename)
    with open('./contribs/{}.csv'.format(filename), 'rb') as csvfile:
        return [contrib for contrib in csv.reader(csvfile)]


def export_json(results, filename):
    if not os.path.exists('./results'):
        os.makedirs('./results')

    print 'Saving results for {} parties to ./results/{}.json...'.format(len(results), filename)
    with open('./results/{}.json'.format(filename), 'wb') as jsonfile:
        json.dump(results, jsonfile)


if __name__ == '__main__':
    parties = ['Bloc Québécois',
               'Conservative Party',
               'Green Party',
               'Liberal Party',
               'New Democratic Party',
               ]

    for party in parties:
        contribs = scrape_contribs(party, 2012)

    totals = {}
    cities = {}
    postal_groups = {}
    for csvfile in os.listdir('./contribs'):
        if csvfile[-4:] == '.csv':
            party = csvfile[:-4]
            contribs = read_from_csv(party)

            totals[party] = analyze.sum_total(contribs)
            cities[party] = analyze.sum_city(contribs)
            postal_groups[party] = analyze.sum_postal_groups(contribs)

    export_json(totals, 'totals')
    export_json(cities, 'cities')
    export_json(postal_groups, 'postal_groups')
