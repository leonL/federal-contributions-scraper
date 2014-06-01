import re
import time

import requests
from bs4 import BeautifulSoup


FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/DetailedReport'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/DetailedReport'


def scrape(queryid, sessionid, federal=True, get_address=True, year=2012):
    base_uri = FEDERAL_URI if federal else RIDING_URI
    cookies = {'ASP.NET_SessionId': sessionid}

    params = {'act': 'C2',
              'returntype': 1,
              'option': 2,
              'part': '2A',
              'period': 0,
              'fromperiod': year,
              'toperiod': year,
              'queryid': queryid
              }

    start_time = time.time()

    contribs = []

    # get list of federal parties or riding associations
    html = requests.get(base_uri, params=params, cookies=cookies)
    soup = BeautifulSoup(html.text)

    select = soup.find('select', id='selectedid')
    if not select:
        raise Exception('Error: no selectbox found on page. Try a new query ID.')

    # iterate through list of federal parties or riding associations
    options = select.find_all('option')
    for o, option in enumerate(options):
        params['selectedid'] = option['value']
        subcat = option.get_text().split(' /', 1)[0]

        print 'Search {0} of {1}:'.format(o + 1, len(options)), subcat
        subcat_contribs = subcat_search(base_uri, params, cookies, get_address)
        contribs.extend([(subcat,) + result for result in subcat_contribs])

    total_time = time.time() - start_time
    print 'Total time: {0} minute(s) {1} second(s)'.format(total_time / 60, total_time % 60)

    return contribs


def subcat_search(base_uri, params, cookies, get_address=True):
    contribs = []

    page = 1
    pages = 1
    while page <= pages:
        print 'Reading page', ('1...' if pages == 1 else '{0} of {1}...'.format(page, pages)),

        params['page'] = page
        search_html = requests.get(base_uri, params=params, cookies=cookies)
        print 'done.'

        #print search_html.text
        soup = BeautifulSoup(search_html.text)

        if page == 1:
            # check for multiple pages
            nextlink = soup.find('a', id='next200pagelink')
            if nextlink:
                m = re.search('totalpages=(\d+)', nextlink['href'])
                pages = int(m.group(1))
                print pages, 'page(s) found.'.format(pages)

        table = soup.find('table', class_='DataTable')
        if not table:
            if soup.find(class_='nodatamessage'):
                print 'No data for this search.'
                continue

            raise Exception('Error: no table on page. Try a new query ID.')

        rows = table.find('tbody').find_all('tr', recursive=False)
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

            city, province, postal = (get_postal_codes(base_uri, params, cookies, name)
                                      if get_address else ('', '', ''))

            contribs.append((int(num), # number
                             name, # full name
                             cells[2].get_text().strip(), # date
                             float(cells[5].get_text().replace(',', '')), # total amount
                             city,
                             province,
                             postal
                             ))

        page += 1

    return contribs


def get_postal_codes(base_uri, params, cookies, name):
    params.update({'addrname': name,
                   'addrclientid': params['selectedid'],
                   'displayaddress': True,
                   })
    postal_html = requests.get(base_uri, params=params, cookies=cookies)
    postal_soup = BeautifulSoup(postal_html.text)
    city = postal_soup.find('input', id='city')['value']
    province = postal_soup.find('input', id='province')['value']
    postal = postal_soup.find('input', id='postalcode')['value'].upper().replace(' ', '')

    return city, province, postal
