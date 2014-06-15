import requests

import parser
import query
import scraper


federal = True
get_address = True
year = 2012
party = None

session = requests.Session()

queryid = query.start_query(session, party, federal)

contribs = scraper.scrape(session, queryid, federal, get_address)
for i in contribs:
    print i

#jsondata = parser.get_map_json(contribs)
#print jsondata
