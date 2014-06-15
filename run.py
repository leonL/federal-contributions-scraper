import csv
import json
import os

import requests

import query
import scraper


with open('postal code groups.csv', 'rb') as csvfile:
    points = {line[0]: line[1:] for line in csv.reader(csvfile)}

if not os.path.exists('./totals'):
    os.makedirs('./totals')

session = requests.Session()


parties = ['Conservative', 'Liberal', 'New Democrat', 'Green', 'Bloc']
year = 2012

for party in parties:
    print 'Getting federal party contributions for', party
    queryid = query.start_query(session, party, True, year)
    contribs = scraper.scrape(session, queryid, True, year)

    print 'Getting local riding association contributions for', party
    queryid = query.start_query(session, party, False, year)
    contribs.extend(scraper.scrape(session, queryid, False, year))

    # get total amount for each postal code group
    code_totals = {}
    for contrib in contribs:
        amount = contrib[4]
        code = contrib[7][:3]

        code_totals.setdefault(code, 0)
        code_totals[code] += amount

    stats = [{
            'PostalCode': code,
            'Lat': points[code][0],
            'Lng': points[code][1],
            'Amount': amount,
        } for code, amount in code_totals.iteritems()]

    with open('./totals/{}.json'.format(party), 'wb') as jsonfile:
        json.dump(stats, jsonfile)
