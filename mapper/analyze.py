import csv
import os


def totals(contribs):
    # temporary hack - need a better way to separate federal from riding contribs
    fed_name = contribs[0][0]

    contribs_fed = [c for c in contribs if c[0] == fed_name]
    contribs_eda = [c for c in contribs if c[0] != fed_name]

    sum_fed = sum(int(contrib[4]) for contrib in contribs_fed)
    sum_eda = sum(int(contrib[4]) for contrib in contribs_eda)

    return {'sum_total': sum_fed + sum_eda,
            'sum_federal': sum_fed,
            'sum_riding': sum_eda,
            'count_total': len(contribs_fed) + len(contribs_eda),
            'count_federal': len(contribs_fed),
            'count_riding': len(contribs_eda),
            'unique_contributors': len(set((contrib[1], contrib[5], contrib[6], contrib[7])
                                           for contrib in contribs)),
            }


def cities(contribs):
    cities = {}
    for contrib in contribs:
        amount = int(contrib[4])
        city = '{}, {}'.format(contrib[5].title(), contrib[6])

        cities.setdefault(city, 0)
        cities[city] += amount

    return cities


def postal_groups(contribs):
    with open(os.path.join(os.path.dirname(__file__), 'postal code groups.csv'), 'rb') as csvfile:
        points = {line[0]: line[1:] for line in csv.reader(csvfile)}

    codes = {}
    for contrib in contribs:
        amount = int(contrib[4])
        code = contrib[7][:3]

        if not code:
            #print 'No postal code for this contribution:', contrib
            continue

        if code not in points:
            #print 'Unknown postal code:', contrib
            continue

        if amount > 1200:
            #print 'Contribution amount over $1200:', contrib
            pass

        codes.setdefault(code, {'Label': code,
                                'Lat': points[code][0],
                                'Lng': points[code][1],
                                'Amount': 0,
                                'Count': 0,
                                })

        codes[code]['Amount'] += amount
        codes[code]['Count'] += 1

    return codes.values()
