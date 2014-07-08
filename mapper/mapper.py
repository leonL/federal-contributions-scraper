from __future__ import unicode_literals

import csv
import json
import os
import unicodedata

import analyze


def analyze_contribs(contribs_dir, results_dir):
    totals = {}
    cities = {}
    postal_groups = {}
    for filename in os.listdir(contribs_dir):
        if filename[-4:] == '.csv':
            csvpath = os.path.join(contribs_dir, filename)
            print 'Reading contributions from {}...'.format(csvpath)
            with open(csvpath, 'rb') as csvfile:
                contribs = [contrib for contrib in csv.reader(csvfile)]

            # normalize json data to composed utf-8 so it will match map.js
            party = unicodedata.normalize('NFC', filename[:-4]).encode('utf-8')

            totals[party] = analyze.sum_total(contribs)
            cities[party] = analyze.sum_city(contribs)
            postal_groups[party] = analyze.sum_postal_groups(contribs)

    export_json(totals, results_dir, 'totals')
    export_json(cities, results_dir, 'cities')
    export_json(postal_groups, results_dir, 'postal_groups')


def read_from_csv(contribs_dir, party):
    csvpath = os.path.join(contribs_dir, party + '.csv')
    print 'Reading contributions from {}...'.format(csvpath)

    with open(csvpath, 'rb') as csvfile:
        return [contrib for contrib in csv.reader(csvfile)]


def export_json(results, results_dir, rname):
    jsonpath = os.path.join(results_dir, rname + '.json')
    print 'Saving results for {} parties to {}...'.format(len(results), jsonpath)

    with open(jsonpath, 'wb') as jsonfile:
        json.dump(results, jsonfile)
