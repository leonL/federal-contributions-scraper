# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import codecs
import csv
import json
import os

import requests

import query
import scraper


def scrape_contribs(parties, year):
    session = requests.Session()

    print
    print 'Getting federal party contributions for', party
    queryid = query.start_query(session, party, True, year)
    contribs = scraper.scrape(session, queryid, True, year)

    print
    print 'Getting local riding association contributions for', party
    queryid = query.start_query(session, party, False, year)
    contribs.extend(scraper.scrape(session, queryid, False, year))

    return contribs


def save_to_csv(contribs, filename):
    if not os.path.exists('./contribs'):
        os.makedirs('./contribs')

    print
    print 'Saving {} contributions to ./contribs/{}.csv...'.format(len(contribs), filename)
    with open('./contribs/{}.csv'.format(filename), 'wb') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')

        for contrib in contribs:
            writer.writerow([unicode(field).encode('utf-8') for field in contrib])


def read_from_csv(filename):
    print
    print 'Reading ./contribs/{}.csv...'.format(filename)
    with open('./contribs/{}.csv'.format(filename), 'rb') as csvfile:
        return [contrib for contrib in csv.reader(csvfile)]


def sum_postal_groups(contribs):
    print
    print 'Totalling contribution amounts for each postal code group...'
    totals = {}
    for contrib in contribs:
        amount = float(contrib[4])
        code = contrib[7][:3]

        totals.setdefault(code, 0)
        totals[code] += amount

    with open('./postal code groups.csv', 'rb') as csvfile:
        points = {line[0]: line[1:] for line in csv.reader(csvfile)}

    return [{'PostalCode': code,
              'Lat': points[code][0],
              'Lng': points[code][1],
              'Amount': amount,
              } for code, amount in totals.iteritems()]


def export_json(stats, filename):
    if not os.path.exists('./totals'):
        os.makedirs('./totals')

    print 'Saving {} postal groups to ./totals/{}.json...'.format(len(stats), filename)
    with codecs.open('./totals/{}.json'.format(filename), 'wb', encoding='utf-8') as jsonfile:
        json.dump(stats, jsonfile, ensure_ascii=False)


if __name__ == '__main__':
    parties = ['Bloc Québécois',
               'Conservative Party',
               'Green Party',
               'Liberal Party',
               'New Democratic Party',
               ]

    for party in parties:
        contribs = scrape_contribs(party, 2012)
        save_to_csv(contribs, party)

    stats = {}
    for csvfile in os.listdir(u'./contribs'):
        if csvfile[-4:] == '.csv':
            stats[csvfile[:-4]] = sum_postal_groups(read_from_csv(csvfile[:-4]))

    export_json(stats, 'totals')
