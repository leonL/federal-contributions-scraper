import re
import time

from bs4 import BeautifulSoup


FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/DetailedReport'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/DetailedReport'


def scrape(session, queryid, federal=True, get_address=True, year=2012):
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
    #print req.text

    select = soup.find('select', id='selectedid')
    if not select:
        raise Exception('Error: no selectbox found on page. Try a new query ID.')

    # iterate through list of federal parties or riding associations
    options = select.find_all('option')
    for o, option in enumerate(options):
        params['selectedid'] = option['value']
        subcat = option.get_text().split(' /', 1)[0]

        print 'Search {0} of {1}:'.format(o + 1, len(options)), subcat.encode('utf8')
        subcat_contribs = subcat_search(session, base_uri, params, get_address)
        contribs.extend([(subcat,) + result for result in subcat_contribs])

    total_time = time.time() - start_time
    print 'Total time: {0} minute(s) {1} second(s)'.format(total_time / 60, total_time % 60)

    return contribs


def subcat_search(session, base_uri, params, get_address=True):
    contribs = []

    page = 1
    pages = 1
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
                print pages, 'page(s) found.'.format(pages),
        page += 1

        table = soup.find('table', class_='DataTable')
        if not table:
            if soup.find(class_='nodatamessage'):
                print 'No results for this search.'
                continue

            raise Exception('Error: no table on page. Try a new query ID.')

        rows = table.find('tbody').find_all('tr', recursive=False)
        print 'Reading {} result(s)...'.format(len(rows))

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


            name = cells[1].get_text().strip()

            city, province, postal = (get_postal_codes(session, base_uri, params, name)
                                      if get_address else ('', '', ''))

            contribs.append((int(num), # number
                             name, # full name
                             cells[2].get_text().strip(), # date
                             float(cells[5].get_text().replace(',', '')), # total amount
                             city,
                             province,
                             postal
                             ))

    return contribs


def get_postal_codes(session, base_uri, params, name):
    params.update({'addrname': name,
                   'addrclientid': params['selectedid'],
                   'displayaddress': True,
                   })
    req = session.get(base_uri, params=params)
    soup = BeautifulSoup(req.text)

    city = soup.find('input', id='city')['value']
    province = soup.find('input', id='province')['value']
    postal = soup.find('input', id='postalcode')['value'].upper().replace(' ', '')

    return city, province, postal
