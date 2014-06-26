import csv
import re
import time

from bs4 import BeautifulSoup, SoupStrainer


FEDERAL_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/PP/DetailedReport'
RIDING_URI = 'http://www.elections.ca/WPAPPS/WPF/EN/EDA/DetailedReport'
PAGE_SIZE = 200


def scrape(session, queryid, federal=True, year=2012, get_address=True, csvpath=None):
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
        subcat = option.get_text().split(' /', 1)[0].encode('utf-8')

        print
        print 'Search {} of {}:'.format(o + 1, len(options)), subcat

        try:
            with open(csvpath, 'rb') as csvfile:
                count = len([contrib for contrib in csv.reader(csvfile) if contrib[0] == subcat])
        except IOError:
            count = 0

        if csvpath:
            with open(csvpath, 'a+b', 1) as csvfile:
                print 'Opening CSV file for writing.'
                csvwriter = csv.writer(csvfile, lineterminator='\n')
                contribs.extend(subcat_search(subcat, session, base_uri, params, get_address,
                                                csvwriter, count))
        else:
            contribs.extend(subcat_search(subcat, session, base_uri, params, get_address))

    total_time = time.time() - start_time
    print 'Total time: {} minute(s) {} second(s)'.format(int(total_time / 60), int(total_time % 60))

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
        req = session.get(base_uri, params=params)
        soup = BeautifulSoup(req.text)

        if page == first_page:
            # check for more pages
            nextlink = soup.find('a', id='next200pagelink')
            if nextlink:
                m = re.search('totalpages=(\d+)', nextlink['href'])
                pages = int(m.group(1))
                print pages, 'page(s) found.'

        # find results table, or skip this search if no data
        table = soup.find('table', class_='DataTable')
        if not table:
            if soup.find(class_='nodatamessage'):
                print 'No results for this search.'
                break

            # no table and no "no data" message means search failed
            raise Exception('Error: no table on page. Try a new query ID.')

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
            # skip empty id numbers
            if not num:
                continue
            # remove weird decimals from id numbers
            for ch in ',.':
                if ch in num:
                    num = num.split(ch, 1)[0]
            num = int(num)

            name = cells[1].get_text().strip().encode('utf-8')
            date = cells[2].get_text().strip().encode('utf-8')
            amount = int(float(cells[5].get_text().replace(',', '')) * 100)

            if get_address:
                postal_params.update({'addrname': name,
                                      'addrclientid': params['selectedid'],
                                      'displayaddress': True,
                                      'page': params['page'],
                                      })

                req = session.get(base_uri, params=postal_params)
                soup = BeautifulSoup(req.text, parse_only=SoupStrainer('input'))

                city = soup.find(id='city')['value'].encode('utf-8')
                province = soup.find(id='province')['value'].encode('utf-8')
                postal = (soup.find(id='postalcode')['value']
                          .upper().replace(' ', '').encode('utf-8'))
            else:
                city = province = postal = ''

            contrib = subcat, num, name, date, amount, city, province, postal
            #print contrib

            if csvwriter is not None:
                csvwriter.writerow(contrib)

            contribs.append(contrib)

        page += 1

    return contribs
