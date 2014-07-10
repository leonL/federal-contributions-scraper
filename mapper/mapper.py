from __future__ import unicode_literals

import csv
import json
import os
import re
import unicodedata

import analyze


def analyze_contribs(contribs_dir, results_dir):
    rtypes = ['totals', 'cities', 'postal_groups']
    results = {rtype: {} for rtype in rtypes}

    for filename in os.listdir(contribs_dir):
        m = re.match('(.+)\.(\d{4})\.csv', filename)
        if m is not None:
            # normalize json data to composed utf-8 so it will match map.js
            party = unicodedata.normalize('NFC', m.group(1)).encode('utf-8')
            year = int(m.group(2))

            csvpath = os.path.join(contribs_dir, filename)
            print 'Reading contributions from {}...'.format(csvpath)
            with open(csvpath, 'rb') as csvfile:
                contribs = [contrib for contrib in csv.reader(csvfile)]

            for rtype in rtypes:
                results[rtype].setdefault(year, {})
                results[rtype][year][party] = getattr(analyze, 'sum_' + rtype)(contribs)

    for rtype in rtypes:
        export_json(results[rtype], results_dir, rtype)


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
