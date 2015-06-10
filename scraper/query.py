from urlparse import urlparse, parse_qs

from bs4 import BeautifulSoup


FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/SelectParties'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/SelectAssociations'


def build_query(session, party=None, federal=True, year=2012, q_reports=False):
    base_uri = FEDERAL_URI if federal else RIDING_URI

    act = "C2"
    if year < 2007:
        act = "C24"
    elif year == 2015:
        act = "C23"

    params = {
        'act': act,
        'returntype': 1,
        'period': 1 if q_reports else 0,
        }

    # get search form
    req = session.get(base_uri, params=params)
    soup = BeautifulSoup(req.text)

    params['queryid'] = parse_qs(urlparse(soup.form.get('action')).query)['queryid'][0]

    partyid = (-1 if not party else
               next(opt.get('value') for opt in soup.find(id='partylist').find_all('option')
                    if party in opt.get_text()))

    postdata = {
        'fromperiod': year,
        'toperiod': year,
        'party': partyid,
        }

    postdata.update({
        'AddParties': 'Find',
        } if federal else {
        'AddAssociations': 'Find Association(s)',
        'district':-1,
        'province':-1,
        })

    # get search options for selected party
    req = session.post(base_uri, params=params, data=postdata)
    soup = BeautifulSoup(req.text)

    options = soup.find(id='partiesSelectedIds' if federal else 'selectedids').find_all('option')

    postdata = {
        'SearchSelected': 'Search selected',
        'fromperiod': year,
        'toperiod': year,
        'party': partyid,
        'returntype': 1,
        }

    postdata.update({
        'partiesSelectedIds': [opt.get('value') for opt in options],
        } if federal else {
        'selectedids': [opt.get('value') for opt in options],
        'district':-1,
        'province':-1,
        })

    print 'Found {} return(s).'.format(len(options))
    print

    # search for selected returns
    req = session.post(base_uri, params=params, data=postdata)
    soup = BeautifulSoup(req.text)

    # new queryid: search parameters are now stored server side for this queryid in this session
    return parse_qs(urlparse(soup.find(id='SelectPart2lnk').get('href')).query)['queryid'][0]
