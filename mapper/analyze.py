import csv
import os


def totals(contribs):
    # temporary hack - need a better way to separate federal from riding contribs
    fed_name = contribs[0][0]

    contribs_fed = []
    contribs_eda = []
    uniques = {}

    for c in contribs:
        if c[0] == fed_name:
            contribs_fed.append(c)
        else:
            contribs_eda.append(c)

        uid = (c[2], c[5], c[6], c[7])
        uniques.setdefault(uid, 0)
        uniques[uid] += int(c[4])

    sum_fed = sum(int(c[4]) for c in contribs_fed)
    sum_eda = sum(int(c[4]) for c in contribs_eda)
    sum_total = sum_fed + sum_eda

    return {'sum_total': sum_total,
            'sum_federal': sum_fed,
            'sum_riding': sum_eda,
            'count_total': len(contribs),
            'count_federal': len(contribs_fed),
            'count_riding': len(contribs_eda),
            'average_total': sum_total / len(contribs) if contribs else 0,
            'average_federal': sum_fed / len(contribs_fed) if contribs_fed else 0,
            'average_riding': sum_eda / len(contribs_eda) if contribs_eda else 0,
            'count_contributors': len(uniques),
            'average_contributor': sum_total / len(uniques),
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
