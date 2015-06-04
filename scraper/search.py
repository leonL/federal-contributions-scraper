import csv
import re
import time
import urlparse

from bs4 import BeautifulSoup, SoupStrainer

FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/DetailedReport'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/DetailedReport'
PAGE_SIZE = 200


def search_contribs(session, queryid, federal=True, year=2012, get_address=True,
                        csvpath=None, q_reports=False):
    base_uri = FEDERAL_URI if federal else RIDING_URI
    params = {'act': 'C2',
              'returntype': 1,
              'option': 2,
              'part': '2A',
              'period': 1 if q_reports else 0,
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
        subcat = option.get_text()
        subcat = subcat.split(' /', 1)[0] if not(q_reports) else subcat

        print 'Search {} of {}:'.format(o + 1, len(options)), subcat

        # if a path is specified, look for existing records in a csv file
        try:
            with open(csvpath, 'rb') as csvfile:
                count = len([contrib for contrib in csv.reader(csvfile)
                             if contrib[0].decode('utf-8') == subcat])
        except IOError:
            count = 0

        # if a path is specified, open as a csv file for writing on-the-fly
        if csvpath:
            with open(csvpath, 'a+b', 1) as csvfile:
                print 'Opening CSV file for writing.'
                csvwriter = csv.writer(csvfile, lineterminator='\n')
                contribs.extend(subcat_search(subcat, session, base_uri, params, get_address,
                                              csvwriter, count))
        else:
            contribs.extend(subcat_search(subcat, session, base_uri, params, get_address))

    total_time = int(time.time() - start_time)
    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    print 'Total time: {}:{:02}:{:02}'.format(hours, minutes, seconds)
    print

    return contribs


def subcat_search(subcat, session, base_uri, params, get_address=True, csvwriter=None, count=0):
    contribs = []

    pages = page = first_page = count / PAGE_SIZE + 1
    if page > 1:
        print '{} results already saved; skipping to page {}.'.format(count, page)

    postal_params = params.copy()
    while page <= pages:
        print 'Reading page', ('{}...'.format(page) if page == first_page
                               else '{} of {}...'.format(page, pages))

        params['page'] = page

        tries = 1
        maxtries = 5
        while tries <= maxtries:
            req = session.get(base_uri, params=params)
            soup = BeautifulSoup(req.text)

            # find results table, or skip this search if no data
            table = soup.find('table', class_='DataTable')
            if table:
                break

            if soup.find(class_='nodatamessage'):
                print 'No results for this search.'
                break

            # no table and no "no data" message means search failed
            print 'Error: no table on results page. (try {} of {})'.format(tries, maxtries)
            tries += 1

        if not table:
            break

        if page == first_page:
            # check for more pages
            nextlink = soup.find('a', id='next200pagelink')
            if nextlink:
                m = re.search('totalpages=(\d+)', nextlink['href'])
                pages = int(m.group(1))
                print pages, 'page(s) found.'

        rows = table.find('tbody').find_all('tr', recursive=False)
        print '{} result(s) on this page.'.format(len(rows))

        if page == first_page:
            row_skip = count % PAGE_SIZE
            if len(rows) >= row_skip > 0:
                print 'Skipping {} saved result(s).'.format(row_skip)
                rows = rows[row_skip:]

        if rows:
            print 'Parsing{}{}...'.format(', fetching addresses' if get_address else '',
                                          ', saving to CSV' if csvwriter else '')

        for row in rows:
            cells = row.find_all('td')

            num = cells[0].get_text().strip()
            # remove weird decimals from id numbers
            for ch in ',.':
                if ch in num:
                    num = num.split(ch, 1)[0]

            name = cells[1].get_text().strip()
            date = cells[2].get_text().strip()
            amount = int(float(cells[5].get_text().replace(',', '')) * 100)

            if get_address:
                href = urlparse.parse_qs(urlparse.urlparse(cells[1].a['href']).query)
                postal_params.update({'addrname': name,
                                      'addrclientid': params['selectedid'],
                                      'displayaddress': True,
                                      'page': params['page'],
                                      'rowNbr': href['rowNbr'][0]
                                      })

                tries = 0
                while tries < 5:
                    req = session.get(base_uri, params=postal_params)
                    soup = BeautifulSoup(req.text, parse_only=SoupStrainer('input'))

                    try:
                        city = soup.find(id='city')['value']
                        province = soup.find(id='province')['value']
                        postal = (soup.find(id='postalcode')['value']
                                  .upper().replace(' ', ''))
                        break
                    except TypeError:
                        tries += 1
                        print 'Error getting address info (try {} of {})'.format(tries, maxtries)

            else:
                city = province = postal = ''

            contrib = subcat, num, name, date, amount, city, province, postal
            #print contrib

            if csvwriter is not None:
                csvwriter.writerow([field.encode('utf-8') if isinstance(field, unicode)
                                    else field for field in contrib])

            contribs.append(contrib)

        page += 1

    print
    return contribs
