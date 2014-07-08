# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from scraper import scraper
from mapper import mapper


if __name__ == '__main__':
    parties = ['Bloc Québécois',
               'Conservative Party',
               'Green Party',
               'Liberal Party',
               'New Democratic Party',
               ]

    contribs_dir = './contribs'
    if not os.path.exists(contribs_dir):
        os.makedirs(contribs_dir)

    results_dir = './results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    for party in parties:
        scraper.scrape_contribs(party, 2012, contribs_dir)

    mapper.analyze_contribs(contribs_dir, results_dir)
