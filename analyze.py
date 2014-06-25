import csv


def sum_total(contribs):
    return sum(float(contrib[4]) for contrib in contribs)


def sum_city(contribs):
    cities = {}
    for contrib in contribs:
        amount = float(contrib[4])
        city = '{}, {}'.format(contrib[5].title(), contrib[6])

        cities.setdefault(city, 0)
        cities[city] += amount

    return cities


def sum_postal_groups(contribs):
    with open('./postal code groups.csv', 'rb') as csvfile:
        points = {line[0]: line[1:] for line in csv.reader(csvfile)}

    totals = {}
    for contrib in contribs:
        amount = float(contrib[4])
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

        totals.setdefault(code, 0)
        totals[code] += amount

    return [{'Label': code,
             'Lat': points[code][0],
             'Lng': points[code][1],
             'Amount': amount,
             } for code, amount in totals.iteritems()]
