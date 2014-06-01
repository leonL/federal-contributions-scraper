import csv

codes = []
current_pcode, lats, longs = None, None, None

print 'Reading codes...'
# Data procured from http://geocoder.ca/onetimedownload/Canada.csv.gz
with open('Canadian Postal Codes Points.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    for pcode, plat, plong, city, province in reader:
        plat = float(plat)
        plong = float(plong)

        if pcode[:3] != current_pcode:
            if current_pcode is not None:
                codes.append((current_pcode, sum(lats) / len(lats), sum(longs) / len(longs)))
            current_pcode, lats, longs = pcode[:3], [plat], [plong]

        else:
            lats.append(plat)
            longs.append(plong)

print 'Writing codes...'
with open('postal code groups.csv', 'wb') as csvout:
    writer = csv.writer(csvout)
    for line in codes:
        writer.writerow(line)

print 'Done.'
