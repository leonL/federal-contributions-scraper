import re
import time

from bs4 import BeautifulSoup, SoupStrainer


FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/DetailedReport'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/DetailedReport'


def scrape(session, queryid, federal=True, year=2012, get_address=True):
    base_uri = FEDERAL_URI if federal else RIDING_URI
    params = {'act': 'C2',
              'returntype': 1,
              'option': 2,
              'part': '2A',
              'period': 0,
              'fromperiod': year,
              'toperiod': year,
              'queryid': queryid,
              }

    start_time = time.time()

    contribs = []

    # get list of federal parties or riding associations
    req = session.get(base_uri, params=params)
    soup = BeautifulSoup(req.text)

    select = soup.find('select', id='selectedid')
    if not select:
        raise Exception('Error: no selectbox found on page. Try a new query ID.')

    # iterate through list of federal parties or riding associations
    options = select.find_all('option')
    for o, option in enumerate(options):
        params['selectedid'] = option['value']
        subcat = option.get_text().split(' /', 1)[0]

        print
        print 'Search {} of {}:'.format(o + 1, len(options)), subcat.encode('utf8')
        subcat_contribs = subcat_search(session, base_uri, params, get_address)
        contribs.extend([(subcat,) + result for result in subcat_contribs])

    total_time = time.time() - start_time
    print 'Total time: {} minute(s) {} second(s)'.format(int(total_time / 60), int(total_time % 60))

    return contribs


def subcat_search(session, base_uri, params, get_address=True):
    contribs = []

    page = 1
    pages = 1
    postal_params = params.copy()
    while page <= pages:
        print 'Reading page', ('1...' if pages == 1 else '{0} of {1}...'.format(page, pages)),

        params['page'] = page
        req = session.get(base_uri, params=params)
        soup = BeautifulSoup(req.text)

        if page == 1:
            # check for multiple pages
            nextlink = soup.find('a', id='next200pagelink')
            if nextlink:
                m = re.search('totalpages=(\d+)', nextlink['href'])
                pages = int(m.group(1))
                print pages, 'page(s) found.'.format(pages)
        page += 1

        table = soup.find('table', class_='DataTable')
        if not table:
            if soup.find(class_='nodatamessage'):
                print 'No results for this search.'
                continue

            raise Exception('Error: no table on page. Try a new query ID.')

        page_contribs = []
        rows = table.find('tbody').find_all('tr', recursive=False)
        print '{} result(s).'.format(len(rows))
        for row in rows:
            cells = row.find_all('td')

            num = cells[0].get_text().strip()
            # skip empty id numbers
            if not num:
                continue
            # remove weird decimals from id numbers
            for ch in ',.':
                if ch in num:
                    num = num.split(ch, 1)[0]

            page_contribs.append((int(num), # number
                                  cells[1].get_text().strip(), # full name
                                  cells[2].get_text().strip(), # date
                                  float(cells[5].get_text().replace(',', '')), # total amount
                                  '', '', ''))

        if get_address:
            print 'Fetching addresses...'
            for i, contrib in enumerate(page_contribs):
                postal_params.update({'addrname': contrib[1],
                                      'addrclientid': params['selectedid'],
                                      'displayaddress': True,
                                      'page': page,
                                      })

                req = session.get(base_uri, params=postal_params)
                soup = BeautifulSoup(req.text, parse_only=SoupStrainer('input'))

                city = soup.find(id='city')['value']
                province = soup.find(id='province')['value']
                postal = soup.find(id='postalcode')['value'].upper().replace(' ', '')

                page_contribs[i] = contrib[:4] + (city, province, postal)

        contribs.extend(page_contribs)

    return contribs
