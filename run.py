# -*- coding: utf-8 -*-

import codecs
import csv
import json
import os

import requests

import analyze
import query
import scraper


def scrape_contribs(party, year, get_address=True, save_csv=True):
    session = requests.Session()

    csvpath = u'./contribs/{}.csv'.format(party) if save_csv else None

    print
    print 'Getting federal party contributions for', party
    queryid = query.start_query(session, party, True, year)
    contribs = scraper.scrape(session, queryid, True, year, get_address, csvpath)

    print
    print 'Getting local riding association contributions for', party
    queryid = query.start_query(session, party, False, year)
    contribs.extend(scraper.scrape(session, queryid, False, year, get_address, csvpath))

    return contribs


def save_to_csv(contribs, filename):
    if not os.path.exists('./contribs'):
        os.makedirs('./contribs')

    print
    print u'Saving {} contributions to ./contribs/{}.csv...'.format(len(contribs), filename)
    with open(u'./contribs/{}.csv'.format(filename), 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')

        for contrib in contribs:
            writer.writerow([unicode(field).encode('utf-8') for field in contrib])


def read_from_csv(filename):
    print u'Reading ./contribs/{}.csv...'.format(filename)
    with open(u'./contribs/{}.csv'.format(filename), 'rb') as csvfile:
        return [contrib for contrib in csv.reader(csvfile)]


def export_json(results, filename):
    if not os.path.exists('./results'):
        os.makedirs('./results')

    print 'Saving results for {} parties to ./results/{}.json...'.format(len(results), filename)
    with codecs.open(u'./results/{}.json'.format(filename), 'wb', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile)


if __name__ == '__main__':
    parties = [u'Bloc Québécois',
               u'Conservative Party',
               u'Green Party',
               u'Liberal Party',
               u'New Democratic Party',
               ]

    for party in parties:
        contribs = scrape_contribs(party, 2012)

    totals = {}
    cities = {}
    postal_groups = {}
    for csvfile in os.listdir(u'./contribs'):
        if csvfile[-4:] == '.csv':
            party = csvfile[:-4]
            contribs = read_from_csv(party)

            totals[party] = analyze.sum_total(contribs)
            cities[party] = analyze.sum_city(contribs)
            postal_groups[party] = analyze.sum_postal_groups(contribs)

    export_json(totals, 'totals')
    export_json(cities, 'cities')
    export_json(postal_groups, 'postal_groups')
