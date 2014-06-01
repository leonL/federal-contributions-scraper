import parser
import scraper


queryid = '289c7d6912724a42b9c4e63462d224bb'
sessionid = 'ppbz0qkvoa3hh3ez0k4ywayq'
federal = True
get_address = True
year = 2012

contribs = scraper.scrape(queryid, sessionid, federal, get_address)
for i in contribs:
    print i

#jsondata = parser.get_map_json(contribs)
#print jsondata
